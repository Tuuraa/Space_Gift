from aiogram import Bot

from User import UserDB
from db import ManagerUsersDataBase, ConfigDBManager
import logic


dbUser = ManagerUsersDataBase()


async def create_ref(amount, user_id, loop):
    count = int(amount/10_000)
    for i in range(count):
        await dbUser.update_count_ref(user_id, loop)


def clear_repeat(users: list):
    return list(set(users))


def cancel_unnecessary(users: list):
    temp_list = []

    for item in users:
        if item[6] == "WAIT_PAYMENT":
            temp_list.append(item)

    return temp_list


def get_users(users: list):
    result = []

    for user in users:
        result.append(UserDB(user[3], user[7], user[1], user[5], user[8], user[11], user[12], user[14], user[15], user[16], user[20]))
    return result


def get_active_status_users(users: list, planet):
    result = []
    count = logic.count_ref[planet]

    for user in users:
        if user.status == 1 and user.count_ref >= count:
            result.append(user)
    return result


def get_current_user(users: list, id: int):
    for user in users:
        if user.user_id == id:
            return user


def users_equals_planet(users: list, user: UserDB):
    result = []

    for item in users:
        if item.planet == user.planet:
            result.append(item)
    return result


def active_users(users: list):
    result = []

    for item in users:
        if item.active == 1:
            result.append(item)
    return result


def create_new_block(users, user_id, db: ManagerUsersDataBase, loop):
    for user in users:
        db.new_block_user(user.user_id, user_id, loop)


def clear_none(users: list):
    result = []
    for user in users:
        if user[0] is not None:
            result.append(user)
    return result


def get_have_jump_users(users: list):
    result = []
    for user in users:
        if user.jump == 1:
            result.append(user)

    return result


def clear_crypt_requests(pays: list):
    result = []
    for pay in pays:
        if pay[5] != "CANCELED" and pay[5] != "OPERATION_COMPLETED":
            result.append(pay)

    return result


async def send_message_safe(bot, tel_id, text, reply_markup=None):
    try:
        await bot.send_message(tel_id, text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception:
        pass


async def test():
    configCl = ConfigDBManager.get()

    API_TOKEN = configCl.api_bot  # Считывание токена
    bot = Bot(token=API_TOKEN)
    await send_message_safe(bot, 855151774, "test")


async def db_reset(loop):
    configCl = ConfigDBManager.get()

    API_TOKEN = configCl.api_bot
    bot = Bot(token=API_TOKEN)

    users = await dbUser.get_users(loop)
    for user in users:
        await dbUser.reset_data(user, loop)
        await send_message_safe(
            bot,
            user,
            "Все участники Space gift 🎁 \n"
                  "система дарения готова к повторной активации!!! \n"
                  "Успейте встать в очередь на подарки, одними из первых 🙌"
        )
