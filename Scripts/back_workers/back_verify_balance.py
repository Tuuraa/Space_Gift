import asyncio
import time
import datetime

import pytz
from aiogram import Bot
import sys
from db import ManagerPayDataBase, ConfigDBManager

import db
from db import ManagerUsersDataBase
from logic import sums


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


async def worker_verify_balance(loop):
    while True:
        try:
            start_program_time = time.time()
            users = await dbUser.get_users(loop)

            for user in users:
                if user[0] is None:
                    continue


                status = bool((await dbUser.get_status(user[0], loop))[0])
                current_planet = int((await dbUser.get_planet(user[0], loop))[0])
                step = int(await dbUser.get_step(user[0], loop))

                if status is False and current_planet == 0:
                    continue

                user_money = int(await dbUser.get_amount_gift_money(user[0], loop))
                verify_sum = sums[current_planet] * step

                if user_money != verify_sum:
                    print(f"{user[0] = }, {current_planet = }, {step = }\n{user_money = } || {verify_sum = }\n\n")

            end_program_time = time.time()
            print(f'BACKGROUND LAP PERCENT TIME: {end_program_time - start_program_time}')
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Percent')
            # config = db.ConfigDBManager().get()
            # await bot.send_message(config.errors_group_id, f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Percent')

        await asyncio.sleep(20)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.run(worker_verify_balance(loop))