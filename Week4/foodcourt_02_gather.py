# foodcourt_02_gather.py
import asyncio
from time import ctime, perf_counter
from food_utils import send_order_to_kitchen

async def main():
    # จำลองรหัสนักศึกษา (จะใช้รหัสเดียวกันหรือต่างกันก็ได้ในกรณีสั่งเป็นกลุ่ม)
    STUDENT_ID = "6710301033"
    
    print(f"{ctime()} | --- [Task 2] Practice using gather to wait for all group orders ---")
    
    # เริ่มจับเวลา
    start_time = perf_counter()
    
    # ใช้ asyncio.gather() เพื่อส่งคำสั่งซื้อ 3 ร้านพร้อมกัน และรอจนกว่าทุกร้านจะทำเสร็จ
    results = await asyncio.gather(
        send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice"),
        send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles"),
        send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak")
    )
    
    # เมื่อทุก Task เสร็จสิ้น (อิงจากเวลาของร้านที่ช้าที่สุดคือ steak: ~4.0 วินาที)
    # วนลูปนำผลลัพธ์ที่ได้รับมาแสดงผล
    for result in results:
        print(f"{ctime()} | [Pickup] Shop: {result.get('shop')} | Menu: {result.get('menu')} is ready!")
        
    # สรุปเวลาทั้งหมดที่ใช้ไป
    elapsed_time = perf_counter() - start_time
    print(f"{ctime()} | Total time: {elapsed_time:.2f} seconds (Equals to the slowest dish).")

if __name__ == "__main__":
    asyncio.run(main())