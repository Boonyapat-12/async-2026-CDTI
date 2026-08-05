import asyncio

async def long_running_task():
    try:
        await asyncio.sleep(10)  # Simulate a long-running task
    except asyncio.CancelledError:
        print("Cleaning up...")
        await asyncio.sleep(1)  # Simulate cleanup time
        print("Cleanup done")

async def main():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(0.1)  # Let the task run for a bit
    task.cancel()  # Cancel the task
    await task

asyncio.run(main())
