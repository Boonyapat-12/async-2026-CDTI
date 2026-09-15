import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def sub_coro():  # ประกาศฟังก์ชัน sub_coro สำหรับรวมขั้นตอนการทำงาน
    return "data"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    coro = sub_coro()  # กำหนดหรือปรับค่าให้ coro
    print(type(coro))  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    res = await coro  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(res)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
