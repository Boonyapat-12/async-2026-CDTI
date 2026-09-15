# Program 3: The Event Loop (asyncio.run)
# Concept: Using the Event Loop to actually execute a Coroutine Object.
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def greet():  # ประกาศฟังก์ชัน greet สำหรับรวมขั้นตอนการทำงาน
    print("Hello From the Event Loop!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    coro_object = greet()  # Create a Coroutine Object

    
    asyncio.run(coro_object)  # Run the Coroutine Object using the Event Loop