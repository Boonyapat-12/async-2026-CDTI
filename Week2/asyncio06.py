# Program 6: Creating a Concurrent Task
# Concept: Wrapping a coroutine inside asyncio.create_task() to schedule it to run in the background.

import asyncio
from time import time,ctime

async def cook_spaghetti(customer):
    print(f"{ctime()} -> Starting Cooking for customer {customer}...")
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> Finished cooking for customer {customer}")

async def main():
    start = time()
    task1 = asyncio.create_task(cook_spaghetti("A"))  # Create a concurrent task for customer A
    
    print(f"{ctime()} -> Main program can do other things while Task A run in background.")

    await task1  # Wait for customer A's cooking to finish

    print(f"Total time: {time() - start:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":
    asyncio.run(main())