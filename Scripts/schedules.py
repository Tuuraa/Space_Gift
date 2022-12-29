from db import ManagerUsersDataBase, ConfigDBManager
from aiogram import Bot


async def send_message_safe(bot, tel_id, text, reply_markup=None):
    try:
        await bot.send_message(tel_id, text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception:
        pass


async def db_reset(loop):
    configCl = ConfigDBManager.get()

    API_TOKEN = configCl.api_bot
    bot = Bot(token=API_TOKEN)
    dbUser = ManagerUsersDataBase()

    users = ConfigDBManager.get_all_users()
    for user in users:
        await dbUser.reset_data(user, loop)
        await send_message_safe(
            bot,
            user,
            "Все участники Space gift 🎁 \n"
            "система дарения готова к повторной активации!!! \n"
            "Успейте встать в очередь на подарки, одними из первых 🙌"
        )
    print('DONE')

if __name__ == "__main__":
    db_reset()