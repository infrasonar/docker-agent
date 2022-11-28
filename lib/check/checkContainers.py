import os
import asyncio
import logging

from .base import Base
from .utils import format_name


class CheckContainers(Base):
    # Query parameters
    # all (boolean; false):
    # Return all containers. By default, only running containers are shown.
    # size (boolean; false):
    # Return the size of container as fields SizeRw and SizeRootFs.
    key = 'containers'
    api_call = '/containers/json?all=true'  # &size=true'
    interval = int(os.getenv('CHECK_CONTAINERS_INTERVAL', '300'))

    semaphore = asyncio.Semaphore(value=10)  # number requests in parallel

    @staticmethod
    def calculate_memory_percentage(stats):
        memory_stats = stats['memory_stats']
        stats = memory_stats['stats']

        # On Linux, the Docker CLI reports memory usage by subtracting cache
        # usage from the total memory usage. The API does not perform such a
        # calculation but rather provides the total memory usage and the amount
        # from the cache so that clients can use the data as needed. The cache
        # usage is defined as the value of total_inactive_file field in the
        # memory.stat file on cgroup v1 hosts.
        # On Docker 19.03 and older, the cache usage was defined as the value
        # of cache field. On cgroup v2 hosts, the cache usage is defined as the
        # value of inactive_file field.
        # https://docs.docker.com/engine/reference/commandline/stats/
        used_memory = memory_stats['usage'] - stats.get(
            'cache',
            stats.get(
                'inactive_file',
                stats.get('total_inactive_file', 0)))
        return (used_memory / memory_stats['limit']) * 100.0

    @staticmethod
    def calculate_cpu_percentage(stats):
        cpu_stats = stats['cpu_stats']
        cpu_usage = cpu_stats['cpu_usage']
        precpu_stats = stats['precpu_stats']
        precpu_usage = precpu_stats['cpu_usage']

        cpu_delta = cpu_usage['total_usage'] - precpu_usage['total_usage']
        system_cpu_delta = cpu_stats['system_cpu_usage'] - \
            precpu_stats['system_cpu_usage']

        # If either precpu_stats.online_cpus or cpu_stats.online_cpus is nil
        # then for compatibility with older daemons the length of the
        # corresponding cpu_usage.percpu_usage array should be used.
        # https://docs.docker.com/engine/api/v1.41/#operation/ContainerExport
        number_cpus = cpu_stats.get(
            'online_cpus',
            precpu_stats.get(
                'online_cpus',
                len(cpu_usage.get('percpu_usage', []))))

        return (cpu_delta / system_cpu_delta) * number_cpus * 100.0

    @classmethod
    async def task(cls, container, stats):
        container_id = container['Id']
        query = f'/containers/{container_id}/stats?stream=false'
        async with cls.semaphore:
            logging.debug(f'get stats: {query}')
            s = await cls.docker_api_call(query)
            stat[container_id] = s

    @classmethod
    async def get_data(cls, query: str):
        # 1. get container ids
        logging.debug('get containers')
        containers = await cls.docker_api_call(query)
        state_data = cls.iterate_containers(containers)
        stats = {}
        tasks = []

        for container in containers:
            # 2. get stats per container
            tasks.append(cls.task(container, stats))

        await asyncio.gather(*tasks)
        cls.apply_stats(state_data['containers'], stats)

        return stats

    @staticmethod
    def format_port(port: dict):
        return (
            f"{port['IP']}:{port['PrivatePort']}"
            f"->{port['PublicPort']}/{port['Type']}"
        ) if 'IP' in port else (
            f"{port['PrivatePort']}/{port['Type']}"
        )

    @classmethod
    def on_item_containers(cls, itm: dict) -> dict:
        resp_data = {
            'id': itm['Id'],
            'name': format_name(itm['Names']),
            'names': itm['Names'],  # list
            'image': itm['Image'],
            'imageId': itm['ImageID'],
            'created': int(itm['Created']),
            'state': itm['State'],
            'status': itm['Status'],
            'ports': [cls.format_port(port) for port in itm['Ports']]
        }

        network_mode = itm.get('HostConfig', {}).get('NetworkMode', None)
        if network_mode is not None:
            resp_data['networkMode'] = network_mode
        return resp_data

    @classmethod
    def on_item_networks(cls, itm: dict) -> list:
        network_data = []
        container_name = format_name(itm['Names'])
        for k, v in itm.get('NetworkSettings', {}).get('Networks', {}).items():
            name = f'{container_name}_{k}'
            network_data.append({
                'name': name,
                'networkId': v['NetworkID'],
                'endpointId': v['EndpointID'],
                'gateway': v['Gateway'],
                'ipAddress': v['IPAddress'],
                'ipPrefixLen': v['IPPrefixLen'],
                'ipv6Gateway': v['IPv6Gateway'],
                'globalIpv6Address': v['GlobalIPv6Address'],
                'macAddress': v['MacAddress'],
                'driverOpts': v.get('DriverOpts'),
                'aliases': v.get('Aliases'),
                'links': v.get('Links'),
            })
        return network_data

    @classmethod
    def iterate_containers(cls, data: list):
        out = {'containers': [], 'networks': []}
        for i in data:
            out['containers'].append(cls.on_item_containers(i))
            out['networks'].extend(cls.on_item_networks(i))
        return out

    @classmethod
    def apply_stats(cls, containers: list, stats: dict):
        for container in containers:
            istats = stats.get(container['id'])
            if istats is None:
                continue
            container['memory'] = cls.calculate_memory_percentage(istats)
            container['cpu'] = cls.calculate_cpu_percentage(istats)

    @classmethod
    def iterate_results(cls, state_data: dict):
        """For the containers check we already have state data at this point.
        """
        return state_data
