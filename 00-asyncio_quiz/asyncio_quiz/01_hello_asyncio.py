# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 1 — Hello World ด้วย Asynchronous asyncio
#
# โจทย์
# ให้นักเรียนเขียนฟังก์ชัน Asynchronous ชื่อ say_hello() เพื่อแสดงผลข้อความตามลำดับที่กำหนด และมีการหน่วงเวลาแบบ Asynchronous
#
# ข้อกำหนด
# - สร้างฟังก์ชัน async def say_hello():
# - พิมพ์ข้อความ "Hello" ออกทางหน้าจอ
# - ใช้คำสั่ง await asyncio.sleep(1.5) เพื่อหน่วงเวลา 1.5 วินาที
# - พิมพ์ข้อความ "World" ออกทางหน้าจอ
#
# ตัวอย่างผลลัพธ์ (Output)
# Hello
# (เว้นระยะเวลา 1.5 วินาที)
# World
#
# เกณฑ์การประเมิน (คะแนนเต็ม 5 คะแนน)
# - 2 คะแนน: ประกาศฟังก์ชัน say_hello() และโครงสร้างโค้ดถูกต้อง
# - 3 คะแนน: มีการใช้ await asyncio.sleep(1.5) และรันงานได้ถูกต้องตามเวลาที่กำหนด

import asyncio  # นำเข้าโมดูล asyncio สำหรับสร้างงานแบบ asynchronous


async def say_hello():  # ประกาศ coroutine สำหรับแสดง Hello แล้วรอแบบไม่บล็อกโปรแกรม
    print("Hello")  # แสดงข้อความแรกออกทางหน้าจอ
    await asyncio.sleep(1.5)  # หยุดเฉพาะ coroutine นี้ 1.5 วินาที โดยเปิดโอกาสให้งานอื่นทำงานได้
    print("World")  # แสดงข้อความที่สองหลังจากครบเวลาหน่วง


asyncio.run(say_hello())  # สร้าง event loop และเริ่มรัน coroutine หลักจนเสร็จ
