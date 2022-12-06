from coinbase.wallet.client import Client
from coinbase.wallet.error import CoinbaseError
import requests
import config
import json
import datetime
from Transction import Transaction


async def send_eth(to_wallet, eth_sum, client: Client):
    primary_accaunt = client.get_primary_account()
    res = client.send_money("", to=to_wallet, amount=eth_sum, currency='ETH', to_financial_institution=True, financial_institution_website='https://t.me//orionbtc_bot')
    return res['to']['address_url']


async def send_ltc(to_wallet, ltc_sum):
    client = Client("", "")
    res = client.send_money("", to=to_wallet, amount=ltc_sum, currency='LTC', to_financial_institution=True, financial_institution_website='https://t.me//orionbtc_bot')
    return res['to']['address_url']


async def get_kurs(type):
    req = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={type}RUB")
    response = json.loads(req.text)
    return float(response.get("price"))


async def get_ballance_btc():
    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)
    resp = client.get_account(config.BTC_ID)
    return resp


async def get_ballance_eth():
    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)
    resp = client.get_account(config.ETH_ID)
    return resp


async def get_ballance_ltc():
    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)
    resp = client.get_account(config.LTC_ID)
    return resp


async def get_transaction():
    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)
    print(client.get_transactions(config.ETH_ID))


async def get_address(currency):

    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)
    account_id = None

    if currency == 'BTC':
        account_id = config.BTC_ID
    elif currency == 'ETH':
        account_id = config.ETH_ID
    elif currency == 'LTC':
        account_id = config.LTC_ID

    addresses = client.get_addresses(account_id)
    return addresses[0]['address']


def parse_transaction(transactions, currency, wallet):
    result = []
    for transaction in transactions:
        if transaction['type'] != 'send' or transaction['status'] != 'completed' or float(
                transaction['amount']['amount']) < 0:
            continue

        amount = float(transaction['amount']['amount'])
        date = transaction['updated_at']
        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

        result.append(Transaction(amount, date, currency, wallet))
    return result


async def get_completed_transactions():
    client = Client(config.API_COINBASE_PAY, config.API_COINBASE_SECRET)

    res_btc = json.loads(str(client.get_transactions(config.BTC_ID)))
    res_eth = json.loads(str(client.get_transactions(config.ETH_ID)))
    res_ltc = json.loads(str(client.get_transactions(config.LTC_ID)))

    wallet_btc = await get_address('BTC')
    wallet_eth = await get_address('ETH')
    wallet_ltc = await get_address("LTC")

    data_btc = res_btc['data']
    data_eth = res_eth['data']
    data_ltc = res_ltc['data']

    result = parse_transaction(data_btc, 'BTC', wallet_btc)
    result.extend(parse_transaction(data_eth, 'ETH', wallet_eth))
    result.extend(parse_transaction(data_ltc, 'LTC', wallet_ltc))

    #print(result)
    return result