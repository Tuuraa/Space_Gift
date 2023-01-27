from aiogram import types
from random import randint
from db import ManagerUsersDataBase
import PayManager


def get_start_inline():
    return types.InlineKeyboardMarkup(). \
        add(types.InlineKeyboardButton("Зарегистрироваться", callback_data="login"))


def accept_inline():
    return types.InlineKeyboardMarkup(). \
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
    markup.add().row("🚀 Взлёт", "📝 О проекте")
    markup.add().row("💻 Инвестиции", "🔧 Инструменты")
    markup.add().row("💳 Кошелёк", "⚙ Тех. поддержка")

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
    return types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton("Рассчитать снова", callback_data="calculate"))


def back():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.InlineKeyboardButton("Отменить платеж", callback_data="calculate"))


def takeoff():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("💸 Пополнить", callback_data="set_money_for_gift")
    )


def get_gift():
    return types.InlineKeyboardMarkup(). \
        add(types.InlineKeyboardButton("▪ Банковская карта RUB", callback_data="payrement_bank")). \
        add(types.InlineKeyboardButton("▪ Криптовалюта", callback_data="payrement_crypt"))


def get_crypt_types():
    return types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton("BTC", callback_data="btc_trans"),
             types.InlineKeyboardButton("LTC", callback_data="ltc_trans")).add(
        types.InlineKeyboardButton("ETH", callback_data="eth_trans"),
        types.InlineKeyboardButton("USDT", callback_data="usdt_trans"))


async def banks_payment():
    banks: list = await PayManager.get_banks()
    inline = types.InlineKeyboardMarkup()

    for bank in banks[1:]:
        inline.add(types.InlineKeyboardButton(str(bank).title(), callback_data=bank))

    return inline


def cancel_pay():
    return types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton("❌ Отменить заявку", callback_data="cancel_pay"))


def get_about_project():
    reply = types.ReplyKeyboardMarkup(resize_keyboard=True)

    reply.row(
        types.KeyboardButton("🚀 Инвестиции в Space Gift"),
        types.KeyboardButton("💫 Инвестиции в Space Money")
    )

    reply.row(
        types.KeyboardButton("🎁 Система дарения"),
        # types.KeyboardButton("🤖 Система клонов")
    )

    reply.row(
        types.KeyboardButton("🤑 Вознаграждение за приглашение"),
        types.KeyboardButton("🤑 Вознаграждение за пополнение реферала")
    )

    reply.row(
        types.KeyboardButton("👥 Условия для сетевиков")
    )

    # reply.row(
    # types.KeyboardButton("О Space Gift"),
    # types.KeyboardButton("O Space Money")
    # )

    reply.row(
        types.KeyboardButton("⬅ Вернуться")
    )

    return reply


def get_tools():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton("💰 Калькулятор"),
        types.KeyboardButton("👥 Реферальная ссылка"),
        types.KeyboardButton("📄 Презентация"),
        types.KeyboardButton("⬅ Вернуться")
    )  # .add().row("Тестовое пополнение", "Удалить аккаунт")


def get_link_to_space_money():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="Ссылка на сайт", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    )


def get_wallet_inline():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🪙 Реинвестировать", callback_data="reinvest")).add(
        types.InlineKeyboardButton("➖ Вывести дивиденды", callback_data="remove_money"))


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
    return types.InlineKeyboardMarkup(). \
        add(types.InlineKeyboardButton("▪ Банковская карта RUB", callback_data="withdraw_payrement_bank")). \
        add(types.InlineKeyboardButton("▪ Криптовалюта", callback_data="withdraw_payrement_crypt"))


def get_admi_crypt_type():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add().row("BTC", "LTC", "ETH")
    return markup


def get_gift_ok_inline():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 Написать", callback_data="ok_gift"))


def cancel_trans_money():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("Отменить")


async def laucnh_inline(db: ManagerUsersDataBase, user_id, loop):
    mark = types.InlineKeyboardMarkup()
    status = await db.get_status(user_id, loop)

    if status[0] == 0:  # 🎁 Сделать подарок
        return mark.add(types.InlineKeyboardButton("🎁 Сделать подарок", callback_data="get_gift"))
    else:
        reply = types.InlineKeyboardMarkup()
        now_dep = await db.get_now_depozit(user_id, loop)
        if now_dep > 0:
            reply.add(types.InlineKeyboardButton("🎁 Получить подарок от Space Gift",
                                                 callback_data="get_gift_from_space_gift"))

        reply.add(types.InlineKeyboardButton("💸 Пополнить баланс", callback_data="set_money_for_gift")).add(
            types.InlineKeyboardButton("🙋‍♂ Пригласить участника", callback_data="invite_new_person"))
        return reply


def inform_pers():
    return types.InlineKeyboardMarkup(). \
        add(types.InlineKeyboardButton("💬 Осведомить участника", callback_data="inform_pers"))


def invest_buttons():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("➕ Инвестировать", callback_data="add_money")).add(
        types.InlineKeyboardButton("🪙 Реинвестировать", callback_data="reinvest_invest")).add(
        types.InlineKeyboardButton("➖ Вывести дивиденды", callback_data="remove_money_0_05")).add(
        types.InlineKeyboardButton("🌟 Вывести инвестиции", callback_data="remove_money_invest")).add(
        types.InlineKeyboardButton("💫 Инвестиции в Space money", callback_data="link_to_space_money"))
    # .add(types.InlineKeyboardButton("🤖 Система клонов", callback_data="system_clones"))


def get_link_space_money():
    return types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton("💫 Перейти на сайт Space money", url="spacemoney.space"))
