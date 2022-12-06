class Transaction:
    def __init__(self, amount, date, currency, wallet):
        self.amount = amount
        self.date = date
        self.currency = currency
        self.wallet = wallet

    def __str__(self):
        return f'(amount: {self.amount}, {self.currency}, date: {self.date})'

    def __repr__(self):
        return f'(amount: {self.amount}, {self.currency}, date: {self.date})'