import asyncio
async def slow_job():
    try:
        await asyncio.sleep(10)
        return "Done"
    except asyncio.CancelledError:
        print("Job was cancelled!")
        raise

async def main():
    try:
        await asyncio.wait_for(slow_job(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Timeout caught")

asyncio.run(main())