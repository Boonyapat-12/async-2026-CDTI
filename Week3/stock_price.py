import asyncio  # ใช้ asyncio สำหรับสร้าง task, sleep แบบ async, wait และ cancel งานที่เหลือ
from time import ctime  # ใช้ ctime เพื่อแสดง timestamp ในผลลัพธ์


async def fetch_stock_price(server_name, delay):  # coroutine จำลองการดึงราคาหุ้นจาก server หนึ่งตัว
    await asyncio.sleep(delay)  # จำลองความช้าของ server ด้วยการรอแบบไม่บล็อก event loop
    return f"[{server_name}] Price: 150 USD"  # คืนผลลัพธ์ราคาหุ้นจำลองเป็นข้อความตามรูปแบบที่โจทย์ต้องการ


async def main():  # coroutine หลักสำหรับสร้างการแข่งขันระหว่าง server ทั้ง 3 ตัว
    tasks = {  # สร้าง set สำหรับเก็บ task ทั้งหมดที่จะแข่งกัน
        asyncio.create_task(fetch_stock_price("Alpha", 3.0)),  # สร้าง task ของ Alpha ซึ่งช้าที่สุด ใช้เวลา 3.0 วินาที
        asyncio.create_task(fetch_stock_price("Beta", 0.8)),  # สร้าง task ของ Beta ซึ่งเร็วที่สุด ใช้เวลา 0.8 วินาที
        asyncio.create_task(fetch_stock_price("Gamma", 1.5))  # สร้าง task ของ Gamma ซึ่งเร็วปานกลาง ใช้เวลา 1.5 วินาที
    }  # ปิด set ของ task ทั้ง 3 ตัว

    done, pending = await asyncio.wait(  # รอ task แบบแบ่งผลลัพธ์เป็นกลุ่มเสร็จแล้วกับยังไม่เสร็จ
        tasks,  # ส่ง set ของ task ทั้งหมดเข้าไปให้ asyncio.wait จัดการ
        return_when=asyncio.FIRST_COMPLETED  # หยุดรอทันทีเมื่อมี task ตัวแรกทำงานเสร็จ
    )  # ได้ผลกลับมาเป็น done และ pending

    for finished_task in done:  # วนอ่าน task ที่ชนะการแข่งขันหรือเสร็จก่อน
        print(f"{ctime()} Winner Result: {finished_task.result()}")  # แสดงผลลัพธ์ของ server ที่ตอบกลับเร็วที่สุด

    print(f"{ctime()} Cleaning up {len(pending)} pending tasks...")  # แจ้งจำนวน task ที่ยังค้างและกำลังจะถูกยกเลิก
    for pending_task in pending:  # วนจัดการ task ที่ยังไม่เสร็จ
        pending_task.cancel()  # สั่งยกเลิก task ที่ไม่ใช่ผู้ชนะ เพื่อไม่ให้ค้างในระบบ

    await asyncio.gather(*pending, return_exceptions=True)  # รวบรวมผลของ task ที่ถูก cancel เพื่อเคลียร์งานค้างอย่างปลอดภัย


asyncio.run(main())  # เริ่ม event loop และรัน main() จนจบ
