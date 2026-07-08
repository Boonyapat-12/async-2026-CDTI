# Objective: Enforce strict deadlines on operations and raise errors if exceeded.  # เป้าหมายคือจำกัดเวลารอ task ด้วย timeout
import asyncio  # ใช้ asyncio สำหรับ sleep, wait_for และ TimeoutError
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาใน output

async def long_query_simulation():  # coroutine จำลอง query ฐานข้อมูลที่ใช้เวลานาน
    print(f"{ctime()} Database: Fetching data...")  # แจ้งว่าเริ่มดึงข้อมูลจากฐานข้อมูล
    await asyncio.sleep(5.0) # จำลองงานที่ใช้เวลานานกว่ากำหนด timeout
    return "Heavy_Report_Data"  # คืนข้อมูลจำลองเมื่อ query สำเร็จ

async def main():  # coroutine หลักของโปรแกรม
    try:  # เปิด try เพื่อจับ timeout
        print(f"{ctime()} Main: Enforcing a strict 2-second timeout deadline...")  # แจ้งว่ากำหนด deadline ไว้ 2 วินาที
        # wait_for จะรอไม่เกินเวลาที่กำหนด ถ้าเกินจะโยน TimeoutError
        result = await asyncio.wait_for(long_query_simulation(), timeout=2.0)  # รอ query ไม่เกิน 2 วินาที
        print(f"{ctime()} Result acquired: {result}")  # ถ้าเสร็จทันเวลา ให้แสดง result
    except asyncio.TimeoutError:  # ถ้าเกินเวลา 2 วินาที จะเข้ามาตรงนี้
        # ถ้างานช้าเกิน 2 วินาที โปรแกรมจะเข้ามาจัดการ error ตรงนี้
        print(f"{ctime()} Main Error Alert: Operation timed out! Task terminated.")  # แสดงข้อความว่า timeout และ task ถูกหยุด

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ