# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 5 — การดึงข้อมูลแบบ Concurrent และเรียงลำดับผลลัพธ์ (Sorting Results)
#
# โจทย์
# ให้นักเรียนสร้าง Coroutine จำนวน 2 ฟังก์ชันเพื่อจำลองการดึงข้อมูลจากแหล่งที่ต่างกัน จากนั้นใช้ asyncio.gather() รันงานพร้อมกัน แล้วนำผลลัพธ์ตัวเลขที่ได้มาเรียงลำดับจากน้อยไปมาก (Ascending Order)
#
# ข้อกำหนด
# - สร้าง Coroutine ฟังก์ชัน async def fetch_task_a():
#   - สั่ง await asyncio.sleep(1.0)
#   - คืนค่า (return) เป็น list ตัวเลข: [42, 12, 88]
# - สร้าง Coroutine ฟังก์ชัน async def fetch_task_b():
#   - สั่ง await asyncio.sleep(1.5)
#   - คืนค่า (return) เป็น list ตัวเลข: [5, 67, 23]
# - สร้างฟังก์ชันหลัก async def process_and_sort():
# - เรียกใช้งาน fetch_task_a() และ fetch_task_b() พร้อมกันด้วย asyncio.gather()
# - รวมรายการตัวเลขจากทั้งสอง Task เข้าด้วยกัน
# - นำตัวเลขทั้งหมดมาเรียงลำดับจากน้อยไปมาก
# - คืนค่า (return) เป็น list ของตัวเลขที่เรียงลำดับแล้ว
#
# ตัวอย่างผลลัพธ์ (Output)
# [5, 12, 23, 42, 67, 88]
# (เวลาที่ใช้ในการทำงานรวมประมาณ 1.5 วินาที)
#
# เกณฑ์การประเมิน (คะแนนเต็ม 15 คะแนน)
# - 5 คะแนน: นิยามฟังก์ชัน fetch_task_a, fetch_task_b และ process_and_sort ได้ถูกต้อง
# - 5 คะแนน: ทำงานแบบ Concurrency ด้วย asyncio.gather() โดยใช้เวลาไม่เกิน 1.8 วินาที
# - 5 คะแนน: รวมข้อมูลและเรียงลำดับตัวเลขจากน้อยไปมากได้ถูกต้องสมบูรณ์

import asyncio  # นำเข้าโมดูล asyncio สำหรับรัน coroutine พร้อมกัน


async def fetch_task_a():  # ประกาศ coroutine จำลองการดึงชุดข้อมูล A
    await asyncio.sleep(1.0)  # จำลองเวลารอข้อมูล A แบบ asynchronous 1.0 วินาที
    a = [42, 12, 88]  # เก็บรายการตัวเลขที่ได้จากแหล่งข้อมูล A
    return a  # คืนรายการตัวเลข A ให้ผู้เรียกใช้ฟังก์ชัน


async def fetch_task_b():  # ประกาศ coroutine จำลองการดึงชุดข้อมูล B
    await asyncio.sleep(1.5)  # จำลองเวลารอข้อมูล B แบบ asynchronous 1.5 วินาที
    b = [5, 67, 23]  # เก็บรายการตัวเลขที่ได้จากแหล่งข้อมูล B
    return b  # คืนรายการตัวเลข B ให้ผู้เรียกใช้ฟังก์ชัน


async def process_and_sort():  # ประกาศ coroutine หลักสำหรับรวมและเรียงลำดับข้อมูล
    a, b = await asyncio.gather(  # รันการดึงข้อมูล A และ B พร้อมกัน แล้วแยกผลลัพธ์ออกเป็นสองตัวแปร
        fetch_task_a(),  # ส่ง coroutine ดึงข้อมูล A ให้ asyncio.gather
        fetch_task_b(),  # ส่ง coroutine ดึงข้อมูล B ให้ asyncio.gather
    )  # ปิดรายการ coroutine ที่ส่งให้ asyncio.gather

    result = a + b  # รวม list ตัวเลขจากแหล่ง A และ B เข้าด้วยกัน
    result.sort()  # เรียงตัวเลขใน list จากน้อยไปมาก

    print(result)  # แสดง list ที่เรียงลำดับเรียบร้อยแล้ว
    return result  # คืน list ที่เรียงลำดับแล้วให้ผู้เรียกใช้ฟังก์ชัน


asyncio.run(process_and_sort())  # สร้าง event loop และเริ่มรัน coroutine หลัก
