import asyncio
from time import ctime


async def fetch_stock_price(server_name, delay):
    await asyncio.sleep(delay)
    return f"[{server_name}] Price: 150 USD"


async def main():
    tasks = {
        asyncio.create_task(fetch_stock_price("Alpha", 3.0)),
        asyncio.create_task(fetch_stock_price("Beta", 0.8)),
        asyncio.create_task(fetch_stock_price("Gamma", 1.5))
    }

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    for finished_task in done:
        print(f"{ctime()} Winner Result: {finished_task.result()}")

    print(f"{ctime()} Cleaning up {len(pending)} pending tasks...")
    for pending_task in pending:
        pending_task.cancel()

    await asyncio.gather(*pending, return_exceptions=True)


asyncio.run(main())
