# Program 7: Dual Tasks Concurrency
# Concept: Scheduling two distinct tasks concurrently and awaiting them individually without gather.

import asyncio
from time import time,ctime

async def cook_spaghetti(customer):
    print(f"{ctime()} -> Starting Cooking for customer {customer}...")
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> Finished cooking for customer {customer}")

async def main():
    start = time()

    #Both tasks are created and run concurrently, but we await them individually.
    task_a = asyncio.create_task(cook_spaghetti("A"))  # Create a concurrent task for customer A
    task_b = asyncio.create_task(cook_spaghetti("B"))  # Create a concurrent task for customer B

    await task_a  # Wait for customer A's cooking to finish
    await task_b  # Wait for customer B's cooking to finish

    print(f"Operation Time: {time() - start:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":
    asyncio.run(main())