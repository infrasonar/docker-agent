import os
from pylibagent.agent import Agent
from lib.check.checkContainers import CheckContainers
from lib.check.checkImages import CheckImages
from lib.check.checkSystem import CheckSystem
from lib.version import __version__ as version


if __name__ == '__main__':
    # Update ASSET_ID and set a default for the docker agent
    ASSET_ID = os.getenv('ASSET_ID', '/data/.asset.json')
    os.environ['ASSET_ID'] = ASSET_ID

    checks = [CheckContainers, CheckImages, CheckSystem]
    Agent('docker', version).start(checks, asset_kind='Docker')
