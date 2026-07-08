# Objective: Stop an ongoing execution prematurely by triggering a cancellation exception.  # เป้าหมายคือหยุด task ที่กำลังทำงานอยู่ด้วยการ cancel
import asyncio  # ใช้ asyncio สำหรับสร้าง task, sleep และ CancelledError
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาใน output

async def background_loop():  # coroutine งานเบื้องหลังที่ตั้งใจให้วนทำงานไปเรื่อย ๆ
    try:  # เปิด try เพื่อดักจับตอน task ถูก cancel
        print(f"{ctime()} Worker: Starting long infinite process...")  # แจ้งว่า worker เริ่มทำงานยาวแล้ว
        while True:  # loop ไม่รู้จบเพื่อจำลองงานที่ทำต่อเนื่อง
            await asyncio.sleep(1)  # รอ 1 วินาทีแบบไม่บล็อก event loop
            print(f"{ctime()} Worker: Still ticking...")  # แจ้งว่า worker ยังทำงานอยู่
    except asyncio.CancelledError:  # ถ้า task ถูก cancel จะเข้ามาที่ exception นี้
        # เมื่อ task ถูก cancel จะเข้ามาตรงนี้เพื่อจัดการก่อนจบงาน
        print(f"{ctime()} Worker: Interrupted! Executing clean-up logic before exit...")  # แสดงข้อความ cleanup ก่อนจบ

async def main():  # coroutine หลักที่ควบคุม worker
    task = asyncio.create_task(background_loop())  # สร้าง task ให้ background_loop ทำงานเบื้องหลัง
    await asyncio.sleep(2.5) # ปล่อยให้ worker ทำงานไปสักพักก่อน
    
    print(f"{ctime()} Main: Changing plans, canceling the worker task now!")  # แจ้งว่า main จะยกเลิก worker แล้ว
    task.cancel() # สั่งยกเลิก task ที่กำลังทำงานอยู่
    await asyncio.sleep(0.1) # ให้เวลา event loop ส่งสัญญาณ cancel ไปถึง task

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ