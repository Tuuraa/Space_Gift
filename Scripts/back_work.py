import asyncio

import pytz
from aiogram import Bot
import sys
import coinbase_data
import time

import db
import os
from config import PATH

from db import ManagerPayDataBase, ManagerUsersDataBase, ManagerClonesDataBase, ConfigDBManager
import Payment
from helper import clear_repeat, cancel_unnecessary
import clones
import helper
import datetime

dbPay = ManagerPayDataBase()
dbUser = ManagerUsersDataBase()
dbClones = ManagerClonesDataBase()

configCl = ConfigDBManager.get()

API_TOKEN = configCl.api_bot  # Считывание токена
bot = Bot(token=API_TOKEN)


async def send_message_safe(bot: Bot, tel_id, text, link=None, reply_markup=None):
    try:
        if link is not None:
            await bot.send_photo(
                tel_id,
                photo=link,
                caption=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await bot.send_message(tel_id, text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception:
        pass


async def worker(loop):
    while True:
        print(1)
        try:
            start_program_time = time.time()

            # Обработчик пополнения банковской картой
            users_db = await dbPay.get_users(loop)
            users = clear_repeat(users_db)

            for user in users:
                user_data = await dbPay.get_data(user[0], loop)
                user_data = cancel_unnecessary(user_data)
                for pay in user_data:
                    print(pay)
                    if await Payment.get_order(pay[0]):

                        status_payment = await Payment.status_requets(pay[0])
                        if status_payment == "CANCELED":
                            await dbPay.change_status_for_cancel("CANCELED", pay[5], "CREDIT", loop)
                            print(f"Ваша заявка на пополнение {pay[0]} отменена автоматечески")
                            await bot.delete_message(user[0], pay[5])

                            await send_message_safe(
                                bot,
                                user[0],
                                f"Ваша заявка на пополнение {pay[0]} отменена автоматечески т.к. "
                                f"оплата не поступила в течении 60-ти минут"
                            )

                        elif status_payment == "OPERATION_COMPLETED":   # Проверка пополнения счета
                                # Пополнение счетов
                                is_fist_pay = await dbUser.is_first_user_topup(user[0], loop)
                                await dbUser.add_money_and_dep(user[0], pay[1], loop)

                                # Оповещение реферала
                                referrer_id = await dbUser.get_referrer_of_user(user[0], loop)
                                status = await dbUser.get_status(user[0], loop)
                                if referrer_id and status[0] == 1 and not is_fist_pay:
                                    dep = pay[1] * .1
                                    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                                    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
                                    await dbUser.insert_ref_money(dep, int(referrer_id), user[0], date_time_now, loop)
                                    await dbUser.add_money_and_pecr_ref_money(int(referrer_id), dep, loop)

                                    await send_message_safe(
                                        bot,
                                        referrer_id,
                                        f"Ваш реферал @{await dbUser.get_name(user[0], loop)} "
                                        f"пополнил баланс и вам подарили {dep} RUB."
                                    )

                                if pay[1] <= 5000:
                                    with open(PATH + "/img/dep_done.png", 'rb') as file:
                                        await send_message_safe(
                                            bot,
                                            user[0],
                                            f"Платеж {pay[0]} успешно выполнен. Ваш счет пополнен на {pay[1]} руб.",
                                            file
                                        )
                                else:
                                    await send_message_safe(bot, user[0], f"Платеж {pay[0]} успешно выполнен. Ваш счет пополненен на {pay[1]} руб.")

                                await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[5], "CREDIT", loop)
                                status = await dbUser.get_status(user[0], loop)
                                planet = await dbUser.get_planet(user[0], loop)

                                if (status == 1 or int(planet[0]) > 0) and pay[1] >= 5000:
                                    #await clones.create_clones(pay[1], loop)
                                    await helper.create_ref(pay[1], user[0], loop)


            #Обработчик пополнения Coinbase
            transactions = await coinbase_data.get_completed_transactions(loop)
            pays_db = helper.clear_crypt_requests(await dbPay.get_all_data_crypt(loop))
            for transaction in transactions:

                if transaction.status == "PROCESSED":
                    for pay in pays_db:
                        if transaction.date > pay[2] and float(transaction.amount) == float(pay[0]) \
                                and transaction.currency == pay[3] and await dbPay.get_status(pay[4], loop) != "CANCELED"\
                                and await dbPay.get_status(pay[4], loop) != 'OPERATION_COMPLETED':
                            is_fist_pay = dbUser.is_first_user_topup(pay[1], loop)

                            amount_rub = await dbPay.get_amount_rub_crypt(pay[4], loop)
                            await dbUser.add_money_and_dep(pay[1], amount_rub, loop)

                            if float(pay[6]) <= 5000:

                                with open(PATH + "/img/dep_done.png", 'rb') as file:
                                    await send_message_safe(
                                        bot,
                                        pay[1],
                                        f"Платеж успешно выполнен. Ваш счет пополненен на {pay[0]} {pay[3]}.",
                                        file
                                    )
                            else:
                                await send_message_safe(
                                    bot,
                                    pay[1],
                                    f"Платеж успешно выполнен. Ваш счет пополненен на {pay[0]} {pay[3]}."
                                )

                            await bot.delete_message(pay[1], pay[4])
                            await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[4], "CRYPT", loop)
                            await dbPay.change_status_trans(transaction.id, "COMPLETED", loop)

                            referrer_id = await dbUser.get_referrer_of_user(pay[1], loop)
                            status = await dbUser.get_status(pay[1], loop)

                            if referrer_id != "None" and status[0] == 1 and not is_fist_pay:
                                dep = amount_rub * .1
                                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
                                # добавялем деньги (10%) (табличка ref_money)
                                await dbUser.insert_ref_money(dep, referrer_id, pay[1], date_time_now, loop)
                                # добавляем деньги в депозит юзера и добавляем в percent_money (поле у user)
                                await dbUser.add_money_and_pecr_ref_money(int(referrer_id), dep, loop)

                                await send_message_safe(bot, referrer_id,
                                                        f"Ваш реферал {dbUser.get_name(pay[1], loop)} "
                                                        f"пополнил баланс и вам подарили {dep} RUB.")

                            status = await dbUser.get_status(pay[1], loop)
                            planet = await dbUser.get_planet(pay[1], loop)

                            if (status == 1 or int(planet[0]) > 0) and amount_rub >= 5000:
                                #await clones.create_clones(amount_rub, loop)
                                await helper.create_ref(amount_rub, pay[1], loop)

            end_program_time = time.time()
            print(f'BACKGROUND LAP PAY TIME: {end_program_time - start_program_time}')
            await asyncio.sleep(30)
        except Exception:
            print(f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from back_works')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            config = db.ConfigDBManager().get()
            await bot.send_message(
                config.errors_group_id,
                f'{exc_type}, {exc_obj}, {exc_tb}, {exc_tb.tb_lineno} from back_works'
            )
