# foodcourt_02_gather.py
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime, perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from food_utils import send_order_to_kitchen  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    # จำลองรหัสนักศึกษา (จะใช้รหัสเดียวกันหรือต่างกันก็ได้ในกรณีสั่งเป็นกลุ่ม)
    STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ STUDENT_ID
    
    print(f"{ctime()} | --- [Task 2] Practice using gather to wait for all group orders ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # เริ่มจับเวลา
    start_time = perf_counter()  # กำหนดหรือปรับค่าให้ start_time
    
    # ใช้ asyncio.gather() เพื่อส่งคำสั่งซื้อ 3 ร้านพร้อมกัน และรอจนกว่าทุกร้านจะทำเสร็จ
    results = await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    
    # เมื่อทุก Task เสร็จสิ้น (อิงจากเวลาของร้านที่ช้าที่สุดคือ steak: ~4.0 วินาที)
    # วนลูปนำผลลัพธ์ที่ได้รับมาแสดงผล
    for result in results:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        print(f"{ctime()} | [Pickup] Shop: {result.get('shop')} | Menu: {result.get('menu')} is ready!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
    # สรุปเวลาทั้งหมดที่ใช้ไป
    elapsed_time = perf_counter() - start_time  # กำหนดหรือปรับค่าให้ elapsed_time
    print(f"{ctime()} | Total time: {elapsed_time:.2f} seconds (Equals to the slowest dish).")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน