import asyncio

async def fail_task():
    await asyncio.sleep(0.1)
    raise ValueError("Error in fail_task")

async def pass_task():
    await asyncio.sleep(0.2)
    return "OK"

async def main():
    try:
        res = await asyncio.gather(fail_task(), pass_task())
        print(res)
    except ValueError as e:
        print(f"Caught : {e}")

asyncio.run(main())
