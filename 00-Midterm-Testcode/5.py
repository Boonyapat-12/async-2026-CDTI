import asyncio

async def job():
    try:
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("Cancelled internal")
        raise

async def main():
    task = asyncio.create_task(job())
    await asyncio.sleep(1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Cancelled external")


asyncio.run(main())
