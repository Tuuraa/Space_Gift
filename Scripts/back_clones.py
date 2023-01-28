import asyncio

import sys
import time

from aiogram import Bot

import helper
import clones
import db
import logic
from User import UserDB


dbUser = db.ManagerUsersDataBase()
dbClones = db.ManagerClonesDataBase()


configCl = db.ConfigDBManager.get()

API_TOKEN = configCl.api_bot  # Считывание токена
bot = Bot(token=API_TOKEN)


async def send_message_safe(bot, tel_id, text, reply_markup=None):
    try:
        await bot.send_message(
            tel_id,
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)


async def worker_clones(loop):
    while True:
        try:
            start_program_time = time.time()
            print('TEST')
            await clones.update_active_user(loop)

            users = await helper.get_users((await dbUser.get_users_on_planet(0, loop)), loop)
            status_active_users = helper.get_active_status_users(users, 0)
            active_user: UserDB = await clones.get_active_user(status_active_users)

            try:
                if active_user is not None:

                    while int(await dbUser.get_step(active_user.user_id, loop)) < 5:
                        if int((await dbUser.get_planet(active_user.user_id, loop))[0]) == 0:
                            if await dbClones.get_count_clones(loop) > 0:
                                if int(await dbUser.get_step(active_user.user_id, loop)) == 4:
                                    await dbUser.add_amount_gift_money(active_user.user_id, 5000, loop)
                                    await send_message_safe(
                                        bot,
                                        active_user.user_id,
                                        "🎆 Поздравляем 🎆 вам сделал подарок "
                                        "<b>клон системы</b> и продвинул вас на новую планету 🪐."
                                    )
                                    await dbUser.update_planet_clones(active_user.user_id, loop)
                                    #await dbUser.reset_step(active_user.user_id, loop)
                                    #await dbUser.change_status(active_user.user_id, 0, loop)
                                    #await dbUser.reset_active(active_user.user_id, loop)
                                    #await dbUser.change_first_dep(active_user.user_id, 0, loop)
                                    await logic.gift(bot, active_user, loop)
                                    await dbUser.update_planet(active_user.user_id, loop)

                                else:
                                    clones_act = await dbClones.get_all(loop)
                                    await dbUser.update_step(active_user.user_id, loop)
                                    ind = clones_act[0][0]
                                    await dbClones.reset_clone(ind, loop)
                                    await dbUser.add_amount_gift_money(active_user.user_id, 5000, loop)
                                    await send_message_safe(
                                        bot,
                                        active_user.user_id,
                                        "Поздравляем! 🎉 Вам сделал подарок 🎁 "
                                        "<b>клон системы</b> и продвинул вас на новый уровень 🚀."
                                    )
                                    await logic.get_launch(bot, active_user.user_id, loop)
                            else:
                                break
                        else:
                            break
                        await clones.update_active_user(loop)

            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_obj, exc_tb.tb_lineno)
                config = db.ConfigDBManager().get()

                await bot.send_message(
                        config.errors_group_id,
                    f'{exc_type}, {exc_obj}, {exc_tb} from back_clones'
                )

            end_program_time = time.time()
            print(f'BACKGROUND LAP CLONES SYSTEM TIME: {end_program_time - start_program_time}\n')

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)
            config = db.ConfigDBManager().get()
            try:
                await bot.send_message(
                    config.errors_group_id,
                    f'{exc_type}, {exc_obj}, {exc_tb} from back_clones'
                )
            except:
                pass

        await asyncio.sleep(20)
