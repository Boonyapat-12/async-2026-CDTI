import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker():  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    print("Working...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = asyncio.create_task(worker())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    task.add_done_callback(lambda t: print("Task Finished!"))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    await task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
