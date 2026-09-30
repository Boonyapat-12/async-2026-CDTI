# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 2 — การสร้าง Concurrent Tasks ด้วย Coroutine เดียวกัน
#
# โจทย์
# ให้นักเรียนสร้าง Coroutine ฟังก์ชันเพื่อรัน Task แบบ Asynchronous พร้อมกัน 2 งานโดยใช้ asyncio.create_task()
#
# ข้อกำหนด
# - สร้าง Coroutine ฟังก์ชัน async def print_message(message, delay): ที่รับค่าข้อความและเวลาหน่วง
# - ภายในฟังก์ชัน print_message ให้สั่ง await asyncio.sleep(delay) แล้วพิมพ์ (print) ข้อความที่ได้รับเข้ามา
# - สร้างฟังก์ชันหลัก async def main_task(): เพื่อครอบการทำงาน
#   - สร้าง Task 1 ให้เรียก print_message("A", 1.0)
#   - สร้าง Task 2 ให้เรียก print_message("B", 2.0)
#   - ใช้ await เพื่อรอให้ทั้งสอง Task ทำงานจนเสร็จ
#
# ตัวอย่างผลลัพธ์ (Output)
# (ผ่านไป 1.0 วินาที)
# A
# (ผ่านไปอีก 1.0 วินาที / รวม 2.0 วินาที)
# B
#
# เกณฑ์การประเมิน (คะแนนเต็ม 5 คะแนน)
# - 2 คะแนน: ประกาศฟังก์ชัน print_message และ main_task พร้อมโครงสร้าง asyncio ถูกต้อง
# - 3 คะแนน: มีการสร้าง Task ทำงานพร้อมกัน (Concurrency) และแสดงผล A กับ B ตามลำดับและเวลาที่ถูกต้อง

import asyncio  # นำเข้าโมดูล asyncio สำหรับจัดการ coroutine และ task


async def print_message(message, delay):  # ประกาศ coroutine ที่รับข้อความและเวลาหน่วง
    await asyncio.sleep(delay)  # รอแบบ asynchronous ตามเวลาที่รับเข้ามา
    print(message)  # แสดงข้อความเมื่อเวลาหน่วงสิ้นสุดลง


async def main_task():  # ประกาศ coroutine หลักสำหรับสร้างและรอ task ทั้งสอง
    task_A = asyncio.create_task(print_message("A", 1.0))  # สร้าง task A ให้รอ 1.0 วินาทีแล้วพิมพ์ A
    task_B = asyncio.create_task(print_message("B", 2.0))  # สร้าง task B ให้รอ 2.0 วินาทีแล้วพิมพ์ B

    await task_A  # รอให้ task A ทำงานเสร็จสมบูรณ์
    await task_B  # รอให้ task B ทำงานเสร็จสมบูรณ์


if __name__ == "__main__":  # รันส่วนนี้เฉพาะเมื่อเปิดไฟล์นี้โดยตรง
    asyncio.run(main_task())  # สร้าง event loop และเริ่มรัน coroutine หลัก
