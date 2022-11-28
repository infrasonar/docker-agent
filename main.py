import os
from pylibagent.agent import Agent
from lib.check.checkContainers import CheckContainers
from lib.check.checkImages import CheckImages
from lib.check.checkSystem import CheckSystem
from lib.version import __version__ as version


if __name__ == '__main__':
    # Update ASSET_ID_FILE and set a default for the docker agent
    asset_id_file = os.getenv('ASSET_ID_FILE', '/data/.asset.json')
    os.environ['ASSET_ID_FILE'] = asset_id_file

    checks = [CheckContainers, CheckImages, CheckSystem]
    Agent('docker', version).start(checks, asset_kind='Docker')
