# foodcourt_01_create_task.py
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from food_utils import send_order_to_kitchen  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    MY_STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ MY_STUDENT_ID
    print(f"{ctime()} | --- [Task 1] Practice using create_task to queue an order ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # 1. Create a task for ordering chicken rice without awaiting it immediately.
    # Store the task object in 'food_task'.
    food_task = asyncio.create_task(  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        send_order_to_kitchen(MY_STUDENT_ID, "hainanese_chicken", "Chicken Rice Mixed")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    
    # 2. Check the task status immediately using .done() to see if it is finished.
    print(f"{ctime()} | Checking task status immediately: Is it done? = {food_task.done()}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # 3. Use await to fetch the result once the task is fully completed.
    result = await food_task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} | System Response: {result}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน