import asyncio
import time

async def worker(n):
    await asyncio.sleep(0.5)
    return n * 10

async def main():
    start = time.time()
    tasks = [asyncio.create_task(worker(i)) for i in range(1, 4)]
    for t in tasks:
        res = await t
        print(f"Time: {round(time.time() - start)}")
        print(res, end=" ")


asyncio.run(main())
