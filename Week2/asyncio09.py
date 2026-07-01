# Program 9: Dynamically Tracking Tasks in a List
# Concept: Managing multiple generated tasks dynamically by appending them into a standard Python list.

import asyncio
from time import time, ctime

async def serve_customer(name):
    print(f"{ctime()} -> handing customer {name}...")
    await asyncio.sleep(1)  # Simulate time taken to serve
    print(f"{ctime()} -> done customer {name}")

async def main():
    start_time = time()
    customers = ["A", "B", "C", "D"]
    task_list = []  # List to hold the dynamically created tasks

    for name in customers:
        t = asyncio.create_task(serve_customer(name))
        task_list.append(t)

    for t in task_list:
        await t  # Await each task to ensure they complete

    print(f"Total time: {time() - start_time:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":
    asyncio.run(main())

