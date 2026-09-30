# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 3 — ดึงข้อมูลจากฐานข้อมูลพร้อมกันด้วย asyncio.gather
#
# โจทย์
# ให้นักเรียนสร้าง Coroutine สำหรับดึงข้อมูลจากฐานข้อมูลสมมติจำนวน 3 ตารางพร้อมกัน โดยใช้ asyncio.gather() เพื่อประมวลผลแบบ Concurrency
#
# ข้อกำหนด
# - สร้าง Coroutine ฟังก์ชัน async def fetch_db_record(table_name: str, latency: float):
# - ภายในฟังก์ชันให้สั่ง await asyncio.sleep(latency)
# - คืนค่า (return) เป็น String ในรูปแบบ f"RowData_{table_name}"
# - สร้างฟังก์ชันหลัก async def main_fetch():
# - เรียกใช้งาน fetch_db_record จำนวน 3 ตารางพร้อมกันผ่าน asyncio.gather() ได้แก่:
#   - ตาราง "users" (latency: 1.0 วินาที)
#   - ตาราง "orders" (latency: 1.5 วินาที)
#   - ตาราง "products" (latency: 0.5 วินาที)
# - คืนค่าผลลัพธ์ที่ได้จาก asyncio.gather() ออกไปเป็น list
#
# ตัวอย่างผลลัพธ์ (Output)
# ['RowData_users', 'RowData_orders', 'RowData_products']
# (เวลาที่ใช้ในการทำงานรวมประมาณ 1.5 วินาที)
#
# เกณฑ์การประเมิน (คะแนนเต็ม 10 คะแนน)
# - 4 คะแนน: นิยามฟังก์ชัน fetch_db_record และ main_fetch ได้ถูกต้องตาม Signature
# - 6 คะแนน: รันงานผ่าน asyncio.gather() สำเร็จ, คืนค่า List คำตอบถูกต้อง และใช้เวลาทำงานแบบ Concurrent (ไม่เกิน 1.8 วินาที)
#
# Code ที่ส่งมีคำอธิบายเดิมว่า:
# Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
# 1. await asyncio.sleep(latency)
# 2. return f"RowData_{table_name}"

import asyncio  # นำเข้าโมดูล asyncio สำหรับรัน coroutine พร้อมกัน


async def fetch_db_record(table_name: str, latency: float):  # ประกาศ coroutine จำลองการดึงข้อมูลจากตารางฐานข้อมูล
    await asyncio.sleep(latency)  # จำลองเวลาหน่วงของการดึงข้อมูลโดยไม่บล็อกงานอื่น
    return f"RowData_{table_name}"  # คืนข้อความข้อมูลแถวตามชื่อตารางที่ได้รับ


async def main_fetch():  # ประกาศ coroutine หลักสำหรับรวมผลการดึงข้อมูลทั้งสามตาราง
    result = await asyncio.gather(  # รัน coroutine ทั้งสามพร้อมกันและรอผลลัพธ์ทั้งหมดตามลำดับที่ส่งเข้าไป
        fetch_db_record("users", 1.0),  # ดึงข้อมูลตาราง users โดยจำลองความหน่วง 1.0 วินาที
        fetch_db_record("orders", 1.5),  # ดึงข้อมูลตาราง orders โดยจำลองความหน่วง 1.5 วินาที
        fetch_db_record("products", 0.5),  # ดึงข้อมูลตาราง products โดยจำลองความหน่วง 0.5 วินาที
    )  # ปิดรายการ coroutine ที่ส่งให้ asyncio.gather
    print(result)  # แสดง list ผลลัพธ์ที่ได้จากทุก coroutine
    return result  # คืน list ผลลัพธ์ให้ผู้เรียกใช้ฟังก์ชัน


asyncio.run(main_fetch())  # สร้าง event loop และเริ่มรัน coroutine หลัก
