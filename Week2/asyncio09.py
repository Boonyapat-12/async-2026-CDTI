# Program 9: Dynamically Tracking Tasks in a List
# Concept: Managing multiple generated tasks dynamically by appending them into a standard Python list.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import time, ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def serve_customer(name):  # ประกาศฟังก์ชัน serve_customer สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> handing customer {name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to serve
    print(f"{ctime()} -> done customer {name}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time
    customers = ["A", "B", "C", "D"]  # กำหนดหรือปรับค่าให้ customers
    task_list = []  # List to hold the dynamically created tasks

    for name in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        t = asyncio.create_task(serve_customer(name))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        task_list.append(t)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    for t in task_list:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        await t  # Await each task to ensure they complete

    print(f"Total time: {time() - start_time:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

