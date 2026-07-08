# Objective: Introspect runtime contexts and monitor open workload queues on the active loop.  # เป้าหมายคือดู task ที่กำลังอยู่ใน event loop
import asyncio  # ใช้ asyncio สำหรับดู current task, all tasks และสร้าง task ใหม่
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาใน output

async def dynamic_job(number):  # coroutine งานย่อยที่รับหมายเลขงานเข้ามา
    await asyncio.sleep(1.0)  # จำลองงานที่ใช้เวลา 1 วินาที

async def main():  # coroutine หลักของโปรแกรม
    # Check identity of the current wrapper context  # ตรวจ task ปัจจุบันที่กำลังรัน main อยู่
    me = asyncio.current_task()  # ดึง task ปัจจุบันจาก event loop
    me.set_name("Main-Coordinator")  # ตั้งชื่อ task หลักให้เป็น Main-Coordinator
    print(f"{ctime()} Active Execution Context Name: {me.get_name()}")  # แสดงชื่อ task หลักปัจจุบัน
    
    # spawn multiple background items dynamically  # สร้าง task งานย่อยหลายตัวแบบ dynamic
    tasks = [asyncio.create_task(dynamic_job(i), name=f"Job-{i}") for i in range(3)]  # สร้าง Job-0 ถึง Job-2 ด้วย list comprehension
    
    # Peek inside active event loop queues to map workflow  # ดูรายการ task ที่ active อยู่ใน event loop
    all_active = asyncio.all_tasks()  # ดึง task ทั้งหมดที่ยัง active ใน event loop
    print(f"{ctime()} Total Active Tasks inside Loop: {len(all_active)}")  # แสดงจำนวน task ทั้งหมดที่ active
    for t in all_active:  # วนดู task แต่ละตัวใน event loop
        print(f"{ctime()}  -> Active Queue Item: {t.get_name()}")  # แสดงชื่อ task แต่ละตัว

    await asyncio.sleep(1.1) # รอให้งานย่อยทั้งหมดทำงานเสร็จ

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ