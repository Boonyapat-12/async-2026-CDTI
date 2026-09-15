import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
async def bad_task():  # ประกาศฟังก์ชัน bad_task สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    raise ValueError("Something went wrong!")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

async def good_task():  # ประกาศฟังก์ชัน good_task สำหรับรวมขั้นตอนการทำงาน
    await asyncio.sleep(2)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    return "Success"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    results = await asyncio.gather(bad_task(), good_task(), return_exceptions=True)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
    print(results)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน