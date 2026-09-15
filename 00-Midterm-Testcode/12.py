import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(n):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    return n * 2  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    coros = [worker(1), worker(2), worker(3)]  # กำหนดหรือปรับค่าให้ coros
    res = await asyncio.gather(*coros)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
    print(res)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
