# Objective: Attach a plain synchronous function that automatically triggers the moment a task finishes.  # เป้าหมายคือผูก callback ให้ทำงานตอน task เสร็จ
import asyncio  # ใช้ asyncio สำหรับสร้าง task และ sleep แบบ async
from time import ctime  # ใช้ ctime เพื่อพิมพ์เวลาใน output

def alert_manager(finished_task):  # function callback ที่รับ task ที่เสร็จแล้วเข้ามา
    # callback นี้จะถูกเรียกอัตโนมัติเมื่อ task ทำงานเสร็จ
    print(f"{ctime()} Callback Triggered! Task output fetched: {finished_task.result()}")  # อ่าน result จาก task แล้วแสดงผล

async def download_file():  # coroutine จำลองการดาวน์โหลดไฟล์
    print(f"{ctime()} Downloading packet...")  # แจ้งว่าเริ่มดาวน์โหลดข้อมูล
    await asyncio.sleep(1.0)  # จำลองเวลาดาวน์โหลด 1 วินาที
    return "Data_Payload.zip"  # คืนชื่อไฟล์ที่ดาวน์โหลดเสร็จ

async def main():  # coroutine หลักของโปรแกรม
    task = asyncio.create_task(download_file())  # สร้าง task จาก download_file
    # ผูก callback เข้ากับ task เพื่อให้เรียก alert_manager ตอนงานเสร็จ
    task.add_done_callback(alert_manager)  # เมื่อ task เสร็จ ให้เรียก alert_manager อัตโนมัติ
    
    await task # รอ task หลักให้เสร็จ เพื่อไม่ให้โปรแกรมจบก่อน callback ทำงาน

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ