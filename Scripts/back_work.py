import asyncio
from aiogram import Bot
import sys
import coinbase_data
import inline_keybords
import time
from config import PATH

from db import ManagerPayDataBase, ManagerUsersDataBase, ManagerClonesDataBase
import Payment
from helper import clear_repeat, cancel_unnecessary
import clones
import helper
from datetime import datetime

dbPay = ManagerPayDataBase()
dbUser = ManagerUsersDataBase()
dbClones = ManagerClonesDataBase()


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
                            #if dbPay.get_status_credit(pay[5]) != "CANCELED":
                                await bot.send_message(
                                    user[0],
                                    f"Ваша заявка на пополнение {pay[0]} отменена автоматечески т.к. "
                                    f"оплата не поступила в течении 60-ти минут"
                                )
                                await dbPay.change_status_for_cancel("CANCELED", pay[5], "CREDIT", loop)
                                print(f"Ваша заявка на пополнение {pay[0]} отменена автоматечески")
                                #dbPay.cancel_request(pay[5], "CREDIT")   #Удаление платежа из БД
                                await bot.delete_message(user[0], pay[5])

                        elif status_payment == "OPERATION_COMPLETED":   # Проверка пополнения счета
                            # print(dbPay.get_status_credit(pay[5]))
                            #if dbPay.get_status_credit(pay[5]) != "OPERATION_COMPLETED":
                                # Пополнение счетов
                                await dbUser.add_depozit(user[0], pay[1], loop)
                                await dbUser.add_money(user[0], pay[1], loop)
                                await dbUser.add_gift_money(user[0], pay[1], loop)

                                # Оповещение реферала
                                referrer_id = await dbUser.get_referrer_of_user(user[0], loop)
                                if referrer_id != "None":
                                    dep = pay[1] * .1
                                    await dbUser.insert_ref_money(dep, referrer_id, user[0], datetime.now(), loop)
                                    await dbUser.add_money(int(referrer_id), dep, loop)
                                    await dbUser.add_depozit(int(referrer_id), dep, loop)
                                    await bot.send_message(
                                        referrer_id,
                                        f"Ваш реферал {await dbUser.get_name(user[0], loop)} пополнил баланс и вам подарили {dep} RUB."
                                    )
                                await bot.delete_message(user[0], pay[5])
                                with open(PATH + "img\\dep_done.png", 'rb') as file:
                                    await bot.send_photo(
                                        user[0],
                                        photo=file,
                                        caption=f"Платеж {pay[0]} успешно выполнен. Ваш счет пополненен на {pay[1]} руб.\n"
                                    )
                                await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[5], "CREDIT", loop)
                                #dbPay.cancel_request(pay[5], "CREDIT")

                                depozit = await dbUser.get_deposit(user[0], loop)

                                if depozit >= 5000:
                                    await clones.create_clones(pay[1], loop)

                                # В случай первого пополнения
                                now_dep = await dbUser.get_now_depozit(user[0], loop)
                                if now_dep <= 0:
                                    await dbUser.set_now_depozit(user[0], pay[1], loop)
                                    response = "Супер 🙌 \n" \
                                               f"Вы пополнили депозит на {pay[1]}₽\n\n" \
                                               "Хорошая новость!!!\n" \
                                               "Space Gift увеличит 🚀 Ваш депозит в 2 раза, для этого \n" \
                                               "Вам нужно нажать кнопку 👇"

                                    with open(PATH + "img\\double_dep.png", 'rb') as file:
                                        await bot.send_photo(
                                            user[0], photo=file,
                                            caption=response,
                                            parse_mode="HTML",
                                            reply_markup=inline_keybords.get_double_dep()
                                        )

                        elif status_payment == "WAIT_PAYMENT":
                            print(f"Платеж {pay[0]} в процессе")


            #Обработчик пополнения Coinbase
            transactions = await coinbase_data.get_completed_transactions(loop)
            pays_db = helper.clear_crypt_requests(await dbPay.get_all_data_crypt(loop))
            for transaction in transactions:

                #if (datetime.strptime(str(datetime.now())[:-7], '%Y-%m-%d %H:%M:%S') - datetime.
                        #strptime(str(transaction.date), '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600 < 1:
                if transaction.status == "PROCESSED":
                    for pay in pays_db:
                        if str(transaction.date) == pay[2] and float(transaction.amount) == float(pay[0]) \
                                and transaction.currency == pay[3] and await dbPay.get_status(pay[4], loop) != "CANCELED":
                            amount_rub = await dbPay.get_amount_rub_crypt(pay[4], loop)
                            await dbUser.add_money(pay[1], amount_rub, loop)
                            await dbUser.add_depozit(pay[1], amount_rub, loop)
                            await dbUser.add_gift_money(pay[1], amount_rub, loop)

                            with open(PATH + "img\\dep_done.png", 'rb') as file:
                                await bot.send_photo(
                                    pay[1], photo=file,
                                    caption=f"Платеж успешно выполнен. Ваш счет пополненен на {pay[0]} {pay[3]}."
                                )
                            await bot.delete_message(pay[1], pay[4])
                            await dbPay.change_status_for_cancel("OPERATION_COMPLETED", pay[4], "CRYPT", loop)
                            await dbPay.change_status_trans(transaction.id, "COMPLETED", loop)

                            referrer_id = await dbUser.get_referrer_of_user(pay[1], loop)
                            if referrer_id != "None":
                                dep = pay[0] * .1
                                await dbUser.insert_ref_money(dep, referrer_id, pay[1], datetime.now(), loop)
                                await dbUser.add_money(int(referrer_id), dep, loop)
                                await dbUser.add_depozit(int(referrer_id), dep, loop)

                                await bot.send_message(
                                    referrer_id,
                                    f"Ваш реферал {dbUser.get_name(pay[1], loop)} пополнил баланс и вам подарили {dep} RUB."
                                )
                            now_dep = await dbUser.get_now_depozit(pay[1], loop)
                            if now_dep <= 0:
                                await dbUser.set_now_depozit(pay[1], amount_rub, loop)
                                response = "Поздравлем! <b>Space Gift</b> увеличит 🚀 Ваш депозит, " \
                                           "для того что бы Вы сделали подарок астронавту на планете меркурий " \
                                           "и активировались на уровне 1, для этого нажмите на кнопку 👇"

                                with open(PATH + "img\\laucnh.jpg", 'rb') as file:
                                    await bot.send_photo(
                                        pay[1], photo=file,
                                        caption=response,
                                        parse_mode="HTML",
                                        reply_markup=inline_keybords.get_double_dep()
                                    )

            end_program_time = time.time()
            print(f'BACKGROUND LAP PAY TIME: {end_program_time - start_program_time}')

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)

        await asyncio.sleep(50)
