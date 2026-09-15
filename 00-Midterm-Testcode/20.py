import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(n):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(n)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return n  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = [asyncio.create_task(worker(i)) for i in [3 ,1 ,2]]  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    done, pending = await asyncio.wait(task, return_when=asyncio.FIRST_COMPLETED)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print([t.result() for t in done])  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
