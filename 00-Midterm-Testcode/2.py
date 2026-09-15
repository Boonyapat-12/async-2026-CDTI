import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def task_a():  # ประกาศฟังก์ชัน task_a สำหรับรวมขั้นตอนการทำงาน
    print("A1")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print("A2")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def task_b():  # ประกาศฟังก์ชัน task_b สำหรับรวมขั้นตอนการทำงาน
    print("B1")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print("B2")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    t1 = asyncio.create_task(task_a())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    t2 = asyncio.create_task(task_b())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    await t1  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await t2  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
