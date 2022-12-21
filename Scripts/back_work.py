import asyncio

import pytz
from aiogram import Bot
import sys
import coinbase_data
import time

import db
from config import PATH

from db import ManagerPayDataBase, ManagerUsersDataBase, ManagerClonesDataBase
import Payment
from helper import clear_repeat, cancel_unnecessary
import clones
import helper
import datetime

dbPay = ManagerPayDataBase()
dbUser = ManagerUsersDataBase()
dbClones = ManagerClonesDataBase()


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


async def worker(bot: Bot, loop):
    while True:
        try:
            start_program_time = time.time()

            # Обработчик пополнения банковской картой
            users_db = await dbPay.get_users(loop)
            users = clear_repeat(users_db)

            for user in users:
                user_data = await dbPay.get_data(user[0], loop)
                user_data = cancel_unnecessary(user_data)
                for pay in user_data:

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
                                await dbUser.add_depozit(user[0], pay[1], loop)
                                await dbUser.add_money(user[0], pay[1], loop)
                                await dbUser.add_gift_money(user[0], pay[1], loop)

                                # Оповещение реферала
                                referrer_id = await dbUser.get_referrer_of_user(user[0], loop)
                                first_dep = await dbUser.get_first_dep(user[0], loop)
                                if referrer_id != "None" and first_dep == 0:
                                    dep = pay[1] * .1
                                    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                                    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
                                    await dbUser.insert_ref_money(dep, referrer_id, user[0], date_time_now, loop)
                                    await dbUser.add_money(int(referrer_id), dep, loop)
                                    await dbUser.set_percent_ref_money(int(referrer_id), dep, loop)
                                    await send_message_safe(
                                        bot,
                                        referrer_id,
                                        f"Ваш реферал {await dbUser.get_name(user[0], loop)} "
                                        f"пополнил баланс и вам подарили {dep} RUB."
                                    )
                                await bot.delete_message(user[0], pay[5])

                                if pay[1] <= 5000:
                                    with open(PATH + "/img/dep_done.png", 'rb') as file:
                                        await send_message_safe(
                                            bot,
                                            user[0],
                                            f"Платеж {pay[0]} успешно выполнен. Ваш счет пополненен на {pay[1]} руб.",
                                            file
                                        )
                                else:
                                    await send_message_safe(bot, user[0], f"Платеж {pay[0]} успешно выполнен. Ваш счет пополненен на {pay[1]} руб.")

                                await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[5], "CREDIT", loop)
                                depozit = await dbUser.get_deposit(user[0], loop)

                                if depozit >= 5000:
                                    await clones.create_clones(pay[1], loop)

                        elif status_payment == "WAIT_PAYMENT":
                            print(f"Платеж {pay[0]} в процессе")

            #Обработчик пополнения Coinbase
            transactions = await coinbase_data.get_completed_transactions(loop)
            pays_db = helper.clear_crypt_requests(await dbPay.get_all_data_crypt(loop))
            for transaction in transactions:

                if transaction.status == "PROCESSED":
                    for pay in pays_db:
                        if transaction.date > pay[2] and float(transaction.amount) == float(pay[0]) \
                                and transaction.currency == pay[3] and await dbPay.get_status(pay[4], loop) != "CANCELED"\
                                and await dbPay.get_status(pay[4], loop) != 'OPERATION_COMPLETED':

                            amount_rub = await dbPay.get_amount_rub_crypt(pay[4], loop)
                            await dbUser.add_money(pay[1], amount_rub, loop)
                            await dbUser.add_depozit(pay[1], amount_rub, loop)
                            await dbUser.add_gift_money(pay[1], amount_rub, loop)

                            if float(pay[6]) <= 5000:

                                with open(PATH + "/img/dep_done.png", 'rb') as file:
                                    await send_message_safe(
                                        bot,
                                        pay[1],
                                        f"Платеж успешно выполнен. Ваш счет пополненен на {pay[0]} {pay[3]}.",
                                        file
                                    )
                            else:
                                await send_message_safe(bot, pay[1], f"Платеж успешно выполнен. Ваш счет пополненен на {pay[0]} {pay[3]}.")

                            await bot.delete_message(pay[1], pay[4])
                            await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[4], "CRYPT", loop)
                            await dbPay.change_status_trans(transaction.id, "COMPLETED", loop)

                            referrer_id = await dbUser.get_referrer_of_user(pay[1], loop)
                            if referrer_id != "None":
                                dep = pay[0] * .1
                                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
                                await dbUser.insert_ref_money(dep, referrer_id, pay[1], date_time_now, loop)
                                await dbUser.add_money(int(referrer_id), dep, loop)
                                await dbUser.add_depozit(int(referrer_id), dep, loop)

                                await send_message_safe(bot, referrer_id,
                                                        f"Ваш реферал {dbUser.get_name(pay[1], loop)} пополнил баланс и вам подарили {dep} RUB.")

                            depozit = await dbUser.get_deposit(pay[1], loop)

                            if depozit >= 5000:
                                await clones.create_clones(amount_rub, loop)

            end_program_time = time.time()
            print(f'BACKGROUND LAP PAY TIME: {end_program_time - start_program_time}')

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            config = db.ConfigDBManager().get()
            await bot.send_message(
                config.errors_group_id,
                f'{exc_type}, {exc_obj}, {exc_tb} from back_works'
            )

        await asyncio.sleep(30)
