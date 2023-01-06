import datetime


class User:
    def __init__(self, name, user_id, date: datetime, referrer_id=None):
        self.name = name
        self.date = date
        self.user_id = user_id
        self.referrer_id = referrer_id
        self.isPay = False


class UserDB:
    def __init__(self, name, link, user_id, money, depozit, planet, step, status, count_ref, active, jump, activate_date):
        self.name = name
        self.link = link
        self.user_id = user_id
        self.money = money
        self.desozit = depozit
        self.planet = planet
        self.step = step
        self.status = status
        self.count_ref = count_ref
        self.active = active
        self.jump = jump
        self.activate_date = activate_date
