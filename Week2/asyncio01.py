# Program 1: The First Coroutine Function
# Concept: Understanding async def and how it differs from a normal function.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def greet():  # ประกาศฟังก์ชัน greet สำหรับรวมขั้นตอนการทำงาน
    print("Hello from the Coroutine")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

print(type(greet))  # <class 'function'>, not a coroutine yet