# Program 6: Creating a Concurrent Task
# Concept: Wrapping a coroutine inside asyncio.create_task() to schedule it to run in the background.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import time,ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def cook_spaghetti(customer):  # ประกาศฟังก์ชัน cook_spaghetti สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Starting Cooking for customer {customer}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> Finished cooking for customer {customer}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start = time()  # กำหนดหรือปรับค่าให้ start
    task1 = asyncio.create_task(cook_spaghetti("A"))  # Create a concurrent task for customer A
    
    print(f"{ctime()} -> Main program can do other things while Task A run in background.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    await task1  # Wait for customer A's cooking to finish

    print(f"Total time: {time() - start:.2f} seconds")  # Should take ~1 second since tasks run concurrently

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน