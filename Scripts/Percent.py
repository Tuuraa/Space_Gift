import asyncio
import time
from datetime import datetime
from aiogram import Bot
import sys
from db import ManagerPayDataBase
import coinbase_data

from db import ManagerUsersDataBase

dbUser = ManagerUsersDataBase()
dbPay = ManagerPayDataBase()


async def worker_percent(bot: Bot, loop):
    while True:
        try:
            start_program_time = time.time()
            users = await dbUser.get_users(loop)

            for user in users:
                date = str(await dbUser.get_date_now(user[0], loop))
                dt_to_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                if (datetime.now() - dt_to_datetime).days >= 1:
                    money = float(await dbUser.get_money(user[0], loop))
                    if money >= 5000.0:
                        #dbUser.add_procent(user[0])
                        await dbUser.set_new_date(user[0], datetime.now(), loop)
                        money = round(float(await dbUser.get_money(user[0], loop)) * .006)
                        await bot.send_message(user[0], f"На ваш счет начислилось {money} RUB")
                        await dbUser.add_gift_money(user[0], money, loop)
                        print(f"На {user[0]} счет был начислен процент")

            pays_db = await dbPay.get_all_data_crypt(loop)

            for pay in pays_db:
                if (datetime.strptime(str(datetime.now())[:-7], '%Y-%m-%d %H:%M:%S') -
                       datetime.strptime(str(pay[2]), '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600 > 1 \
                        and await dbPay.get_status(pay[4], loop) != "CANCELED":

                    await bot.delete_message(pay[1], pay[4])
                    await bot.send_message(
                        pay[1],
                        f"Ваша заявка на пополнение криптовалюты отменена "
                        f"автоматечески т.к. оплата не поступила в течении 60-ти минут"
                    )

                    await dbPay.change_status_for_cancel("CANCELED", pay[4], "CRYPT", loop)

            transatcions = await coinbase_data.get_completed_transactions(loop)

            for transatcion in transatcions:
                if (datetime.strptime(str(datetime.now())[:-7], '%Y-%m-%d %H:%M:%S') -
                    datetime.strptime(str(transatcion.date), '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600 > 1\
                    and transatcion.status != "CANSELED":

                    await dbPay.change_status_trans(transatcion.id, 'CANCELED', loop)

            end_program_time = time.time()
            print(f'BACKGROUND LAP PERCENT TIME: {end_program_time - start_program_time}')

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)

        await asyncio.sleep(45)