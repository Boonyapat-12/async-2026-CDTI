import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def compute(val):  # ประกาศฟังก์ชัน compute สำหรับรวมขั้นตอนการทำงาน
    return val * 2  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    coro = compute(10)  # กำหนดหรือปรับค่าให้ coro
    res = await coro  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(res)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
