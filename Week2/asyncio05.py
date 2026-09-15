# Program 5: Sequential Execution (The Wrong Way)
# Concept: Showing that simply awaiting one after another is still sequential (Synchronous behavior).

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import time, ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def serve_customer(name):  # ประกาศฟังก์ชัน serve_customer สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Cooking for {name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # Simulate time taken to cook
    print(f"{ctime()} -> Served {name}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start = time()  # กำหนดหรือปรับค่าให้ start
    await serve_customer("A")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await serve_customer("B")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    print(f"Total time: {time() - start:.2f} seconds") #Will take ~2 seconds since it's sequential

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
