from db import ManagerUsersDataBase


dbUser = ManagerUsersDataBase()


async def is_user_subbed(bot, group_id: int, user_id: int) -> bool:
    try:
        info = await bot.get_chat_member(group_id, user_id)
        if info.status == 'left' or info.status == 'kicked':
            return False
        return True
    except Exception:
        return False


# function that counts the number of nested referrals
async def count_total_referrals_by_user(user_id, to_level, loop) -> dict:
    curr_referrals = [user_id]

    count = 0
    activated_count = 0
    for _ in range(to_level):
        db_answer = await dbUser.get_ref_users_in(curr_referrals, loop)
        curr_referrals = list(map(lambda x: x[0], db_answer))

        if len(curr_referrals) == 0:
            break
        count += len(curr_referrals)

        for user in db_answer:
            if int(user[1]) != 0 or int(user[2]) != 0 or int(user[3]) != 0:
                activated_count += 1

    return {
        'total': count,
        'activated': activated_count
    }