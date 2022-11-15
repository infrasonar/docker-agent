import os
import asyncio
import logging

from .base import Base
from .utils import format_name


class CheckStats(Base):
    key = 'stats'
    api_call = '/containers/json'  # To get container ids
    interval = int(os.getenv('CHECK_STATS_INTERVAL', '300'))

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
            s['name'] = format_name(container['Names'])
            stats.append(s)

    @classmethod
    async def get_data(cls, query: str):
        # 1. get container ids
        logging.debug('get containers')
        containers = await cls.docker_api_call(query)
        stats = []
        tasks = []

        for container in containers:
            # 2. get stats per container
            tasks.append(cls.task(container, stats))

        await asyncio.gather(*tasks)
        return stats

    @classmethod
    def on_item_memory(cls, itm: dict):
        resp_data = {
            'name': itm['name'],
            'percentUsed': cls.calculate_memory_percentage(itm),
        }
        return resp_data

    @classmethod
    def on_item_cpu(cls, itm: dict):
        resp_data = {
            'name': itm['name'],
            'percentUsed': cls.calculate_cpu_percentage(itm),
        }
        return resp_data

    @classmethod
    def iterate_results(cls, data: list):
        out = {
            'memory': [],
            'cpu': [],
        }
        for i in data:
            out['memory'].append(cls.on_item_memory(i))
            out['cpu'].append(cls.on_item_cpu(i))
        return out
