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
            config = db.ConfigDBManager().get()

            for user in users:
                if user[0] is None:
                    continue

                # Проверка денег с планет
                status = bool((await dbUser.get_status(user[0], loop))[0])
                current_planet = int((await dbUser.get_planet(user[0], loop))[0])
                step = int(await dbUser.get_step(user[0], loop))
                user_data = (await dbUser.get_full_data(user[0], loop))[0]

                user_money = int(await dbUser.get_amount_gift_money(user[0], loop))
                verify_sum = sums[current_planet] * step

                user_name = f"{user_data[3]} ({user_data[1]})"
                if user_data[7]:
                    user_name = f"@{user_data[7]}"

                if user_money > verify_sum and not (status is False and current_planet == 0):
                    # await bot.send_message(
                    #     config.errors_group_id,
                    #     f'У пользователя {user_name} на балансе сумма {user_money} рублей. Правильная сумма {verify_sum} рублей',
                    # )
                    print(f'У пользователя {user_name} на балансе сумма {user_money} рублей. Правильная сумма {verify_sum} рублей')


                # Проверка рефералов
                user_ref = (await dbUser.get_ref_users(user[0], loop))
                activate_ref_count = user_data[27]

                user_active_ref_count = 0
                for ref in user_ref:
                    is_active = await dbUser.is_first_user_topup(ref[1], loop)
                    if is_active:
                        user_active_ref_count += 1

                if user_active_ref_count > activate_ref_count:
                    # await bot.send_message(
                    #     config.errors_group_id,
                    #     f'У пользователя {user_name} {user_ref_active_count} активированных рефералов. Правильное количество {active_ref_count}',
                    # )
                    print(
                        f'У пользователя {user_name} {activate_ref_count} активированных рефералов.'
                        f' Правильное количество {user_active_ref_count}'
                    )

            end_program_time = time.time()
            print(f'BACKGROUND LAP VERIFY TIME: {end_program_time - start_program_time}')
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Verify Balance')
            #config = db.ConfigDBManager().get()
            #await bot.send_message(config.errors_group_id, f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from Verify Baance')

        await asyncio.sleep(60 * 60)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.run(worker_verify_balance(loop))
