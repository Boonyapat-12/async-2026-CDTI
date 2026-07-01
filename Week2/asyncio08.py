# Program 8: Task Interleaving (Context Switching)
# Concept: Watching a single thread switch back and forth between two different workflows using create_task.

import asyncio
from time import ctime

async def kitchen_crew():
    print(f"{ctime()} -> [Chef] puts noodles in boiling water...")
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> [Chef] strains the noodles")

async def bar_Crew():
    print(f"{ctime()} -> [Bar] starts grinding coffee beans...")
    await asyncio.sleep(1)  # Simulate time taken to make cocktails
    print(f"{ctime()} -> [Bar] pours espresso shot!")

async def main():
    # Create concurrent tasks for kitchen and bar crews
    task_kitchen = asyncio.create_task(kitchen_crew())
    task_bar = asyncio.create_task(bar_Crew())

    # Await both tasks to finish
    await task_kitchen
    await task_bar

if __name__ == "__main__":
    asyncio.run(main())