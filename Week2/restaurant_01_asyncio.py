import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime,time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def greet_diners(customer):  # ประกาศฟังก์ชัน greet_diners สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Greeting for customer-{customer} ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def customer_private_workflow(customer):  # ประกาศฟังก์ชัน customer_private_workflow สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} [Task-{customer}] Taking Order ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} [Task-{customer}] Taking Order ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    print(f"\n{ctime()} [Task-{customer}] All served!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    customers = ["A", "B", "C"]  # กำหนดหรือปรับค่าให้ customers

    start_time = time()  # กำหนดหรือปรับค่าให้ start_time

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        await greet_diners(customer)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    print(f"{ctime()} --- All customers greeted, FORKING into independent tasks for each customer ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    tasks = []  # กำหนดหรือปรับค่าให้ tasks

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        task = asyncio.create_task(customer_private_workflow(customer))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        tasks.append(task)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    for task in tasks:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        await task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    print(f"Total Operation time: {time() - start_time:.2f} seconds")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน