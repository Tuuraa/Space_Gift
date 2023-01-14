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
async def count_total_referrals_by_user(user_id, to_level, loop):
    curr_referrals = [user_id]

    count = 0
    for _ in range(to_level):
        curr_referrals = await dbUser.get_ref_users_in(curr_referrals, loop)
        if len(curr_referrals) == 0:
            break
        count += len(curr_referrals)
    return count


async def count_total_active_referrals_by_user(user_id, to_level, loop):
    curr_referrals = [user_id]

    count = 0
    for _ in range(to_level):
        curr_referrals = await dbUser.get_ref_users_in(curr_referrals, loop)
        if len(curr_referrals) == 0:
            break
        for ref_id in curr_referrals:
            if not(await dbUser.is_first_user_topup(ref_id, loop)):
                count += 1
    return count