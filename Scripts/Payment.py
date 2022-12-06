import json
import aiohttp
import config


domain = config.domain_pay
hermes_api_key = config.api_pay


async def client_payment_types():
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
    }

    api_url = f"https://{domain}/api_v1/client_payment_types/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url) as resp:
            return dict(json.loads(await resp.text()))


async def create_order(payment_type, rub_sum):
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
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
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
    }

    params = {
        'id': ids,
    }

    api_url = f"https://{domain}/api_v1/ballance/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url, data=params) as resp:
            return json.loads(await resp.text())


async def status_requets(ids):
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
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
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
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
    headers = {
        'Authorization': f'Api-Key {hermes_api_key}'
    }

    api_url = f"https://{domain}/api_v1/ballance/"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        async with session.post(api_url) as resp:
            body = json.loads(await resp.text())
            print(body)
            return body
