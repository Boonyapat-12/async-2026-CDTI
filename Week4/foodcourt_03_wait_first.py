# foodcourt_03_wait_first.py
import asyncio
from time import ctime, perf_counter
from food_utils import send_order_to_kitchen

async def main():
    STUDENT_ID = "6710301033"
    
    print(f"{ctime()} | --- [Task 3] Practice using wait (FIRST_COMPLETED) ---")
    
    # เริ่มจับเวลา
    start_time = perf_counter()
    
    # ห่อหุ้มคำสั่งเป็น Task objects ก่อน เพื่อให้สามารถใช้คำสั่ง .cancel() ในภายหลังได้
    task1 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice Thigh"))
    task2 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles"))
    task3 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak"))
    
    # นำ Tasks ทั้งหมดใส่ List แล้วส่งเข้า asyncio.wait()
    # ตั้งค่า return_when เป็น FIRST_COMPLETED เพื่อให้ await หยุดรอแค่จานแรกที่เสร็จ
    done, pending = await asyncio.wait(
        [task1, task2, task3], 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # ดึงผลลัพธ์ของงานที่เสร็จแล้ว (done)
    # เนื่องจากเราใช้ FIRST_COMPLETED จึงมีแค่งานเดียวที่เสร็จก่อนใคร
    winner_task = done.pop()
    result = winner_task.result()
    print(f"{ctime()} | Winner served dish: Shop: {result.get('shop')} | Menu: {result.get('menu')}")
    
    # ทำความสะอาดทรัพยากร (Active Resource Cleanup)
    # วนลูปเพื่อยกเลิกคำสั่งซื้อที่ยังค้างอยู่ (pending)
    print(f"{ctime()} | Cleaning up: Canceling {len(pending)} remaining pending orders...")
    for task in pending:
        task.cancel()
        
    # สรุปเวลาที่ใช้ไปทั้งหมด
    elapsed_time = perf_counter() - start_time
    print(f"{ctime()} | Total waiting time for the first dish: {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())