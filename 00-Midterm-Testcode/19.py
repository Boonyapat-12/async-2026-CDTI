import asyncio
import time

async def sub_coro():
    return "data"

async def main():
    coro = sub_coro()
    print(type(coro))
    res = await coro
    print(res)

asyncio.run(main())
