import aiomysql
from pymysql import connect
from datetime import datetime
from config import Config
from config import HOST, USERS, DB_NAME, PASSWORD


async def async_connect_to_mysql(loop):
    connection = await aiomysql.connect(
        host=HOST,
        user=USERS,
        db=DB_NAME,
        password=PASSWORD,
        loop=loop
    )
    cursor = await connection.cursor()

    return connection, cursor


def create_sync_con():
    con = connect(host=HOST, user=USERS, db=DB_NAME, password=PASSWORD)
    cur = con.cursor()

    return con, cur


def get_tokens(title):
    connection, cursor = create_sync_con()
    cursor.execute("select `title` from `tokens` where `api` = %s ", (title))
    result = cursor.fetchall()[0][0]
    return result


class ConfigDBManager:
    @staticmethod
    def get():
        connection, cursor = create_sync_con()
        data = ['bot_api', 'api_pay', 'api_coinbase_pay', 'api_coinbase_secret', 'ltc_id', 'btc_id', 'eth_id', 'usdt_wallet', 'type_crypt']
        result = []
        for item in data:
            cursor.execute("select `title` from `tokens` where `api` = %s", (item, ))
            result.append(cursor.fetchone()[0])

        return Config(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])


class ManagerUsersDataBase:

    async def exists_user(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)

        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchall()
            return bool(len(result))

    async def get_users(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `user_id` FROM `users`")
            result = await cursor.fetchall()
            return result

    async def add_user(self, loop, name, user_id, date, date_now, user_name, last_withd, referrer_id=None):
        connection, cursor = await async_connect_to_mysql(loop)

        async with connection.cursor() as cursor:
            if referrer_id is not None:
                await cursor.execute("INSERT INTO `users` (`name`, `user_id`, `date`, `referrer_id`, `date_now`, "
                                           "`link_name`, last_withd) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                           (name, user_id, date, referrer_id, date_now, user_name, last_withd,))
                await connection.commit()
            else:
                await cursor.execute("INSERT INTO `users` (`name`, `user_id`, `date`, `date_now`, `link_name`, "
                                           "`last_withd`) VALUES (%s, %s, %s, %s, %s, %s)",
                                           (name, user_id, date, date_now, user_name, last_withd))
                await connection.commit()

    async def count_referrer(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `users` WHERE referrer_id = %s", (user_id,))
            result = await cursor.fetchall()
            return len(result)

    async def get_date(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `date` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchone())[0]
            return result

    async def get_date_now(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `date_now` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_money(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `money` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = str((await cursor.fetchall())[0][0])
            return result

    async def add_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET money = money + %s WHERE user_id = %s", (money, user_id,))
            await connection.commit()

    async def add_depozit(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET depozit = depozit + %s WHERE user_id = %s", (money, user_id,))
            await connection.commit()

    async def add_money_with_user_name(self, name, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET money = money + %s WHERE `name` = %s", (money, name,))
            await connection.commit()

    async def remove_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET money = money - %s WHERE user_id = %s", (money, user_id,))
            await connection.commit()

    async def add_procent(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            money = round(float(await self.get_money(user_id, loop)) * 1.005)
            await cursor.execute("UPDATE `users` SET money = %s WHERE user_id = %s", (money, user_id,))
            await connection.commit()

    async def set_new_date(self, user_id, date: datetime, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET date_now =  %s WHERE user_id = %s", (date, user_id,))
            await connection.commit()

    async def get_referrer_of_user(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `referrer_id` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = str((await cursor.fetchall())[0])[1:-2]
            return result

    async def set_gift_id(self, from_id, to_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `helper` (`from_id`, `to_id`) VALUES (%s, %s)", (from_id, to_id))
            await connection.commit()

    async def get_gift_id(self, to_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `from_id` FROM `helper` WHERE `to_id` = %s", (to_id,))
            result = await cursor.fetchall()
            return result

    async def delete_gift(self, from_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM `helper` WHERE `from_id` = %s", (from_id,))
            await connection.commit()

    async def get_full_users_name(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `name` FROM `users`")
            result = await cursor.fetchall()
            return result

    async def change_status(self, user_id, value, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `status` = %s WHERE `user_id` = %s", (value, user_id, ))
            await connection.commit()

    async def get_id(self, name, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `user_id` FROM `users` WHERE `name` = %s", (name, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_user_name(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `link_name` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_full_data(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `users` WHERE `user_id` = %s", (user_id,))
            result = await cursor.fetchall()
            return result

    async def get_size_gift(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `gift_value` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_deposit(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `depozit` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_now_depozit(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `now_depozit` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def set_now_depozit(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `now_depozit` =  %s WHERE user_id = %s", (money, user_id,))
            await connection.commit()

    async def update_step(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `step` = `step` + %s WHERE user_id = %s", (1, user_id,))
            await connection.commit()

    async def reset_step(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `step` = 1 WHERE user_id = %s", (user_id,))
            await connection.commit()

    async def update_planet(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `planet` = `planet` + %s WHERE user_id = %s", (1, user_id,))
            await connection.commit()

    async def add_gift_value(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `gift_value` = `gift_value` + 1 WHERE `user_id` = %s", (user_id,))
            await connection.commit()

    async def get_status(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `status` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0]
            return result

    async def get_first_dep(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `first_dep` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_planet(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `planet` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0]
            return result

    async def get_step(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `step` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_name(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `name` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def change_first_dep(self, user_id, value, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `first_dep` = %s WHERE `user_id` = %s", (value, user_id,))
            await connection.commit()

    async def get_users_on_planet(self, planet, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `users` WHERE `planet` = %s", (planet, ))
            result = await cursor.fetchall()
            return result

    async def get_empty_block_users(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `users` WHERE `block_user_id` = 0 AND `user_id` != %s", (user_id, ))
            result = await cursor.fetchall()
            return result

    async def new_block_user(self, user_id, block_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `block_user_id` = %s WHERE `user_id` = %s", (block_id, user_id))
            await connection.commit()

    async def update_count_ref(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `count_ref` = `count_ref` + 1 WHERE `user_id` = %s", (user_id, ))
            await connection.commit()

    async def update_active(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `active` =  1 WHERE `user_id` = %s", (user_id,))
            await connection.commit()

    async def reset_active(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `active` =  0 WHERE `user_id` = %s", (user_id,))
            await connection.commit()

    async def add_gift_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `gift_money` =  `gift_money` + %s WHERE `user_id` = %s",
                                       (money, user_id,))
            await connection.commit()

    async def remove_gift_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `gift_money` =  `gift_money` - %s WHERE `user_id` = %s",
                                       (money, user_id,))
            await connection.commit()

    async def get_gift_money(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `gift_money` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def add_amount_gift_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `amount_gift_money` =  `amount_gift_money` + %s WHERE `user_id` = %s",
                                       (money, user_id,))
            await connection.commit()

    async def get_ref_money(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `ref_money` FROM `users` WHERE `user_id` = %s",
                                       (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def add_ref_money(self, user_id, money, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `ref_money` =  `ref_money` + %s WHERE `user_id` = %s",
                                       (money, user_id,))
            await connection.commit()

    async def get_amount_gift_money(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `amount_gift_money` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_active(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `active` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_users_of_block(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `link_name` FROM `users` WHERE `block_user_id` = %s", (user_id, ))
            result = await cursor.fetchall()
            return result

    async def get_count_ref(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `count_ref` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def delete_acc(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM `users` WHERE `user_id` = %s", (user_id, ))
            await connection.commit()

    async def have_jump(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `jump` FROM `users` WHERE `user_id` = %s", (user_id,))
            result = (await cursor.fetchall())[0][0]
            return result

    async def reset_jump(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `jump` = 0 WHERE `user_id` = %s", (user_id,))
            await connection.commit()

    async def get_ref_users(self, ref_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `users` WHERE `referrer_id` = %s", (ref_id,))

    async def ref_count(self, ref_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM `users` WHERE `referrer_id` = %s", (ref_id,))

    async def get_last_withd(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `last_withd` FROM `users` WHERE `user_id` = %s", (user_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def set_last_withd(self, user_id, date, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users` SET `last_withd` = %s WHERE `user_id` = %s", (date, user_id, ))
            await connection.commit()

    async def insert_ref_money(self, money, ref_id, user_id, date, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("insert into ref_money (user_id, ref_id, money, date) values (%s, %s, %s, %s)", (user_id, ref_id, money, date, ))
            await connection.commit()


class ManagerPayDataBase:
    async def create_pay(self, pay_id, pay_type, pay_amount, date, user_id, canc_id, status, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `pay` (`pay_id`, `pay_amount`, `date`,  `pay_type`, `user_id`, "
                                      "`cancel_id`, `status`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                       (pay_id, pay_amount, date, pay_type, user_id, canc_id, status))
            await connection.commit()

    async def get_data(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `pay` WHERE `user_id` = %s", (user_id,))
            result = await cursor.fetchall()
            return result

    async def get_data_canc(self, canc_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `pay` WHERE `cancel_id` = %s", (canc_id,))
            result = await cursor.fetchall()
            return result

    async def cancel_request(self, canc_id, type, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            if type == "CREDIT":
                await cursor.execute("DELETE FROM `pay` WHERE `cancel_id` = %s", (canc_id,))
                await connection.commit()
            else:
                await cursor.execute("DELETE FROM `crypt_pay` WHERE `cancel_id` = %s", (canc_id,))
                await connection.commit()

    async def get_users(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `user_id` FROM `pay`")
            result = await cursor.fetchall()
            return result

    async def create_crypt_pay(self, pay_type, pay_amount, date, user_id, canc_id, status, amount_rub, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `crypt_pay` (`amount`, `date`,  `pay_type`, `user_id`, `cancel_id`,"
                                       " `status`, `amount_rub`) "
                                       "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                       (pay_amount, date, pay_type, user_id, canc_id, status, amount_rub))
            await connection.commit()

    async def get_status(self, canc_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `status` FROM `crypt_pay` WHERE `cancel_id` = %s", (canc_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_status_credit(self, canc_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `status` FROM `pay` WHERE `cancel_id` = %s", (canc_id, ))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_data_crypt(self, canc_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `crypt_pay` WHERE `cancel_id` = %s", (canc_id,))
            result = await cursor.fetchall()
            return result

    async def get_all_data_crypt(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `crypt_pay`")
            result = await cursor.fetchall()
            return result

    async def change_status(self, status, user_id, type, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            if type == "CREDIT":
                await cursor.execute("UPDATE `pay` SET `status` = %s WHERE `user_id` = %s",
                                           (status, user_id,))
                await connection.commit()
            else:
                await cursor.execute("UPDATE `crypt_pay` SET `status` = %s WHERE `user_id` = %s",
                                           (status, user_id,))
                await connection.commit()

    async def change_status_for_cancel(self, status, cancel, type, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            if type == "CREDIT":
                await cursor.execute("UPDATE `pay` SET `status` = %s WHERE `cancel_id` = %s", (status, cancel,))
                await connection.commit()
            else:
                await cursor.execute("UPDATE `crypt_pay` SET `status` = %s WHERE `cancel_id` = %s", (status, cancel,))
                await connection.commit()

    async def get_count_crypt(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM `crypt_pay`")
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_count_credit(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM `pay`")
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_amount_rub_crypt(self, cancel_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `amount_rub` FROM `crypt_pay` WHERE `cancel_id` = %s", (cancel_id))
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_all_transactions(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `transactions`")
            result = await cursor.fetchall()
            return result

    async def create_trans(self, amount, currency, date, wallet, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `transactions`(`amount`, `currency`, `date`, `wallet`, `status`) "
                                "VALUES (%s, %s, %s, %s, 'PROCESSED')", (amount, currency, date, wallet, ))
            await connection.commit()

    async def check_exist(self, amount, currency, date, wallet, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT EXISTS(SELECT id FROM `transactions` WHERE `amount` = %s AND "
                                       "`currency` = %s AND `date` = %s AND `wallet` = %s)", (amount, currency, date, wallet,))
            result = await cursor.fetchall()
            return result

    async def change_status_trans(self, id, status, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `transactions` SET `status` = %s WHERE `id` = %s", (status , id))
            await connection.commit()


class ManagerWithDrawDataBase:
    async def create_request_crypt(self, card, data, type, amount, amount_crypt, amount_commission, user_id, date, type_crypt, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `withdraw` (`card`, `data`, `type`, `amount`, `amount_crypt`, "
                                 "`amount_commission`,`user_id`, `date`, `status`, `type_crypt`) VALUES (%s, %s, %s, %s, "
                                       "%s, %s,  %s, %s, %s, %s)", (card, data, type, amount, amount_crypt,
                                                                    amount_commission, user_id, date, 'В ожидании', type_crypt, ))
            await connection.commit()

    async def create_request_bank(self, card, data, type, amount, amount_commission, user_id, date, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `withdraw` (`card`, `data`, `type`, `amount`, `amount_commission`, `user_id`, `date`, `status`) VALUES (%s, %s, %s, %s, "
                                       "%s, %s, %s, %s)", (card, data, type, amount, amount_commission, user_id, date, 'В ожидании'))
            await connection.commit()

    async def delete_request(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM `withdraw` WHERE `user_id` = %s", (user_id,))
            await connection.commit()

    async def get_all_request(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `withdraw`")

    async def get_other_request(self, user_id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `withdraw` WHERE `user_id` = %s", (user_id,))


class ManagerClonesDataBase:
    async def create_clone(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("INSERT INTO `clones` (`active`) VALUES (1)")
            await connection.commit()

    async def get_count_clones(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM `clones`")
            result = (await cursor.fetchall())[0][0]
            return result

    async def get_all(self, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM `clones`")
            result = await cursor.fetchall()
            return result

    async def change_active(self, id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `clones` SET `active` = 0 WHERE `id` = ?", (id, ))
            await connection.commit()

    async def reset_clone(self, id, loop):
        connection, cursor = await async_connect_to_mysql(loop)
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM `clones` WHERE `id` = ?", (id, ))
            await connection.commit()
