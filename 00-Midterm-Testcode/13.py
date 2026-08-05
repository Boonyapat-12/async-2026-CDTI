import asyncio
import time

async def worker(delay):
    await asyncio.sleep(delay)
    return delay


async def main():
    start = time.time()
    res = await asyncio.gather(worker(2), worker(3), worker(1))
    print(f"Time: {round(time.time() - start)}, Res: {res}")

asyncio.run(main())
