# foodcourt_05_mix_concepts.py
import asyncio
from time import ctime, perf_counter
from food_utils import send_order_to_kitchen

async def main():
    STUDENT_ID = "6710301017"
    
    print(f"{ctime()} | --- [Task 5] Advanced Practice: Mixing concepts together ---")
    
    start_time = perf_counter()
    
    # Task 1: สั่งก๋วยเตี๋ยว (ใช้เวลาทำ 1.5s) ด้วยวงรอบการรอแบบปกติ (Standard waiting cycle)
    noodle_task = asyncio.create_task(
        send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles")
    )
    
    # Task 2: สั่งข้าวมันไก่ (ใช้เวลาทำ 0.8s) โดยนำ asyncio.wait_for มาซ้อน (Wrap) ไว้ข้างใน
    # เพื่อบังคับเงื่อนไขว่าต้องเสร็จภายใน 1.0 วินาที
    chicken_task = asyncio.create_task(
        asyncio.wait_for(
            send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice"), 
            timeout=1.0
        )
    )
    
    try:
        # นำ Task ที่มีโครงสร้างแตกต่างกันมารวมศูนย์ (Resolve) อยู่ใน asyncio.gather() ตัวเดียว
        results = await asyncio.gather(noodle_task, chicken_task)
        
        print(f"{ctime()} | Success: All food served on time! Received {len(results)} dishes.")
        
    except asyncio.TimeoutError:
        # หากมี Task ใดใน gather ที่เกิด Timeout จะตกลงมาที่ Exception นี้
        print(f"{ctime()} | Failed: One of the dishes took too long!")
        
    # สรุปเวลาการทำงานทั้งหมด (จะเท่ากับเวลาของก๋วยเตี๋ยวที่นานกว่า คือ ~1.5 วินาที)
    elapsed_time = perf_counter() - start_time
    print(f"{ctime()} | Total elapsed time: {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())