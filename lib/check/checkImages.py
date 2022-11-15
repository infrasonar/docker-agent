import os

from .base import Base
from .utils import format_list


class CheckImages(Base):
    key = 'images'
    api_call = '/images/json?all=false'
    interval = int(os.getenv('CHECK_IMAGES_INTERVAL', '300'))
    type_key = 'images'

    @staticmethod
    def on_item(itm: dict):
        resp_data = {
            'created': itm['Created'],
            'name': itm['Id'],
            'parentId': itm['ParentId'],
            'repoDigests': format_list(itm['RepoDigests']),
            'repoTags': format_list(itm['RepoTags']),
            'size': itm['Size'],
            'virtualSize': itm['VirtualSize'],
        }

        containers = itm['Containers']
        shared_size = itm['SharedSize']

        # check issue https://github.com/moby/moby/issues/43244
        if containers != -1:
            resp_data['containers'] = containers
        if shared_size != -1:
            resp_data['sharedSize'] = shared_size

        return resp_data
