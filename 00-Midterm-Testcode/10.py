import asyncio

async def worker():
    print("Working...")

async def main():
    task = asyncio.create_task(worker())
    task.add_done_callback(lambda t: print("Task Finished!"))
    await task

asyncio.run(main())
