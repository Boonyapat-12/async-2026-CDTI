# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 4 — ดึงข้อมูลจากฐานข้อมูลพร้อมกันด้วย asyncio.wait
#
# โจทย์
# ให้นักเรียนปรับเปลี่ยนการดึงข้อมูลจากฐานข้อมูลสมมติจำนวน 3 ตารางพร้อมกัน โดยใช้ asyncio.wait() แทน asyncio.gather()
#
# ข้อกำหนด
# - สร้าง Coroutine ฟังก์ชัน async def fetch_db_record(table_name: str, latency: float):
# - ภายในฟังก์ชันให้สั่ง await asyncio.sleep(latency)
# - คืนค่า (return) เป็น String ในรูปแบบ f"RowData_{table_name}"
# - สร้างฟังก์ชันหลัก async def main_fetch_wait():
# - สร้าง Task จำนวน 3 ตารางด้วย asyncio.create_task() ได้แก่:
#   - ตาราง "users" (latency: 1.0 วินาที)
#   - ตาราง "orders" (latency: 1.5 วินาที)
#   - ตาราง "products" (latency: 0.5 วินาที)
# - เรียกใช้งาน await asyncio.wait(...) เพื่อรอให้ทุก Task ทำงานเสร็จสมบูรณ์
# - ดึงผลลัพธ์จากเซตของ Task ที่เสร็จแล้ว (done) ผ่านการเรียก task.result()
# - คืนค่าเป็น set ของข้อมูลผลลัพธ์ทั้งหมด
#
# ตัวอย่างผลลัพธ์ (Output)
# {'RowData_users', 'RowData_orders', 'RowData_products'}
# (เวลาที่ใช้ในการทำงานรวมประมาณ 1.5 วินาที)
#
# เกณฑ์การประเมิน (คะแนนเต็ม 10 คะแนน)
# - 4 คะแนน: นิยามฟังก์ชัน fetch_db_record และ main_fetch_wait ได้ถูกต้องตาม Signature
# - 6 คะแนน: รันงานผ่าน asyncio.wait() สำเร็จ, คืนค่า Set คำตอบถูกต้อง และใช้เวลาทำงานแบบ Concurrent (ไม่เกิน 1.8 วินาที)
#
# Code ที่ส่งมีคำอธิบายเดิมว่า:
# Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
# 1. await asyncio.sleep(latency)
# 2. return f"RowData_{table_name}"

import asyncio  # นำเข้าโมดูล asyncio สำหรับรันและควบคุม task


async def fetch_db_record(table_name: str, latency: float):  # ประกาศ coroutine จำลองการดึงข้อมูลจากตารางฐานข้อมูล
    await asyncio.sleep(latency)  # จำลองเวลาหน่วงของการดึงข้อมูลโดยไม่บล็อก task อื่น
    return f"RowData_{table_name}"  # คืนข้อความข้อมูลแถวตามชื่อตารางที่ได้รับ


async def main_fetch_wait():  # ประกาศ coroutine หลักสำหรับรอ task ด้วย asyncio.wait
    task = {  # สร้าง set เพื่อเก็บ task ทั้งสามรายการ
        asyncio.create_task(fetch_db_record("users", 1.0)),  # สร้าง task สำหรับตาราง users
        asyncio.create_task(fetch_db_record("orders", 1.5)),  # สร้าง task สำหรับตาราง orders
        asyncio.create_task(fetch_db_record("products", 0.5)),  # สร้าง task สำหรับตาราง products
    }  # ปิด set ของ task ที่ต้องรอ

    done, pending = await asyncio.wait(task)  # รอจนทุก task เสร็จ แล้วรับ set งานที่เสร็จและงานที่ยังค้าง
    result = set()  # สร้าง set ว่างสำหรับเก็บผลลัพธ์โดยไม่ให้ข้อมูลซ้ำกัน
    for finished_task in done:  # วนดู task ทุกตัวที่เสร็จแล้ว
        result.add(finished_task.result())  # อ่านผลลัพธ์ของ task แล้วเพิ่มเข้า set

    print(result)  # แสดง set ของข้อมูลที่ดึงได้ทั้งหมด
    return result  # คืน set ผลลัพธ์ให้ผู้เรียกใช้ฟังก์ชัน


asyncio.run(main_fetch_wait())  # สร้าง event loop และเริ่มรัน coroutine หลัก
