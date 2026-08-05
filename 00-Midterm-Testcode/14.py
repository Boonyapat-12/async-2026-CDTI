import asyncio
async def bad_task():
    await asyncio.sleep(1)
    raise ValueError("Something went wrong!")

async def good_task():
    await asyncio.sleep(2)
    return "Success"

async def main():
    results = await asyncio.gather(bad_task(), good_task(), return_exceptions=True)
    print(results)

asyncio.run(main())