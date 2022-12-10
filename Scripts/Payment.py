import json
import aiohttp
import config
from db import ConfigDBManager

domain = config.domain_pay


async def client_payment_types():
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    api_url = f"https://{domain}/api_v1/client_payment_types/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url) as resp:
            return dict(json.loads(await resp.text()))


async def create_order(payment_type, rub_sum):
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    params = {
        'payment_type': payment_type,
        'rub_sum': rub_sum,
        'cryptocurrency': config.TYPE_CRIPT,
        'cryptocurrency_wallet': "MSmBXKzawd7tEr6LjQEvWpZixBKuGCB2CB",
    }

    api_url = f"https://{domain}/api_v1/create_order/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url, data=params) as resp:
            body = json.loads(await resp.text())
            return body


async def get_order(ids):
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    params = {
        'id': ids,
    }

    api_url = f"https://{domain}/api_v1/ballance/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url, data=params) as resp:
            return json.loads(await resp.text())


async def status_requets(ids):
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    params = {
        'id': ids,
    }

    api_url = f"https://{domain}/api_v1/order/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url, data=params) as resp:
            body = json.loads(await resp.text())
            #print(body)
            return body['orders'][0][str(ids)]['status']


async def order_is_not_None(ids):
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    params = {
        'id': ids,
    }

    api_url = f"https://{domain}/api_v1/order/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url, data=params) as resp:
            body = json.loads(await resp.text())

            if body is not None:
                return True
            else:
                return False


async def ballance():
    config = ConfigDBManager.get()
    headers = {
        'Authorization': f'Api-Key {config.api_pay}'
    }

    api_url = f"https://{domain}/api_v1/ballance/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url) as resp:
            body = json.loads(await resp.text())
            print(body)
            return body
