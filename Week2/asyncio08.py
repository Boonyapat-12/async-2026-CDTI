# Program 8: Task Interleaving (Context Switching)
# Concept: Watching a single thread switch back and forth between two different workflows using create_task.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def kitchen_crew():  # ประกาศฟังก์ชัน kitchen_crew สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> [Chef] puts noodles in boiling water...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> [Chef] strains the noodles")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def bar_Crew():  # ประกาศฟังก์ชัน bar_Crew สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> [Bar] starts grinding coffee beans...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to make cocktails
    print(f"{ctime()} -> [Bar] pours espresso shot!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    # Create concurrent tasks for kitchen and bar crews
    task_kitchen = asyncio.create_task(kitchen_crew())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    task_bar = asyncio.create_task(bar_Crew())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    # Await both tasks to finish
    await task_kitchen  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await task_bar  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน