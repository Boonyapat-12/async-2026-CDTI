import asyncio
async def my_coro():
    print("A")
    await asyncio.sleep(0)
    print("B")

async def main():
    task = asyncio.create_task(my_coro())
    print("C")
    await task

asyncio.run(main())