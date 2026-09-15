import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def compute():  # ประกาศฟังก์ชัน compute สำหรับรวมขั้นตอนการทำงาน
    return 42  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = asyncio.create_task(compute())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    # Line X
    res = task.result  # กำหนดหรือปรับค่าให้ res
    print(res)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
