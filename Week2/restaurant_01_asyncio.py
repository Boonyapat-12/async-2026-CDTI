import asyncio
import threading
from time import ctime,time

async def greet_diners(customer):
    print(f"{ctime()} -> Greeting for customer-{customer} ...")    
    await asyncio.sleep(1)
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")

async def customer_private_workflow(customer):
    print(f"{ctime()} [Task-{customer}] Taking Order ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Taking Order ...Done!")

    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...Done!")

    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...Done!")

    print(f"\n{ctime()} [Task-{customer}] All served!")

async def main():
    customers = ["A", "B", "C"]

    start_time = time()

    for customer in customers:
        await greet_diners(customer)
    
    print(f"{ctime()} --- All customers greeted, FORKING into independent tasks for each customer ...")

    tasks = []

    for customer in customers:
        task = asyncio.create_task(customer_private_workflow(customer))
        tasks.append(task)

    for task in tasks:
        await task

    print(f"Total Operation time: {time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())