import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(delay):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(delay)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return delay  # ส่งผลลัพธ์กลับไปยังผู้เรียก


async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    start = time.time()  # กำหนดหรือปรับค่าให้ start
    res = await asyncio.gather(worker(2), worker(3), worker(1))  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
    print(f"Time: {round(time.time() - start)}, Res: {res}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
