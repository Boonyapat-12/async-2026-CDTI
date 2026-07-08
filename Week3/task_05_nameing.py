# Objective: Label task objects explicitly to simplify logging and production tracking.  # เป้าหมายคือเรียนการตั้งชื่อ task
import asyncio  # ใช้ asyncio สำหรับสร้าง task และ sleep แบบ async
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาปัจจุบันใน output

async def background_worker():  # coroutine งานเบื้องหลังตัวอย่าง
    await asyncio.sleep(0.1)  # จำลองงานสั้น ๆ ที่ใช้เวลา 0.1 วินาที

async def main():  # coroutine หลักของโปรแกรม
    task = asyncio.create_task(background_worker())  # สร้าง task โดยยังไม่ได้ตั้งชื่อเอง
    
    # ดูชื่อเริ่มต้นที่ asyncio ตั้งให้ task อัตโนมัติ
    print(f"{ctime()} Initial Name: {task.get_name()}") # ชื่อนี้ช่วยแยก task ตอน debug ได้
    
    # เปลี่ยนชื่อ task ให้สื่อความหมายมากขึ้น
    task.set_name("Payment-Gateway-Validator")  # ตั้งชื่อใหม่ให้ task เพื่อให้อ่าน log ง่ายขึ้น
    print(f"{ctime()} Updated Name: {task.get_name()}") # แสดงชื่อใหม่หลังจากตั้งค่าแล้ว

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ