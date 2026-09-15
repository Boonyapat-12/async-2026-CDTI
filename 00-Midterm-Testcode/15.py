import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
async def slow_job():  # ประกาศฟังก์ชัน slow_job สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await asyncio.sleep(10)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        return "Done"  # ส่งผลลัพธ์กลับไปยังผู้เรียก
    except asyncio.CancelledError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("Job was cancelled!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        raise  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await asyncio.wait_for(slow_job(), timeout=2.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    except asyncio.TimeoutError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("Timeout caught")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน