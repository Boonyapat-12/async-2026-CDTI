# Program 4: The await Keyword
# Concept: Pausing a coroutine to let another operation finish using await.
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Task Started")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    await asyncio.sleep(1)  # Pause for 1 second

    print(f"{ctime()} -> Task Finished")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน