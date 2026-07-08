import asyncio
from time import ctime


async def delivery_task(package_id, duration):
    try:
        print(f"{ctime()} Courier started delivering {package_id}...")
        await asyncio.sleep(duration)
        return f"Package {package_id} Delivered!"
    except asyncio.CancelledError:
        print(f"{ctime()} Delivery Canceled! Returning package to warehouse.")
        raise


async def main():
    task = asyncio.create_task(
        delivery_task(package_id="P001", duration=5.0),
        name="Express-Courier"
    )

    await asyncio.sleep(2.0)

    print(f"{ctime()} Checking task '{task.get_name()}'. Is it done? {task.done()}")

    if not task.done():
        print(f"{ctime()} Taking too long! Canceling the task...")
        task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    print(f"{ctime()} Final verify: Is task officially canceled? {task.cancelled()}")


asyncio.run(main())
