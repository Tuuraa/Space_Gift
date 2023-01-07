from db import ManagerClonesDataBase, ManagerUsersDataBase
import helper
from User import UserDB


dbClones = ManagerClonesDataBase()
dbUser = ManagerUsersDataBase()


async def create_clones(money: int, loop):
    count = int(money / 5000)

    for clone in range(0, count):
        await dbClones.create_clone(loop)


async def get_active_user(users: list):
    for user in users:
        if user.active == 1:
            return user


async def update_active_user(loop):
    users = await dbUser.get_users_on_planet(0, loop)
    users_on_planet = await helper.get_users(users, loop)
    active_users = helper.get_active_status_users(users_on_planet, 0)

    gifts_users = helper.active_users(active_users)

    if len(active_users) > 0:
        gifts_users.sort(key=lambda sort: sort.count_ref, reverse=1)
        active_users.sort(key=lambda sort: sort.count_ref, reverse=1)

        active_user = active_users[0]
        active = await dbUser.get_active(active_user.user_id, loop)
        if active != 1:
            await dbUser.update_active(active_users[0].user_id, loop)
        if len(gifts_users) > 0:
            for user in gifts_users:
                if user.user_id != active_user.user_id:
                    await dbUser.reset_active(user.user_id, loop)