# Objective: Label task objects explicitly to simplify logging and production tracking.
import asyncio
from time import ctime

async def background_worker():
    await asyncio.sleep(0.1)

async def main():
    task = asyncio.create_task(background_worker())
    
    # ดูชื่อเริ่มต้นที่ asyncio ตั้งให้ task อัตโนมัติ
    print(f"{ctime()} Initial Name: {task.get_name()}") # ชื่อนี้ช่วยแยก task ตอน debug ได้
    
    # เปลี่ยนชื่อ task ให้สื่อความหมายมากขึ้น
    task.set_name("Payment-Gateway-Validator")
    print(f"{ctime()} Updated Name: {task.get_name()}") # แสดงชื่อใหม่หลังจากตั้งค่าแล้ว

asyncio.run(main())