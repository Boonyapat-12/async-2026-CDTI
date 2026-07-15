# foodcourt_04_wait_for.py
import asyncio
from time import ctime
from food_utils import send_order_to_kitchen

async def main():
    STUDENT_ID = "6710301033"
    
    print(f"{ctime()} | --- [Task 4] Practice using wait_for to handle timeouts ---")
    print(f"{ctime()} | [System] Order sent. Monitoring 2.0s timeout limit...")
    
    try:
        # ใช้ asyncio.wait_for เพื่อบังคับให้รอผลลัพธ์ไม่เกิน 2.0 วินาที (SLA Limit)
        # เนื่องจากร้านสเต็กใช้เวลาทำ 4.0 วินาที (อิงจากเซิร์ฟเวอร์) คำสั่งนี้จะทำงานไม่สำเร็จตามเวลา
        result = await asyncio.wait_for(
            send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak"),
            timeout=2.0
        )
        
        # บรรทัดนี้จะไม่ถูกเรียกใช้งาน เนื่องจากโค้ดจะโยน Exception ไปที่ block except ก่อน
        print(f"{ctime()} | Order received: {result}")
        
    except asyncio.TimeoutError:
        # จัดการกับเหตุการณ์ที่รอเกินเวลา (Exception-Driven Control Flow)
        print(f"{ctime()} | Timeout occurred: Steak took too long! Leaving the food court now.")

if __name__ == "__main__":
    asyncio.run(main())