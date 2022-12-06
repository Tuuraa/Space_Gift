from aiogram import types
from random import randint
from db import ManagerUsersDataBase
import PayManager


def get_start_inline():
    return types.InlineKeyboardMarkup().\
        add(types.InlineKeyboardButton("Зарегистрироваться", callback_data="login"))


def accept_inline():
    return types.InlineKeyboardMarkup().\
        add(types.InlineKeyboardButton("✅ Принять соглашение Space Gift", callback_data="capcha"))


async def create_capcha(bot, id):
    value_first, value_second = randint(10, 50), randint(10, 50)
    sum = value_first + value_second

    sum_but = types.InlineKeyboardButton(str(sum), callback_data="right")

    row, column = randint(0, 1), randint(0, 2)
    markups = types.InlineKeyboardMarkup()

    for i in range(0, 2):
        list_buttons = []
        while len(list_buttons) != 3:
            rund = randint(min(value_first, value_second), sum * 2)
            if rund != sum:
                list_buttons.append(types.InlineKeyboardButton(str(rund), callback_data="except"))
        if i == row:
            list_buttons[column] = sum_but
        markups.row(list_buttons[0], list_buttons[1], list_buttons[2])

    markups.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))

    await bot.send_message(id, f"Чтобы принять соглашение Space Gift и \n"
                           "политику конфиденциальности"
                           "\nвыберите правильный ответ.\n"
                            "👉 Сколько будет:"
                           f"\n{value_first} + {value_second} = ?",
                           reply_markup=markups)


def profile_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add().row(types.KeyboardButton("🚀 Взлёт"), types.KeyboardButton("📝 О проекте"))
    markup.add().row(types.KeyboardButton("💳 Кошелёк"), types.KeyboardButton("🌑 Space Money"))
    markup.add().row(types.KeyboardButton("🔧 Инструменты"), types.KeyboardButton("⚙ Техническая поддержка"))
    markup.add().row("Тестовое пополнение", "Удалить аккаунт", "Тестовые клоны")

    return markup


def sure_login():
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton("Да ✅", callback_data="yes_ans"),
        types.InlineKeyboardButton("Нет ❌", callback_data="no_ans")
    )


def add_money():
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton("➕ Пополнить", callback_data="add_money"),
        types.InlineKeyboardButton("➖ Вывести", callback_data="remove_money")
    )


def calculate():
    return types.InlineKeyboardMarkup()\
        .add(types.InlineKeyboardButton("Рассчитать снова", callback_data="calculate"))


def back():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.InlineKeyboardButton("Отменить платеж", callback_data="calculate"))


def takeoff():
    return types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("💸 Пополнить", callback_data="set_money_for_gift")
        )


def get_gift():
    return types.InlineKeyboardMarkup().\
        add(types.InlineKeyboardButton("▪ Банковская карта RUB", callback_data="payrement_bank")).\
        add(types.InlineKeyboardButton("▪ Криптовалюта", callback_data="payrement_crypt"))


def get_crypt_types():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("BTC", callback_data="btc_trans"),
                                            types.InlineKeyboardButton("LTC", callback_data="ltc_trans"),
                                            types.InlineKeyboardButton("ETH", callback_data="eth_trans"))


async def banks_payment():

    banks: list = await PayManager.get_banks()
    inline = types.InlineKeyboardMarkup()

    for bank in banks[1:]:
        inline.add(types.InlineKeyboardButton(str(bank).title(), callback_data=bank))

    return inline


def cancel_pay():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Отменить заявку", callback_data="cancel_pay"))


def get_about_project():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton("О Space Gift"),
        types.KeyboardButton("O Space Money"),
        types.KeyboardButton("Что такое арбитраж"),
        types.KeyboardButton("⬅ Вернуться")
    )


def get_tools():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton("Рассчитать пассив"),
        types.KeyboardButton("Реферальная система"),
        types.KeyboardButton("Презентация"),
        types.KeyboardButton("⬅ Вернуться")
    )


def get_link_to_space_money():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="Ссылка на сайт", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    )


def get_wallet_inline():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("➕ Пополнить", callback_data="add_money"),
        types.InlineKeyboardButton("➖ Вывести", callback_data="remove_money"))


def get_double_dep():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Удвоить депозит", callback_data="get_double_deposit")
    )


def get_transfer_inline():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Зарегистрироваться", url="https://t.me/Financespacemoney_bot"),
        types.InlineKeyboardButton("Код", callback_data="code_for_transfer_money")
    )


def get_inline_for_withdraw():
    return types.InlineKeyboardMarkup().\
        add(types.InlineKeyboardButton("▪ Банковская карта RUB", callback_data="withdraw_payrement_bank")).\
        add(types.InlineKeyboardButton("▪ Криптовалюта", callback_data="withdraw_payrement_crypt"))


def get_admi_crypt_type():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add().row("BTC", "LTC", "ETH")
    return markup


def get_gift_ok_inline():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Вперед", callback_data="ok_gift"))


def get_full_users(db: ManagerUsersDataBase):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    users = db.get_full_users_name()
    for item in range(0, len(users), 2):
        if item + 2 <= len(users):
            markup.row(types.KeyboardButton(users[item][0]), users[item+1][0])
        else:
            markup.add(types.KeyboardButton(users[item][0]))
    markup.add(types.KeyboardButton("Назад"))
    return markup


def cancel_trans_money():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("Отменить")


def laucnh_inline(db, user_id):

    mark = types.InlineKeyboardMarkup()
    status = db.get_status(user_id)

    if status[0] == 0:  #🎁 Сделать подарок
        return mark.add(types.InlineKeyboardButton("🎁 Сделать подарок", callback_data="get_gift"))
    else:
        return types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("💸 Пополнить баланс", callback_data="set_money_for_gift"))\
            .add(types.InlineKeyboardButton("🙋‍♂ Пригласить участника", callback_data="invite_new_person")
        )


def inform_pers():
    return types.InlineKeyboardMarkup().\
        add(types.InlineKeyboardButton("💬 Осведомить участника", callback_data="inform_pers"))

