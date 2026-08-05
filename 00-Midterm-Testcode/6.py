import asyncio

async def task1():
    await asyncio.sleep(0.2)
    return "T1"

async def task2():
    await asyncio.sleep(0.1)
    return "T2"

async def main():
    done, pending = await asyncio.wait([asyncio.create_task(task1()), asyncio.create_task(task2())], return_when=asyncio.ALL_COMPLETED)
    print(f"Done count: {len(done)}, Pending count: {len(pending)}")

asyncio.run(main())
