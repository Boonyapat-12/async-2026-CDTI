import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
async def compute(x):  # ประกาศฟังก์ชัน compute สำหรับรวมขั้นตอนการทำงาน
    return x * 2  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    t1 = asyncio.create_task(compute(5))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    t2 = asyncio.create_task(compute(10))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    res2 = await t2  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    res1 = await t1  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{res1}, {res2}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน