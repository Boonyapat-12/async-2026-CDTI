import asyncio

async def worker(n):
    await asyncio.sleep(n)
    if n == 2:
        raise ValueError("Failed on 2")
    return n

async def main():
    tasks = [asyncio.create_task(worker(i)) for i in [1, 2, 3]]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    print(f"Done: {len(done)}, Pending: {len(pending)}")

asyncio.run(main())
