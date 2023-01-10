class Config:
    def __init__(self, api_bot, api_pay, api_coinbase_pay, api_coinbase_secret, ltc_id, btc_id, eth_id,
                 usdt_wallet, type_cript, errors_token, errors_group_id):
        self.api_bot = api_bot
        self.api_pay = api_pay
        self.API_COINBASE_PAY = api_coinbase_pay
        self.API_COINBASE_SECRET = api_coinbase_secret
        self.LTC_ID = ltc_id
        self.BTC_ID = btc_id
        self.ETH_ID = eth_id
        self.USDT_WALLET = usdt_wallet
        self.TYPE_CRIPT = type_cript
        self.ERRORS_TOKEN = errors_token
        self.errors_group_id = errors_group_id


name_bot = "space_gift_bot"

domain_pay = "orionbtc.xyz"

NUMBER_PAY = 0
ADMINS = [855151774]

SUB_GROUP = -1001878641715

DEBUG = True

if DEBUG:
    PATH = '/Users/v_sopin/Documents/GitHub/Space_Gift'

    HOST = "127.0.0.1"
    USERS = "root"
    PASSWORD = "vlad1550vlad1550"
    DB_NAME = "yougiftdb"
else:
    PATH = '/opt/Space_Gift'

    HOST = "127.0.0.1"
    USERS = "root"
    PASSWORD = "6CHWb6QmNUy9bLuX"
    DB_NAME = "yougiftdb"

COMMISSION = 0.2

