from db import ManagerUsersDataBase, ConfigDBManager
import asyncio
from aiogram import Bot
import asyncio
from aiogram import types

configCl = ConfigDBManager.get()

API_TOKEN = configCl.api_bot  # Считывание токена
bot = Bot(token=API_TOKEN)


async def main(loop):
    dbSystem = ManagerUsersDataBase()
    user_ids = await dbSystem.get_users(loop)
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("Да", callback_data="reset_system_yes"), types.InlineKeyboardButton("Нет", callback_data="reset_system_no"))

    for tg_id in user_ids:
        try:
            msg = await bot.send_message(tg_id[0], 'Планируете ли вы зайти в систему дарения повторно 1 февраля в 10:00 утра?\n\nЕсли «Да», то вы сможете стать одним из первых в системе дарения  и получить преимущество в 5 минут, перед новыми участниками 1 числа в 9:55\n\nЕсли «Нет» тогда вы сможете перевести свои 5000₽ в инвестиции и продолжите получать свои  дивиденды.',
                                   reply_markup=kb)
        except Exception as e:
            print(e)
            pass
    print(3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
