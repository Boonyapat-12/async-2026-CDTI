# Objective: Learn how to query the lifecycle status of a task object.  # เป้าหมายคือเรียนการเช็กสถานะของ task
import asyncio  # ใช้ asyncio สำหรับสร้าง task และ sleep แบบ async
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาปัจจุบันใน output

async def short_job():  # coroutine งานสั้น ๆ ที่ใช้ทดสอบสถานะ task
    await asyncio.sleep(1)  # จำลองงานที่ใช้เวลา 1 วินาทีแบบไม่บล็อก event loop
    return "Success"  # เมื่องานเสร็จให้คืนข้อความ Success

async def main():  # coroutine หลักของโปรแกรม
    task = asyncio.create_task(short_job())  # สร้าง task จาก short_job เพื่อให้ event loop จัดการ
    
    #  Inspect status immediately while it is still running  # ตรวจสถานะทันทีตอน task ยังทำงานอยู่
    print(f"{ctime()} Is task done? {task.done()}")          # ตอนนี้ task ยังทำงานอยู่ จึงน่าจะยังไม่เสร็จ
    print(f"{ctime()} Is task canceled? {task.cancelled()}")  # เช็กว่า task ถูกยกเลิกไปแล้วหรือยัง
    
    await task # รอให้ short_job ทำงานจนเสร็จก่อนค่อยไปบรรทัดถัดไป
    
    # Inspect status again after it finishes  # ตรวจสถานะอีกครั้งหลัง task ทำงานเสร็จแล้ว
    print(f"{ctime()} Is task done now? {task.done()}")      # หลัง await แล้ว task ควรเสร็จเรียบร้อย
    print(f"{ctime()} Is task canceled now? {task.cancelled()}") # ถึง task จะเสร็จแล้ว แต่ไม่ได้แปลว่าถูกยกเลิก

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ