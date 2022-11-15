import asyncio
import re
import aiohttp
from pylibagent.check import CheckBase


URL_RE = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|'
    r'[A-Z0-9-]{2,}\.?)|'  # domain
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Base(CheckBase):

    key = ''
    interval = 300

    api_call = ''
    api_version = 'v1.41'
    type_key = None

    @classmethod
    async def run(cls):
        if cls.interval == 0:
            raise Exception(f'{cls.key} is disabled')

        data = await asyncio.wait_for(
            cls.get_data(cls.api_call),
            timeout=60.0  # 60 seconds
        )
        state_data = cls.iterate_results(data)
        return state_data

    @classmethod
    async def get_data(cls, query: str):
        return await cls.docker_api_call(query)

    @classmethod
    async def docker_api_call(cls, query: str):
        url = f'http://{cls.api_version}' + query
        async with aiohttp.ClientSession(connector=cls.get_conn()) as session:
            async with session.get(url) as resp_data:
                return await resp_data.json()

    @classmethod
    def get_conn(cls):
        address = '/var/run/docker.sock'

        if URL_RE.match(address):
            raise NotImplementedError('TCP connector is not implemented')

        return aiohttp.UnixConnector(path=address)

    @staticmethod
    def on_item(itm: dict) -> dict:
        assert 'name' in itm
        return itm

    @classmethod
    def on_items(cls, itms: list) -> list:
        return [cls.on_item(i) for i in itms]

    @classmethod
    def iterate_results(cls, data: list):
        itms = cls.on_items(data)
        return {cls.type_key: itms}
