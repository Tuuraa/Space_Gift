import asyncio
from back_work import worker
from Percent import worker_percent
from back_clones import worker_clones
from jump import worker_jump
from back_verify_balance import worker_verify_balance
from db import ConfigDBManager
import threading


async def main():
    loop = asyncio.new_event_loop()
    print('start')
    await asyncio.gather(
        worker(loop),
        worker_percent(loop),
        worker_clones(loop),
        #worker_jump(loop),
        worker_verify_balance(loop),
    )
    print('end')


if __name__ == '__main__':
    asyncio.run(main())
