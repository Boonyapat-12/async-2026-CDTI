import asyncio

async def compute():
    return 42

async def main():
    task = asyncio.create_task(compute())
    # Line X
    res = task.result
    print(res)

asyncio.run(main())
