import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def job():  # ประกาศฟังก์ชัน job สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await asyncio.sleep(5)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    except asyncio.CancelledError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("Cancelled internal")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        raise  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    task = asyncio.create_task(job())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    task.cancel()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    except asyncio.CancelledError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("Cancelled external")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
