import asyncio

import sys
import time
import helper
import clones
import db
import logic
from User import UserDB


dbUser = db.ManagerUsersDataBase()
dbClones = db.ManagerClonesDataBase()


async def worker_clones(bot, loop):
    while True:
        try:
            start_program_time = time.time()
            await clones.update_active_user(loop)
            users = helper.get_users((await dbUser.get_users_on_planet(0, loop)))
            status_active_users = helper.get_active_status_users(users, 0)
            active_user: UserDB = await clones.get_active_user(status_active_users)

            try:
                while int(await dbUser.get_step(active_user.user_id, loop)) < 5:
                    if int((await dbUser.get_planet(active_user.user_id, loop))[0]) == 0:
                        if await dbClones.get_count_clones(loop) > 0:
                            if int(await dbUser.get_step(active_user.user_id, loop)) == 4:
                                await bot.send_message(
                                    active_user.user_id,
                                    "🎆 Поздравляем 🎆 вам сделал подарок <b>клон системы и продвинул вас на новую планету 🪐."
                                )
                                await logic.gift(bot, active_user, loop)
                                await dbUser.reset_step(active_user.user_id, loop)
                                await dbUser.change_status(active_user.user_id, 0, loop)
                                await dbUser.update_planet(active_user.user_id, loop)
                                await dbUser.reset_active(active_user.user_id, loop)
                            else:
                                await bot.send_message(
                                    active_user.user_id,
                                    "Поздравляем! 🎉 Вам сделал подарок 🎁 <b>клон системы</b> и продвинул вас на новый уровень 🚀."
                                )
                                clones_act = await dbClones.get_all(loop)
                                await dbUser.update_step(active_user.user_id, loop)
                                ind = clones_act[0][0]
                                await dbClones.reset_clone(ind, loop)
                                await logic.get_launch(bot, active_user.user_id, loop)
                        else:
                            break
                    else:
                        break
                    await clones.update_active_user(loop)

            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                if exc_obj.args[0] == "'NoneType' object has no attribute 'user_id'":
                    pass

                elif exc_obj.match == 'bot was blocked by the user':
                    await dbUser.change_status(active_user.user_id, 0, loop)
                    await dbUser.reset_active(active_user.user_id, loop)
                    print(f"The user {active_user.link} has been reset. Reason: canceled the bot")

            end_program_time = time.time()
            print(f'BACKGROUND LAP CLONES SYSTEM TIME: {end_program_time - start_program_time}\n')

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno)

        await asyncio.sleep(60)