import asyncio  # ใช้ asyncio สำหรับสร้าง task, wait แบบ FIRST_COMPLETED และยกเลิก request ที่เหลือ
import httpx  # ใช้ httpx.AsyncClient สำหรับยิง HTTP request แบบ async ไปยัง FastAPI server
from time import ctime  # ใช้ ctime เพื่อแสดง timestamp ใน output

async def fetch_stock_price(server_name: str):
    """
    TODO: Assignment 3 - เขียนฟังก์ชันเชื่อมต่อ Mock Server ผ่านระบบเครือข่าย
    1. กำหนดเป้าหมายไปที่พอร์ต 8088 ตามสเปกเซิร์ฟเวอร์ของอาจารย์
    2. ใช้ httpx.AsyncClient() ดึงข้อมูลเพื่อไม่ให้เกิดการ Block สัญญาณ Event Loop
    3. นำข้อมูล JSON (server และ price_usd) มาจัดฟอร์แมตแสดงผล
    """
    url = f"http://127.0.0.1:8088/price/{server_name}"
    
    async with httpx.AsyncClient() as client:  # เปิด async HTTP client และปิดให้อัตโนมัติเมื่อใช้งานเสร็จ
        response = await client.get(url)  # ยิง GET request ไปยัง URL และรอ response แบบไม่บล็อก event loop
        data = response.json()  # แปลง response JSON ให้เป็น dictionary ของ Python
        return f"[{data['server']}] Price: {data['price_usd']} USD"  # จัดรูปแบบผลลัพธ์ให้เหมือนตัวอย่าง output

async def main():  # coroutine หลักสำหรับทำ concurrency racing บน network request 3 สาขา
    tasks = {  # สร้าง set เพื่อเก็บ task ของ request ทั้ง 3 ตัว
        asyncio.create_task(fetch_stock_price("Alpha")),  # สร้าง task ยิง request ไปหา Alpha
        asyncio.create_task(fetch_stock_price("Beta")),  # สร้าง task ยิง request ไปหา Beta ซึ่งคาดว่าจะตอบเร็วสุด
        asyncio.create_task(fetch_stock_price("Gamma"))  # สร้าง task ยิง request ไปหา Gamma
    }  # ปิด set ของ task

    done, pending = await asyncio.wait(  # รอ request แบบแข่งกัน แล้วแบ่งเป็น done กับ pending
        tasks,  # ส่ง task ทั้งหมดเข้าไปให้ wait จัดการ
        return_when=asyncio.FIRST_COMPLETED  # หยุดรอทันทีเมื่อ request ตัวแรกทำงานเสร็จ
    )  # ได้ task ที่เสร็จแล้วและ task ที่ยังค้างอยู่กลับมา

    for finished_task in done:  # วนอ่าน task ที่ตอบกลับเร็วที่สุด
        print(f"{ctime()} Winner Result: {finished_task.result()}")  # แสดงผลลัพธ์ราคาหุ้นของผู้ชนะ

    print(f"{ctime()} Cleaning up {len(pending)} pending tasks...")  # แจ้งว่ากำลังเก็บกวาด request ที่ยังไม่เสร็จ
    for pending_task in pending:  # วนจัดการ task ที่ยังค้างอยู่
        pending_task.cancel()  # ยกเลิก request ที่เหลือเพื่อลดงานค้างและป้องกัน memory leak

    await asyncio.gather(*pending, return_exceptions=True)  # รอให้ task ที่ถูก cancel เคลียร์ตัวเองจนจบอย่างปลอดภัย


if __name__ == "__main__":  # ถ้ารันไฟล์นี้โดยตรง ให้เริ่ม main()
    asyncio.run(main())  # เริ่ม event loop และรัน main() จนจบ