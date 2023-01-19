import asyncio
import time
import datetime

import pytz
from aiogram import Bot
import sys
from db import ManagerPayDataBase, ConfigDBManager
import coinbase_data
from helper import clear_none

import db
from db import ManagerUsersDataBase

dbUser = ManagerUsersDataBase()
dbPay = ManagerPayDataBase()


configCl = ConfigDBManager.get()

API_TOKEN = configCl.api_bot  # Считывание токена
bot = Bot(token=API_TOKEN)


async def send_message_safe(bot, tel_id, text, reply_markup=None):
    try:
        await bot.send_message(tel_id, text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception:
        pass


async def worker_percent(loop):
    while True:
        try:
            start_program_time = time.time()
            users = await dbUser.get_users(loop)

            for user in users:
                if user[0] is None:
                    continue

                date = (await dbUser.get_date_now(user[0], loop)).astimezone(pytz.timezone("UTC"))

                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                if (date_time_now - date).days >= 1:
                    status = await dbUser.get_status(user[0], loop)
                    planet = await dbUser.get_planet(user[0], loop)
                    payments = await dbPay.get_user_topups(user[0], loop)

                    if (status[0] == 1 or int(planet[0]) > 0) and payments > 0:
                        await dbUser.set_new_date(user[0], date_time_now, loop)
                        cd = float(await dbUser.get_amount_gift_money(user[0], loop))
                        dep = float(await dbUser.get_deposit(user[0], loop))
                        ref = await dbUser.get_activate_count_ref(user[0], loop) * 5000
                        ref_money = float(await dbUser.get_percent_ref_money(user[0], loop))
                        reinv = float(await dbUser.get_reinvest(user[0], loop))

                        full_money = cd + dep + ref + ref_money + reinv
                        money = round(float(full_money) * .008)
                        await send_message_safe(bot, user[0], f"На ваш счет начислилось {money} RUB")
                        await dbUser.add_gift_money(user[0], money, loop)
                        print(f"На {user[0]} счет был начислен процент")

            pays_db = await dbPay.get_all_data_crypt(loop)

            for pay in pays_db:
                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                if (datetime.datetime.strptime(str(date_time_now)[:-13], '%Y-%m-%d %H:%M:%S') -
                       datetime.datetime.strptime(str(pay[2]), '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600 > 1 and \
                        (await dbPay.get_status(pay[4], loop)) == "WAIT_PAYMENT":
                    try:
                        await bot.delete_message(pay[1], pay[4])
                    except:
                        pass

                    await send_message_safe(
                        bot,
                        pay[1],
                        f"Ваша заявка на пополнение криптовалюты отменена "
                        f"автоматечески т.к. оплата не поступила в течении 60-ти минут"
                    )

                    await dbPay.change_status_for_cancel("CANCELED", pay[4], "CRYPT", loop)

            transatcions = await coinbase_data.get_completed_transactions(loop)

            for transatcion in transatcions:
                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                if (datetime.datetime.strptime(str(date_time_now)[:-13], '%Y-%m-%d %H:%M:%S') -
                    datetime.datetime.strptime(str(transatcion.date), '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600 > 1\
                    and transatcion.status == "WAIT_PAYMENT":
                    await dbPay.change_status_trans(transatcion.id, 'CANCELED', loop)

            end_program_time = time.time()
            print(f'BACKGROUND LAP PERCENT TIME: {end_program_time - start_program_time}')
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Percent')
            config = db.ConfigDBManager().get()
            await bot.send_message(config.errors_group_id, f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Percent')

        await asyncio.sleep(20)
