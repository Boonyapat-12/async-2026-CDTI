import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def task1():  # ประกาศฟังก์ชัน task1 สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(0.2)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return "T1"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def task2():  # ประกาศฟังก์ชัน task2 สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return "T2"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    done, pending = await asyncio.wait([asyncio.create_task(task1()), asyncio.create_task(task2())], return_when=asyncio.ALL_COMPLETED)  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    print(f"Done count: {len(done)}, Pending count: {len(pending)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
