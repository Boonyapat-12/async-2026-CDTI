# Objective: Group multiple operations to run concurrently and return an ordered list of outputs.  # เป้าหมายคือใช้ gather รวมผลงานหลายงาน
import asyncio  # ใช้ asyncio สำหรับ gather และ sleep แบบ async
from time import time, ctime  # ใช้ time จับเวลารวม และ ctime แสดงเวลาปัจจุบัน

async def fetch_db_record(table_name, latency):  # coroutine จำลองการดึงข้อมูลจากตารางฐานข้อมูล
    await asyncio.sleep(latency)  # จำลอง latency ของแต่ละ query ตามค่าที่ส่งเข้ามา
    return f"RowData_{table_name}"  # คืนข้อมูลจำลองโดยผูกกับชื่อ table

async def main():  # coroutine หลักของโปรแกรม
    start = time()  # บันทึกเวลาเริ่มต้นเพื่อเอาไว้คำนวณเวลารวม
    
    # asyncio.gather สั่งให้งานหลายตัวเริ่มพร้อมกัน แล้วรวบรวมผลลัพธ์กลับมาเป็น list เดียว
    results = await asyncio.gather(  # รัน coroutine หลายตัวพร้อมกันและรอจนทุกตัวเสร็จ
        fetch_db_record("Users", 1.0),  # งานดึงข้อมูล Users ใช้เวลา 1.0 วินาที
        fetch_db_record("Products", 0.5),  # งานดึงข้อมูล Products ใช้เวลา 0.5 วินาที
        fetch_db_record("Invoices", 1.0)  # งานดึงข้อมูล Invoices ใช้เวลา 1.0 วินาที
    )  # gather คืนผลลัพธ์เป็น list ตามลำดับที่ส่ง coroutine เข้าไป
    
    print(f"{ctime()} Aggregated Output Results List: {results}")  # แสดง list ผลลัพธ์ที่ gather รวมมาให้
    print(f"{ctime()} Execution Completed in: {time() - start:.2f} seconds") # เวลารวมจะใกล้เคียงงานที่ช้าที่สุด ไม่ใช่ผลรวมทุกงาน

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ