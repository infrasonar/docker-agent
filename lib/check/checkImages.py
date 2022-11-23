import os

from .base import Base


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
            # https://github.com/moby/moby/issues/29203 repoDigests can be null
            'repoDigests': itm['RepoDigests'],
            'repoTags': itm['RepoTags'],
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
