import asyncio
import httpx  
from time import ctime

async def fetch_stock_price(server_name: str):
    url = f"http://127.0.0.1:8088/price/{server_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return f"[{data['server']}] Price: {data['price_usd']} USD"

async def main():
    tasks = {
        asyncio.create_task(fetch_stock_price("Alpha")),
        asyncio.create_task(fetch_stock_price("Beta")),
        asyncio.create_task(fetch_stock_price("Gamma"))
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


if __name__ == "__main__":
    asyncio.run(main())