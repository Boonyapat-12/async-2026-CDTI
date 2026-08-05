import asyncio

async def compute(val):
    return val * 2

async def main():
    coro = compute(10)
    res = await coro
    print(res)

asyncio.run(main())
