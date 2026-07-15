# foodcourt_01_create_task.py
import asyncio
from time import ctime
from food_utils import send_order_to_kitchen

async def main():
    MY_STUDENT_ID = "6710301033"
    print(f"{ctime()} | --- [Task 1] Practice using create_task to queue an order ---")
    
    # 1. Create a task for ordering chicken rice without awaiting it immediately.
    # Store the task object in 'food_task'.
    food_task = asyncio.create_task(
        send_order_to_kitchen(MY_STUDENT_ID, "hainanese_chicken", "Chicken Rice Mixed")
    )
    
    # 2. Check the task status immediately using .done() to see if it is finished.
    print(f"{ctime()} | Checking task status immediately: Is it done? = {food_task.done()}")
    
    # 3. Use await to fetch the result once the task is fully completed.
    result = await food_task
    print(f"{ctime()} | System Response: {result}")

if __name__ == "__main__":
    asyncio.run(main())