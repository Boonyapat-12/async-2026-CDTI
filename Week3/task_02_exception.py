# Objective: Extract returned data safely and inspect crashed tasks without breaking the main loop.  # เป้าหมายคืออ่าน result และ exception จาก task อย่างปลอดภัย
import asyncio  # ใช้ asyncio สำหรับสร้าง task และจำลองเวลารอ
from time import ctime  # ใช้ ctime เพื่อพิมพ์เวลาปัจจุบันใน output

async def division_worker(a, b):  # coroutine สำหรับหารเลข a ด้วย b
    await asyncio.sleep(0.5)  # จำลองงานที่ใช้เวลา 0.5 วินาที
    return a / b # will raise ZeroDivisionError if b == 0

async def main():  # coroutine หลักของโปรแกรม
    task_success = asyncio.create_task(division_worker(10, 2))  # สร้าง task ที่หารได้สำเร็จ
    task_fail = asyncio.create_task(division_worker(10, 0))  # สร้าง task ที่จะเกิด ZeroDivisionError เพราะหารด้วยศูนย์

    # wait for both  # รอให้ทั้งสอง task มีเวลาทำงานจนเสร็จ
    await asyncio.sleep(1)  # รอ 1 วินาที เพื่อให้ task ทั้งสองจบก่อนตรวจผล
    
    # ถ้า task สำเร็จและไม่มี error จึงค่อยอ่านผลลัพธ์ด้วย result()
    if task_success.done() and not task_success.exception():  # ตรวจว่า task สำเร็จและไม่มี exception
        print(f"{ctime()} Task Success Result: {task_success.result()}") # แสดงผลลัพธ์ที่ task คืนกลับมา
        
    # ถ้า task ที่หารด้วยศูนย์ทำงานจบแล้ว ให้ดูว่าเกิด exception อะไร
    if task_fail.done():  # ตรวจว่า task ที่คาดว่าจะพังทำงานจบแล้ว
        print(f"{ctime()} Task Fail Exception: {type(task_fail.exception()).__name__}") # แสดงชื่อ error เช่น ZeroDivisionError

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ