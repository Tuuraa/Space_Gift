import asyncio
import sys

import db
import helper
import logic


dbUser = db.ManagerUsersDataBase()


async def send_message_safe(bot, tel_id, text, reply_markup=None):
    try:
        await bot.send_message(tel_id, text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception:
        pass


async def worker_jumps(bot, loop):
    while True:
        try:
            for planet_number in range(0, 5):
                users = helper.get_users(await dbUser.get_users_on_planet(planet_number, loop))
                jump_users = helper.get_have_jump_users(users)

                for user in jump_users:
                    ref_users = helper.get_users(await dbUser.get_referrer_of_user(user.user_id, loop)) #Количество рефералов у user
                    len_ref_users = len(ref_users)
                    count_ref = 0  #Количество рефералов у реферала нашего user

                    for ref_user in ref_users: #Прoходимся по рефералам нашего реферала user
                        if await dbUser.ref_count(ref_user.user_id, loop) >= 5:
                            count_ref += 1

                    if count_ref == len_ref_users:
                        await logic.gift(bot, user, loop)
                        if int(user.planet) < 5:
                            await dbUser.reset_jump(user.user_id, loop)
                            await dbUser.reset_step(user.user_id, loop)
                            await dbUser.change_status(user.user_id, 0, loop)
                            await dbUser.update_planet(user.user_id, loop)
                            await logic.check_active(int(user.planet) + 1, user.user_id, loop)
                            await send_message_safe(
                                bot,
                                user.user_id,
                                "🎆 Поздравляем 🎆 с помощью системы сетивиков вы попали на новую планету!"
                            )

                        else:
                            await send_message_safe(
                                bot,
                                user.user_id,
                                "Вы закончили игру"
                            )
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            config = db.ConfigDBManager().get()

            await bot.send_message(
                config.errors_group_id,
                f'{exc_type}, {exc_obj}, {exc_tb} from jump'
            )
        await asyncio.sleep(60)