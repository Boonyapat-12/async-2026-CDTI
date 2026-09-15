# foodcourt_04_wait_for.py
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from food_utils import send_order_to_kitchen  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ STUDENT_ID
    
    print(f"{ctime()} | --- [Task 4] Practice using wait_for to handle timeouts ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"{ctime()} | [System] Order sent. Monitoring 2.0s timeout limit...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        # ใช้ asyncio.wait_for เพื่อบังคับให้รอผลลัพธ์ไม่เกิน 2.0 วินาที (SLA Limit)
        # เนื่องจากร้านสเต็กใช้เวลาทำ 4.0 วินาที (อิงจากเซิร์ฟเวอร์) คำสั่งนี้จะทำงานไม่สำเร็จตามเวลา
        result = await asyncio.wait_for(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            timeout=2.0  # กำหนดหรือปรับค่าให้ timeout
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        
        # บรรทัดนี้จะไม่ถูกเรียกใช้งาน เนื่องจากโค้ดจะโยน Exception ไปที่ block except ก่อน
        print(f"{ctime()} | Order received: {result}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
    except asyncio.TimeoutError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        # จัดการกับเหตุการณ์ที่รอเกินเวลา (Exception-Driven Control Flow)
        print(f"{ctime()} | Timeout occurred: Steak took too long! Leaving the food court now.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน