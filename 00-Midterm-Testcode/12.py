import asyncio

async def worker(n):
    return n * 2

async def main():
    coros = [worker(1), worker(2), worker(3)]
    res = await asyncio.gather(*coros)
    print(res)

asyncio.run(main())
