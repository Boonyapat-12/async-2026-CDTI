import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def long_running_task():  # ประกาศฟังก์ชัน long_running_task สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await asyncio.sleep(10)  # Simulate a long-running task
    except asyncio.CancelledError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("Cleaning up...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(1)  # Simulate cleanup time
        print("Cleanup done")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = asyncio.create_task(long_running_task())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    await asyncio.sleep(0.1)  # Let the task run for a bit
    task.cancel()  # Cancel the task
    await task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
