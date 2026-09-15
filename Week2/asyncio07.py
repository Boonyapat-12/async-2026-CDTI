# Program 7: Dual Tasks Concurrency
# Concept: Scheduling two distinct tasks concurrently and awaiting them individually without gather.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import time,ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def cook_spaghetti(customer):  # ประกาศฟังก์ชัน cook_spaghetti สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Starting Cooking for customer {customer}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> Finished cooking for customer {customer}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start = time()  # กำหนดหรือปรับค่าให้ start

    #Both tasks are created and run concurrently, but we await them individually.
    task_a = asyncio.create_task(cook_spaghetti("A"))  # Create a concurrent task for customer A
    task_b = asyncio.create_task(cook_spaghetti("B"))  # Create a concurrent task for customer B

    await task_a  # Wait for customer A's cooking to finish
    await task_b  # Wait for customer B's cooking to finish

    print(f"Operation Time: {time() - start:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน