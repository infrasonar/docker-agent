import os
from typing import Union

from .base import Base
from .utils import get_ts_from_time_str
from ..version import __version__ as version


class CheckSystem(Base):
    key = 'system'
    api_call = '/info'
    interval = int(os.getenv('CHECK_SYSTEM_INTERVAL', '300'))
    type_key = 'system'

    @staticmethod
    def on_item(itm: dict):
        return {
            'id': itm['ID'],
            'containers': itm['Containers'],
            'containersRunning': itm['ContainersRunning'],
            'containersPaused': itm['ContainersPaused'],
            'containersStopped': itm['ContainersStopped'],
            'images': itm['Images'],
            'driver': itm['Driver'],
            # SystemStatus is omitted if the field is not set
            # https://github.com/moby/moby/pull/40340
            'systemStatus': itm.get('SystemStatus'),
            'memoryLimit': itm['MemoryLimit'],
            'swapLimit': itm['SwapLimit'],
            # kernelMemory and kernelMemoryTCP do exist in newer versions
            'kernelMemory': itm.get('KernelMemory'),
            'kernelMemoryTCP': itm.get('KernelMemoryTCP'),
            'cpuCfsPeriod': itm['CpuCfsPeriod'],
            'cpuCfsQuota': itm['CpuCfsQuota'],
            'cpuShares': itm['CPUShares'],
            'cpuSet': itm['CPUSet'],
            'pidsLimit': itm['PidsLimit'],
            'ipv4Forwarding': itm['IPv4Forwarding'],
            'bridgeNfIptables': itm['BridgeNfIptables'],
            'bridgeNfIp6tables': itm['BridgeNfIp6tables'],
            'debug': itm['Debug'],
            'oomKillDisable': itm['OomKillDisable'],
            'nGoroutines': itm['NGoroutines'],
            'systemTime': get_ts_from_time_str(itm['SystemTime']),
            'loggingDriver': itm['LoggingDriver'],
            'nEventsListener': itm['NEventsListener'],
            'kernelVersion': itm['KernelVersion'],
            'operatingSystem': itm['OperatingSystem'],
            'osType': itm['OSType'],
            'architecture': itm['Architecture'],
            'indexServerAddress': itm['IndexServerAddress'],
            'nCpu': itm['NCPU'],
            'memTotal': itm['MemTotal'],
            'dockerRootDir': itm['DockerRootDir'],
            'httpProxy': itm['HttpProxy'],
            'httpsProxy': itm['HttpsProxy'],
            'noProxy': itm['NoProxy'],
            'name': itm['Name'],
            'experimentalBuild': itm['ExperimentalBuild'],
            'serverVersion': itm['ServerVersion'],
            'clusterStore': itm.get('ClusterStore'),
            'clusterAdvertise': itm.get('ClusterAdvertise'),
            'defaultRuntime': itm['DefaultRuntime'],
            'liveRestoreEnabled': itm['LiveRestoreEnabled'],
            'isolation': itm['Isolation'],
            'initBinary': itm['InitBinary'],
            'warnings': itm.get('Warnings') or [],
            'infrasonarAgentVersion': version,
        }

    @classmethod
    def iterate_results(cls, data: Union[dict, list]):
        assert isinstance(data, dict)
        state = {cls.type_key: [cls.on_item(data)]}
        return state
