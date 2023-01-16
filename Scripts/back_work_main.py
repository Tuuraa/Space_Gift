import asyncio
from back_work import worker
from Percent import worker_percent
from back_clones import worker_clones
from jump import worker_jumps
import threading


if __name__ == '__main__':
    loops = [asyncio.new_event_loop() for i in range(0, 4)]

    thread1 = threading.Thread(target=loops[0].run_forever)
    thread1.start()
    asyncio.run_coroutine_threadsafe(worker(loops[0]), loops[0])

    thread2 = threading.Thread(target=loops[1].run_forever)
    thread2.start()
    asyncio.run_coroutine_threadsafe(worker_percent(loops[1]), loops[1])

    thread3 = threading.Thread(target=loops[2].run_forever)
    thread3.start()
    asyncio.run_coroutine_threadsafe(worker_clones(loops[2]), loops[2])

    thread4 = threading.Thread(target=loops[3].run_forever)
    thread4.start()
    asyncio.run_coroutine_threadsafe(worker_jumps(loops[3]), loops[3])
