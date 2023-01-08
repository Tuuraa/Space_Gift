import asyncio
import db
import pytz
import datetime

ids = [77414227, 2079216243, 345937641, ]


async def main(loop):
    connection, cursor = await db.async_connect_to_mysql(loop)
    async with connection.cursor() as cursor:
        await cursor.execute('select `user_id` from `users`')
        users = await cursor.fetchall()

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

        for user in users:
            await cursor.execute('select count(*) from `users` where `referrer_id` = %s and `refgift` = 1', (user,))
            result = await cursor.fetchall()
            await cursor.execute('update `users` set `activate_ref_count` = %s where '
                                 '`user_id` = %s', (result, user, ))
            await cursor.execute('update `users` set `activate_date` = %s where '
                                 '`user_id` = %s', (date_time_now, user,))
            await connection.commit()

        for id in ids:
            await cursor.execute('update `users` set `activate_ref_count` = `activate_ref_count` + %s  where '
                                 '`user_id` = %s', (1, id,))
            await connection.commit()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.run(main(loop))