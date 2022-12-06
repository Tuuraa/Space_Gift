import sqlite3
from datetime import datetime


class ManagerUsersDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("C:\\Users\\turap\\OneDrive\\Рабочий стол\\DonationBot\\Data\\YouGiftDB.db")
        self.cursor = self.connection.cursor()

    def exists_user(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT `user_id` FROM `users`").fetchall()

    def add_user(self, name, user_id, date, date_now, user_name, last_withd, referrer_id=None):
        with self.connection:
            if referrer_id is not None:
                return self.cursor.execute("INSERT INTO `users` (`name`, `user_id`, `date`, 'referrer_id', 'date_now', `link_name`, last_withd) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                           (name, user_id, date, referrer_id, date_now, user_name, last_withd,))
            else:
                return self.cursor.execute("INSERT INTO `users` (`name`, `user_id`, `date`, 'date_now', link_name, last_withd) VALUES (?, ?, ?, ?, ?, ?)",
                                           (name, user_id, date, date_now, user_name, last_withd, ))

    def count_referrer(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE referrer_id = ?", (user_id,)).fetchall()
            return len(result)

    def get_date(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `date` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return str(result)[3:-4]

    def get_date_now(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `date_now` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_money(self, user_id):
        with self.connection:
            return str(self.cursor.execute("SELECT `money` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0])[1:-2]

    def add_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET money = money + ? WHERE user_id = ?", (money, user_id,)).fetchall()

    def add_depozit(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET depozit = depozit + ? WHERE user_id = ?", (money, user_id,)).fetchall()

    def add_money_with_user_name(self, name, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET money = money + ? WHERE `name` = ?", (money, name,)).fetchall()

    def remove_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET money = money - ? WHERE user_id = ?", (money, user_id,)).fetchall()

    def add_procent(self, user_id):
        with self.connection:
            money = round(float(self.get_money(user_id)) * 1.005)
            return self.cursor.execute("UPDATE `users` SET money = ? WHERE user_id = ?", (money, user_id,)).fetchall()

    def set_new_date(self, user_id, date: datetime):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET date_now =  ? WHERE user_id = ?", (date, user_id,)).fetchall()

    def get_referrer_of_user(self, user_id):
        with self.connection:
            return str(self.cursor.execute("SELECT `referrer_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0])[1:-2]

    def set_gift_id(self, from_id, to_id):
        with self.connection:
            self.cursor.execute("INSERT INTO `helper` (`from_id`, `to_id`) VALUES (?,?)", (from_id, to_id))

    def get_gift_id(self, to_id):
        with self.connection:
            return self.cursor.execute("SELECT `from_id` FROM `helper` WHERE `to_id` = ?", (to_id,)).fetchall()

    def delete_gift(self, from_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `helper` WHERE `from_id` = ?", (from_id,))

    def get_full_users_name(self):
        with self.connection:
            return self.cursor.execute("SELECT `name` FROM `users`").fetchall()

    def change_status(self, user_id, value):
        with self.connection:
            self.cursor.execute("UPDATE `users` SET `status` = ? WHERE `user_id` = ?", (value, user_id, ))

    def get_id(self, name):
        with self.connection:
            return self.cursor.execute("SELECT `user_id` FROM `users` WHERE `name` = ?", (name, )).fetchall()[0][0]

    def get_user_name(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `link_name` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def get_full_data(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()

    def get_size_gift(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `gift_value` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_deposit(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `depozit` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def get_now_depozit(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `now_depozit` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def set_now_depozit(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `now_depozit` =  ? WHERE user_id = ?", (money, user_id,))

    def update_step(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `step` = `step` + ? WHERE user_id = ?", (1, user_id,))

    def reset_step(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `step` = 1 WHERE user_id = ?", (user_id,))

    def update_planet(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `planet` = `planet` + ? WHERE user_id = ?", (1, user_id,))

    def add_gift_value(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `gift_value` = `gift_value` + 1 WHERE `user_id` = ?" ,
                                       (user_id,))

    def get_status(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `status` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0]

    def get_first_dep(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `first_dep` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_planet(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `planet` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0]

    def get_step(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `step` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_name(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `name` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def change_first_dep(self, user_id, value):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `first_dep` = ? WHERE `user_id` = ?", (value, user_id,))

    def get_users_on_planet(self, planet):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `planet` = ?", (planet, )).fetchall()

    def get_empty_block_users(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `block_user_id` = 0 AND `user_id` != ?", (user_id, )).fetchall()

    def new_block_user(self, user_id, block_id):
        with self.connection:
            self.cursor.execute("UPDATE `users` SET `block_user_id` = ? WHERE `user_id` = ?", (block_id, user_id))

    def update_count_ref(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `count_ref` = `count_ref` + 1 WHERE `user_id` = ?", (user_id, ))

    def update_active(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `active` =  1 WHERE `user_id` = ?",
                                       (user_id,))

    def reset_active(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `active` =  0 WHERE `user_id` = ?",
                                       (user_id,))

    def add_gift_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `gift_money` =  `gift_money` + ? WHERE `user_id` = ?",
                                       (money, user_id,))

    def remove_gift_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `gift_money` =  `gift_money` - ? WHERE `user_id` = ?",
                                       (money, user_id,))

    def get_gift_money(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `gift_money` FROM `users` WHERE `user_id` = ?",
                                       (user_id,)).fetchall()[0][0]

    def add_amount_gift_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `amount_gift_money` =  `amount_gift_money` + ? WHERE `user_id` = ?",
                                       (money, user_id,))

    def get_ref_money(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `ref_money` FROM `users` WHERE `user_id` = ?",
                                       (user_id,)).fetchall()[0][0]

    def add_ref_money(self, user_id, money):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `ref_money` =  `ref_money` + ? WHERE `user_id` = ?",
                                       (money, user_id,))

    def get_amount_gift_money(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `amount_gift_money` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def get_active(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `active` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def get_users_of_block(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `link_name` FROM `users` WHERE `block_user_id` = ?", (user_id, )).fetchall()

    def get_count_ref(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `count_ref` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def delete_acc(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `users` WHERE `user_id` = ?", (user_id, ))

    def have_jump(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `jump` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def reset_jump(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `jump` = 0 WHERE `user_id` = ?", (user_id,))

    def get_ref_users(self, ref_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `referrer_id` = ?", (ref_id,))

    def ref_count(self, ref_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM `users` WHERE `referrer_id` = ?", (ref_id,))

    def get_last_withd(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `last_withd` FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()[0][0]

    def set_last_withd(self, user_id, date):
        with self.connection:
            self.cursor.execute("UPDATE `users` SET `last_withd` = ? WHERE `user_id` = ?", (date, user_id, ))


class ManagerPayDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("C:\\Users\\turap\\OneDrive\\Рабочий стол\\DonationBot\\Data\\YouGiftDB.db")
        self.cursor = self.connection.cursor()

    def create_pay(self, pay_id, pay_type, pay_amount, date, user_id, canc_id, status):
        with self.connection:
            res = self.cursor.execute("INSERT INTO `pay` (`pay_id`, `pay_amount`, `date`,  'pay_type', `user_id`, `cancel_id`, `status`) "
                                      "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                       (pay_id, pay_amount, date, pay_type, user_id, canc_id, status))
            return res

    def get_data(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `pay` WHERE `user_id` = ?", (user_id,)).fetchall()

    def get_data_canc(self, canc_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `pay` WHERE `cancel_id` = ?", (canc_id,)).fetchall()

    def cancel_request(self, canc_id, type):
        with self.connection:
            if type == "CREDIT":
                self.cursor.execute("DELETE FROM `pay` WHERE `cancel_id` = ?", (canc_id,))
            else:
                self.cursor.execute("DELETE FROM `crypt_pay` WHERE `cancel_id` = ?", (canc_id,))

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT `user_id` FROM `pay`").fetchall()

    def create_crypt_pay(self, pay_type, pay_amount, date, user_id, canc_id, status):
        with self.connection:
            return self.cursor.execute("INSERT INTO `crypt_pay` (`amount`, `date`,  'pay_type', `user_id`, `cancel_id`, `status`) "
                                       "VALUES (?, ?, ?, ?, ?, ?)",
                                       (pay_amount, date, pay_type, user_id, canc_id, status))

    def get_status(self, canc_id):
        with self.connection:
            return self.cursor.execute("SELECT `status` FROM `crypt_pay` WHERE `cancel_id` = ?", (canc_id, )).fetchall()[0][0]

    def get_status_credit(self, canc_id):
        with self.connection:
            return self.cursor.execute("SELECT `status` FROM `pay` WHERE `cancel_id` = ?", (canc_id, )).fetchall()[0][0]

    def get_data_crypt(self, canc_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `crypt_pay` WHERE `cancel_id` = ?", (canc_id,)).fetchall()

    def get_all_data_crypt(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `crypt_pay`").fetchall()

    def change_status(self, status, user_id, type):
        with self.connection:
            if type == "CREDIT":
                return self.cursor.execute("UPDATE `pay` SET status = ? WHERE user_id = ?",
                                           (status, user_id,)).fetchall()
            else:
                return self.cursor.execute("UPDATE `crypt_pay` SET status = ? WHERE user_id = ?",
                                           (status, user_id,)).fetchall()

    def change_status_for_cancel(self, status, cancel, type):
        with self.connection:
            if type == "CREDIT":
                return self.cursor.execute("UPDATE `pay` SET status = ? WHERE cancel_id = ?",
                                           (status, cancel,)).fetchall()
            else:
                return self.cursor.execute("UPDATE `crypt_pay` SET status = ? WHERE cancel_id = ?",
                                           (status, cancel,)).fetchall()

    def get_count_crypt(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM `crypt_pay`").fetchall()[0][0]

    def get_count_credit(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM `pay`").fetchall()[0][0]


class ManagerWithDrawDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("C:\\Users\\turap\\OneDrive\\Рабочий стол\\DonationBot\\Data\\YouGiftDB.db")
        self.cursor = self.connection.cursor()

    def create_request(self, card, data, type, amount, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `withdraw` (card, data, type, amount, user_id) VALUES (?, ?, ?, ?, ?)", (card, data, type, amount, user_id))

    def delete_request(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `withdraw` WHERE `user_id` = ?", (user_id,))

    def get_all_request(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM `withdraw`")

    def get_other_request(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM `withdraw` WHERE `user_id` = ?", (user_id,))


class ManagerClonesDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("C:\\Users\\turap\\OneDrive\\Рабочий стол\\DonationBot\\Data\\YouGiftDB.db")
        self.cursor = self.connection.cursor()

    def create_clone(self):
        with self.connection:
            self.cursor.execute("INSERT INTO `clones` (`active`) VALUES (1)")

    def get_count_clones(self):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM `clones`").fetchall()[0][0]

    def get_all(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `clones`").fetchall()

    def change_active(self, id):
        with self.connection:
            return self.cursor.execute("UPDATE `clones` SET `active` = 0 WHERE `id` = ?", (id, ))

    def reset_clone(self, id):
        with self.connection:
            self.cursor.execute("DELETE FROM `clones` WHERE `id` = ?", (id, ))