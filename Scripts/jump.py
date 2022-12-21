import asyncio
import sys

import db
import helper
import logic


dbUser = db.ManagerUsersDataBase()


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

                        else:
                            await bot.send_message(
                                user.user_id,
                                "Вы закончили игру"
                            )
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            config = db.ConfigDBManager().get()

            await bot.send_message(
                config.errors_group_id,
                f'{exc_type}, {exc_obj}, {exc_tb} from back_clones'
            )
        await asyncio.sleep(60)