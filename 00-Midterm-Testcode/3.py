import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(n):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(0.5)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return n * 10  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start = time.time()  # กำหนดหรือปรับค่าให้ start
    tasks = [asyncio.create_task(worker(i)) for i in range(1, 4)]  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    for t in tasks:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        res = await t  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"Time: {round(time.time() - start)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(res, end=" ")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
