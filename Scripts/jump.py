import asyncio

import db
import helper
import logic


dbUser = db.ManagerUsersDataBase()


async def worker_jumps(bot):
    while True:
        for planet_number in range(0, 5):
            users = helper.get_users(dbUser.get_users_on_planet(planet_number))
            jump_users = helper.get_have_jump_users(users)
            for user in jump_users:
                ref_users = helper.get_users(dbUser.get_referrer_of_user(user.user_id)) # Количество рефералов у user
                len_ref_users = len(ref_users)
                count_ref = 0  # Количество рефералов у реферала нашего user
                for ref_user in ref_users: # Прoходимся по рефералам нашего реферала user
                    if dbUser.ref_count(ref_user.user_id) >= 5:
                        count_ref += 1

                if count_ref == len_ref_users:
                    await logic.gift(bot, user)
                    if int(user.planet) < 5:
                        dbUser.reset_jump(user.user_id)
                        dbUser.reset_step(user.user_id)
                        dbUser.change_status(user.user_id, 0)
                        dbUser.update_planet(user.user_id)
                        await logic.check_active(int(user.planet) + 1, user.user_id)

                    else:
                        await bot.send_message(
                            user.user_id,
                            "Вы закончили игру"
                        )

        await asyncio.sleep(3600)