import asyncio
async def compute(x):
    return x * 2

async def main():
    t1 = asyncio.create_task(compute(5))
    t2 = asyncio.create_task(compute(10))

    res2 = await t2
    res1 = await t1
    print(f"{res1}, {res2}")

asyncio.run(main())