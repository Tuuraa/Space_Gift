import db
import helper
import logic

dbUser = db.ManagerUsersDataBase()


async def main(planet, money, gift, loop):
    sys_gift = money
    gift_amount = gift
    users = await db.get_users_on_planet(planet, loop)
    users_on_planet = await helper.get_users(users, loop)
    active_users = helper.get_active_status_users(users_on_planet, 1)

    while sys_gift >= 0:
        for user in active_users:
            if user.step < 5:
                await db.update_step(user.user_id, loop)
            if int(step) == 5:
                if int(await db.get_count_ref(user.user_id, loop)) >= logic.count_ref[int(user.planet)]:
                    await logic.gift(bot, user, loop)
                    if int(user.planet) < 5:
                        await db.update_new_step(user.user_id, loop)
        sys_gift -= gift_amount
