import asyncio

async def worker(n):
    await asyncio.sleep(n)
    return n

async def main():
    task = [asyncio.create_task(worker(i)) for i in [3 ,1 ,2]]
    done, pending = await asyncio.wait(task, return_when=asyncio.FIRST_COMPLETED)
    print([t.result() for t in done])

asyncio.run(main())
