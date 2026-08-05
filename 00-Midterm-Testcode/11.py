import asyncio

async def bad_coro():
    print("Starting...")

    asyncio.sleep(1)
    print("Finished...")

async def main():
    await bad_coro()

asyncio.run(main())
