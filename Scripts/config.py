class Config:
    def __init__(self, api_bot, api_pay, api_coinbase_pay, api_coinbase_secret, ltc_id, btc_id, eth_id, usdt_wallet):
        self.api_bot = api_bot
        self.api_pay = api_pay
        self.API_COINBASE_PAY = api_coinbase_pay
        self.API_COINBASE_SECRET = api_coinbase_secret
        self.LTC_ID = ltc_id
        self.BTC_ID = btc_id
        self.ETH_ID = eth_id
        self.USDT_WALLET = usdt_wallet


name_bot = "yougift_donation_bot"

domain_pay = "orionbtc.xyz"

NUMBER_PAY = 0
ADMINS = [855151774]

TYPE_CRIPT = "LTC"

PATH = "/opt/Space_Gift"

HOST = "localhost"
USERS = "root"
PASSWORD = "6CHWb6QmNUy9bLuX"
DB_NAME = "yougiftdb"

COMMISSION = 0.3

