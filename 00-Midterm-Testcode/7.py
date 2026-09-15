import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(n):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(n)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    if n == 2:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        raise ValueError("Failed on 2")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ
    return n  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    tasks = [asyncio.create_task(worker(i)) for i in [1, 2, 3]]  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"Done: {len(done)}, Pending: {len(pending)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
