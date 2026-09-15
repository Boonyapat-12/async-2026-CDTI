import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
async def my_coro():  # ประกาศฟังก์ชัน my_coro สำหรับรวมขั้นตอนการทำงาน
    print("A")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print("B")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = asyncio.create_task(my_coro())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    print("C")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน