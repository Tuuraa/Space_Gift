from db import ManagerResetSystem
import asyncio


async def main():
    dbSystem = ManagerResetSystem()
    loop = asyncio.new_event_loop()

    await dbSystem.reset_data(loop)
    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
