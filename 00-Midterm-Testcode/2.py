import asyncio

async def task_a():
    print("A1")
    await asyncio.sleep(0.1)
    print("A2")

async def task_b():
    print("B1")
    print("B2")

async def main():
    t1 = asyncio.create_task(task_a())
    t2 = asyncio.create_task(task_b())
    await t1
    await t2

asyncio.run(main())
