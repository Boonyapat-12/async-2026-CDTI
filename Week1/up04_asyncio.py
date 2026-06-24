from time import ctime, perf_counter
import asyncio


def log(message):
    print(f"{ctime()} | {message}", flush=True)


async def update_cup_number(customer_name):
    log(f"LCD: Processing for customer {customer_name}...")
    await asyncio.sleep(1)
    log(f"LCD: Done for customer {customer_name}.")


async def make_coffee(customer_name):
    log(f"Making coffee for {customer_name}...")
    await asyncio.sleep(1)
    log(f"Coffee ready for {customer_name}!")
    await update_cup_number(customer_name)


async def main():
    queue = ['A', 'B', 'C']

    log("=== Asyncio Coffee Machine ===")
    start_time = perf_counter()

    tasks = []
    for customer in queue:
        task = asyncio.create_task(make_coffee(customer))
        tasks.append(task)

    await asyncio.gather(*tasks)

    duration = perf_counter() - start_time
    log(f"Total time: {duration:0.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
