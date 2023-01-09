async def is_user_subbed(bot, group_id: int, user_id: int) -> bool:
    try:
        info = await bot.get_chat_member(group_id, user_id)
        if info.status == 'left' or info.status == 'kicked':
            return False
        return True
    except Exception:
        return False
