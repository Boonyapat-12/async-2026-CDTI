import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def fail_task():  # ประกาศฟังก์ชัน fail_task สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    raise ValueError("Error in fail_task")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

async def pass_task():  # ประกาศฟังก์ชัน pass_task สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(0.2)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return "OK"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        res = await asyncio.gather(fail_task(), pass_task())  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        print(res)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    except ValueError as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print(f"Caught : {e}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
