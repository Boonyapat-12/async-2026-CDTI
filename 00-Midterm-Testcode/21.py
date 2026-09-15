import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def count():  # ประกาศฟังก์ชัน count สำหรับรวมขั้นตอนการทำงาน
    print("One")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print("Two")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    await asyncio.gather(count(), count(), count())  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์

asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

