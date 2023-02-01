import db
import inline_keybords
import helper
from User import UserDB
from config import PATH

dbUser = db.ManagerUsersDataBase()
dbPay = db.ManagerPayDataBase()

first_path = PATH + "/img/"

planets = ["Меркурий", "Венера", "Земля", "Марс", "Юпитер", "Сатурн"]
money_add = [25_000, 75_000, 250_000, 1_000_000, 4_200_000, 12_000_000]
sums = [5000, 15_000, 50_000, 200_000, 800_000, 3_000_000]
out_money = [10_000, 25_000, 50_000, 200_000, 1_000_000, 3_000_000]
count_ref = [0, 2, 4, 8, 16, 32]


def get_photo(planet):
    match int(planet):
        case 0:
            return 0, planets[0]
        case 1:
            return 1, planets[1]
        case 2:
            return 2, planets[2]
        case 3:
            return 3, planets[3]
        case 4:
            return 4, planets[4]
        case 5:
            return 5, planets[5]
    return None


async def get_launch(bot, user_id, loop):
    planet = await dbUser.get_planet(user_id, loop)

    user = (await get_user_on_planet(planet, user_id, loop))

    if user is None:
        link = 'space_gift_bot'
        gift_id = 5415272844
    else:
        link = user.link
        gift_id = int(user.user_id)

    level = int((await dbUser.get_step(user_id, loop))[0])
    level_text = f"Уровень {level}"
    path = ""
    more_text = ""
    active_text = ""
    text_planet = get_photo(planet[0])

    sum_gift = sums[text_planet[0]]
    text_planet = get_photo(planet[0])
    status = await dbUser.get_status(user_id, loop)

    text_status = " ❌"
    if status[0] == 1:
        text_status = " ✅"

    c_ref = count_ref[int(planet[0])] - int(await dbUser.get_activate_count_ref(user_id, loop))
    c_ref_op = await dbUser.get_activate_count_ref(user_id, loop)
    if await dbUser.get_activate_count_ref(user_id, loop) < count_ref[int(planet[0])]:
        if c_ref_op == 0:
            active_text = f"\n❗️ Чтобы попасть в очередь на планету {text_planet[1]} вам нужно пригласить " \
                         f"{c_ref} активных чел." \
                         f" или пополнить депозит на {c_ref * 10_000} RUB ❗️\n"
        else:
            active_text = f"\n❗️ Чтобы попасть в очередь на планету {text_planet[1]} вам нужно пригласить еще " \
                      f"{c_ref} активных чел." \
                      f" или пополнить депозит на {c_ref * 10_000} RUB ❗️\n"

    if level == 1 and status[0] == 0:
        path = first_path + f"{text_planet[1]}/В ожидании ({text_planet[1].lower()}).png"
        level_text = "В ожидании"
    elif status[0] == 1 and await dbUser.get_count_ref(user_id, loop) >= count_ref[int(planet[0])] and gift_id != user_id:
        path = first_path + f"{text_planet[1]}/В очереди ({text_planet[1].lower()}).png"
        level_text = "В очереди"
        ud = (await dbUser.get_planet(user_id, loop))[0]
        number = await get_queue(ud, user_id, loop)
        if type(number) is int:
            if number <= 10:
                more_text = f"\nНомер в очереди: {number}"

        more_text += f"\n\n🙌Поздравляем! Вы заняли место в очереди на подарки от новых участников на свой депозит!\n" \
            f"⚡️ Не жди очереди, начни увеличивать свой депозит уже сейчас и получать по 0,8% в день!\n\n"\
            f"1️⃣ Инвестируй в Space gift с собственных средств.\n" \
            f"2️⃣ Получай +5000р на депозит за каждого приглашенного реферала.\n" \
            f"3️⃣ Space gift начислит на депозит 10% от инвестиций реферала.\n\n" \
            f"НЕ ЖДИ. ДЕЙСТВУЙ 💪 ✅"

    elif status[0] == 1 and await dbUser.get_count_ref(user_id, loop) < count_ref[int(planet[0])] and gift_id != user_id:
        path = first_path + f"{text_planet[1]}/В очереди ({text_planet[1].lower()}).png"
        level_text = "В очереди"
        ud = (await dbUser.get_planet(user_id, loop))[0]
        number = await get_queue(ud, user_id, loop)
        if type(number) is int:
            if number <= 10:
                more_text = f"\nНомер в очереди: {number}"

        more_text += f"\n\n🙌Поздравляем! Вы заняли место в очереди на подарки от новых участников на свой депозит!\n" \
            f"⚡️ Не жди очереди, начни увеличивать свой депозит уже сейчас и получать по 0,8% в день!\n\n" \
            f"1️⃣ Инвестируй в Space gift с собственных средств.\n" \
            f"2️⃣ Получай +5000р на депозит за каждого приглашенного реферала.\n" \
            f"3️⃣ Space gift начислит на депозит 10% от инвестиций реферала.\n\n" \
            f"НЕ ЖДИ. ДЕЙСТВУЙ 💪 ✅"
    else:
        path += first_path + f"{text_planet[1]}/Шаг {int(level)} ({text_planet[1].lower()}).png"
        more_text += f"\n\nПоздравляем 🎉 На этом уровне новый участник подарит Вам + {sum_gift}₽ к Вашему депозиту! \n" \
                        f"До следующей планеты осталось {5 - int(await dbUser.get_step(user_id, loop))} подарка 🎁"

    text_plan = f"🪐 Движемся к планете: {text_planet[1]}"
    if text_planet[1] == planets[4] and level == 5:
        text_plan = "🎆 Поздравляем, вы долетели до Юпитера! Ваш полет завершен! 🎆"

    cd = await dbUser.get_amount_gift_money(user_id, loop)

    text = f"📆 Профиль создан: {await dbUser.get_date(user_id, loop)}\n" \
        f"🤖 Ваш ID: {user_id}\n\n"\
        f"👩‍🚀 Астронавт: {await dbUser.get_name(user_id, loop)}\n"\
        f"🎁 Системы дарения: {int(cd)} RUB\n"\
        f"{text_plan}\n"\
        f"👥 Лично приглашенных: {await dbUser.get_count_ref(user_id, loop)} чел. ({await dbUser.get_activate_count_ref(user_id, loop)}).\n"\
        f"🚀 Статус: {level_text} {text_status} {more_text}\n {active_text}"

    if status[0] == 0:
        text += "\n✅ Для того что бы активироваться в системе, и встать в «очередь» на " \
               f"подарки, Вам нужно сделать 🎁 подарок " \
               f"в размере {sums[text_planet[0]]} RUB астронавту @{link}."

    try:
        with open(path, "rb") as file:
            await bot.send_photo(
                chat_id=user_id,
                photo=file,
                caption=text,
                reply_markup=await inline_keybords.laucnh_inline(dbUser, user_id, loop)
            )
    except:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=await inline_keybords.laucnh_inline(dbUser, user_id, loop)
        )


async def get_user_on_merk(planet, user_id, loop):
    users = await dbUser.get_users_on_planet(planet, loop)
    users_on_planet = await helper.get_users(users, loop)

    active_users = helper.get_active_status_users(users_on_planet, int((await dbUser.get_planet(user_id, loop))[0]))
    active_users = [x for x in active_users if x.activate_date is not None]

    if len(active_users) > 0:
        max_step_user = max(active_users, key=lambda sort: sort.step)
        if int(max_step_user.step) == 1:
            active_users.sort(key=lambda sort: sort.activate_date)
            if len(active_users) > 0:
                return active_users[0]
            else:
                return None
        else:
            return max_step_user
    else:
        return None


async def get_user_on_planet(planet, user_id, loop):

    # if int(planet[0]) == 0:
    return await get_user_on_merk(planet, user_id, loop)

    # users = await dbUser.get_users_on_planet(planet, loop)
    # users_on_planet = await helper.get_users(users, loop)
    # active_users = helper.get_active_status_users(users_on_planet, int((await dbUser.get_planet(user_id, loop))[0]))
    #
    # if len(active_users) > 0:
    #     max_step_user = max(active_users, key=lambda sort: sort.step)
    #     if int(max_step_user.step) == 1:
    #         gifts_users = helper.active_users(active_users)
    #
    #         if len(active_users) > 0:
    #             gifts_users.sort(key=lambda sort: sort.count_ref, reverse=1)
    #             active_users.sort(key=lambda sort: sort.count_ref, reverse=1)
    #
    #             active_user = active_users[0]
    #             active = await dbUser.get_active(active_user.user_id, loop)
    #             if active != 1:
    #                 await dbUser.update_active(active_users[0].user_id, loop)
    #             if len(gifts_users) > 0:
    #                 for user in gifts_users:
    #                     if user.user_id != active_user.user_id:
    #                         await dbUser.reset_active(user.user_id, loop)
    #             return active_users[0]
    #         else:
    #             return None
    #     else:
    #         return max_step_user
    # else:
    #     return None


async def get_gift(user_id, gift_user: UserDB, loop):
    if user_id == gift_user.user_id:
        return False, "Нельзя дарить самому себе ❌"

    planet = await dbUser.get_planet(user_id, loop)
    text_planet = get_photo(planet[0])

    sum_gift = sums[text_planet[0]]
    #system_gift = await dbUser.get_amount_gift_money(user_id, loop)

    await dbUser.get_gift(gift_user.user_id, user_id, sum_gift, loop)
    #await dbUser.add_amount_gift_money(gift_user.user_id, sum_gift, loop)
    #await dbUser.add_money(gift_user.user_id, sum_gift, loop)
    #await dbUser.set_now_depozit(user_id, sum_gift, loop)
    #await dbUser.remove_money(user_id, sum_gift, loop)
    now_dep = await dbUser.get_now_depozit(gift_user.user_id, loop)

    if now_dep > 0:
        await dbUser.add_now_dep(gift_user.user_id, now_dep, loop)
        #await dbUser.add_amount_gift_money(gift_user.user_id, now_dep, loop)
        #await dbUser.set_now_depozit(gift_user.user_id, 0, loop)

    if int(planet[0]) > 0:
        amount = await dbUser.get_amount_gift_money(user_id, loop)
        if amount >= sum_gift:
            await dbUser.remove_amount_gift_money(user_id, sum_gift, loop)
        else:
            return False, "Недостаточно денег"
    else:
        await dbUser.remove_depozit(sum_gift, user_id, loop)

    return True, f"Вы успешно подарили @{gift_user.link} {sum_gift} RUB", sum_gift


async def gift(bot, user: UserDB, loop):

    planet = await dbUser.get_planet(user.user_id, loop)
    path = first_path

    astr = await get_user_on_planet(user.planet, user.user_id, loop)
    if astr is None:
        link = "@space_gift_bot"
    elif astr.link == (await dbUser.get_name(user.user_id, loop)):
        link = "@space_gift_bot"
    else:
        link = f"@{astr.link}"
    text_planet = get_photo(planet[0])
    text_planet_next = get_photo(int(planet[0]) + 1)
    if text_planet_next is None:
        text_planet_next = (5, 'Сатурн')

    sum_add = money_add[text_planet[0]]
    sum_gift = sums[text_planet[0]]
    path += f"{text_planet[1]}/Поздравляем. {text_planet[1]}.png"

    await dbUser.gift(user.user_id, (sum_add - out_money[text_planet[0]]), out_money[text_planet[0]],
                      (sum_add - out_money[text_planet[0]] - sum_gift), sum_gift * 4, loop)
    #await dbUser.add_money(user.user_id, (sum_add - out_money[text_planet[0]]), loop)
    #await dbUser.add_gift_money(user.user_id, out_money[text_planet[0]], loop)
    #await dbUser.add_amount_gift_money(user.user_id, (sum_add - out_money[text_planet[0]] - sum_gift), loop)
    #await dbUser.change_first_dep(user.user_id, 0, loop)

    now_dep = await dbUser.get_now_depozit(user.user_id, loop)
    if now_dep > 0:
        await dbUser.reset_now_dep_for_new_planet(user.user_id, now_dep, loop)
        # await dbUser.add_amount_gift_money(user.user_id, now_dep, loop)
        # await dbUser.remove_now_depozit(user.user_id, now_dep, loop)

    await dbUser.reset_activate_date(user.user_id, loop)

    text = f"Поздравляем! 🎉 вы теперь на планете {text_planet[1]}! 🙌\n\n" \
           f"👩‍🚀 На ваш депозит было подарено  🎁 +{sum_add} RUB, " \
           f"из них Вы можете вывести {out_money[text_planet[0]]} RUB \n( с 20% комиссией )\n\n" \
           f"Чтобы взлететь 🚀 на планету {text_planet_next[1]}, нужно остаток " \
           f"Вашего депозита подарить Астронавту {link}"

    with open(path, "rb") as file:
        try:
            await bot.send_photo(
                chat_id=user.user_id,
                photo=file,
                caption=text,
            )
        except:
            pass


async def get_queue(planet, user_id, loop):
    users = await dbUser.get_users_on_planet(planet, loop)
    users_on_planet = await helper.get_users(users, loop)
    active_users = helper.get_active_status_users(users_on_planet, int((await dbUser.get_planet(user_id, loop))[0]))
    active_users = [x for x in active_users if x.activate_date is not None]

    if len(active_users) > 0:
        active_users.sort(key=lambda sort: sort.activate_date)
    index = 1

    for user in active_users:
        if int(user.user_id) == user_id:
            return index
        index += 1
    return "Недостаточно рефералов, для вступления в очередь"


async def check_active(planet, user_id, loop):
    users = await dbUser.get_users_on_planet(planet, loop)
    users_on_planet = await helper.get_users(users, loop)
    active_users = helper.get_active_status_users(users_on_planet, int((await dbUser.get_planet(user_id, loop))[0]))
    gifts_users = helper.active_users(active_users)

    if len(active_users) > 0:
        gifts_users.sort(key=lambda sort: sort.count_ref, reverse=1)
    if len(gifts_users) > 0:
        if user_id != gifts_users[0].user_id:
            await dbUser.reset_active(user_id, loop)


async def get_amount_gift_money(user_id, loop):
    planet = int((await dbUser.get_planet(user_id, loop))[0])
    step = int(await dbUser.get_step(user_id, loop))
    money = 0

    if planet == 0:
        if (await dbUser.get_status(user_id, loop))[0] == 1:
            money += 5000
            if step > 1:
                for i in range(1, step):
                    money += 5000
                return money
        return money

    for temp in range(1, planet+1):
        money += sums[temp - 1] + money_add[temp - 1]
    if step > 1:
        for i in range(1, step):
            money += sums[planet]
        return money
    return 0

