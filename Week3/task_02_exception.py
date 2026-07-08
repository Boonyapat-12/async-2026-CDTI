# Objective: Extract returned data safely and inspect crashed tasks without breaking the main loop.
import asyncio
from time import ctime

async def division_worker(a, b):
    await asyncio.sleep(0.5)
    return a / b # will raise ZeroDivisionError if b == 0

async def main():
    task_success = asyncio.create_task(division_worker(10, 2))
    task_fail = asyncio.create_task(division_worker(10, 0))

    # wait for both
    await asyncio.sleep(1)
    
    # ถ้า task สำเร็จและไม่มี error จึงค่อยอ่านผลลัพธ์ด้วย result()
    if task_success.done() and not task_success.exception():
        print(f"{ctime()} Task Success Result: {task_success.result()}") # แสดงผลลัพธ์ที่ task คืนกลับมา
        
    # ถ้า task ที่หารด้วยศูนย์ทำงานจบแล้ว ให้ดูว่าเกิด exception อะไร
    if task_fail.done():
        print(f"{ctime()} Task Fail Exception: {type(task_fail.exception()).__name__}") # แสดงชื่อ error เช่น ZeroDivisionError

asyncio.run(main())