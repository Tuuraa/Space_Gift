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
            msg = await bot.send_message(tg_id[0], 'Планируете ли вы заходить в систему повторно?',
                                   reply_markup=kb)
        except Exception as e:
            print(e)
            pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
