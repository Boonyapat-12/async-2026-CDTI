# foodcourt_05_mix_concepts.py
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime, perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from food_utils import send_order_to_kitchen  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    STUDENT_ID = "6710301017"  # กำหนดหรือปรับค่าให้ STUDENT_ID
    
    print(f"{ctime()} | --- [Task 5] Advanced Practice: Mixing concepts together ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    start_time = perf_counter()  # กำหนดหรือปรับค่าให้ start_time
    
    # Task 1: สั่งก๋วยเตี๋ยว (ใช้เวลาทำ 1.5s) ด้วยวงรอบการรอแบบปกติ (Standard waiting cycle)
    noodle_task = asyncio.create_task(  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    
    # Task 2: สั่งข้าวมันไก่ (ใช้เวลาทำ 0.8s) โดยนำ asyncio.wait_for มาซ้อน (Wrap) ไว้ข้างใน
    # เพื่อบังคับเงื่อนไขว่าต้องเสร็จภายใน 1.0 วินาที
    chicken_task = asyncio.create_task(  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        asyncio.wait_for(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            timeout=1.0  # กำหนดหรือปรับค่าให้ timeout
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        # นำ Task ที่มีโครงสร้างแตกต่างกันมารวมศูนย์ (Resolve) อยู่ใน asyncio.gather() ตัวเดียว
        results = await asyncio.gather(noodle_task, chicken_task)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        
        print(f"{ctime()} | Success: All food served on time! Received {len(results)} dishes.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
    except asyncio.TimeoutError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        # หากมี Task ใดใน gather ที่เกิด Timeout จะตกลงมาที่ Exception นี้
        print(f"{ctime()} | Failed: One of the dishes took too long!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
    # สรุปเวลาการทำงานทั้งหมด (จะเท่ากับเวลาของก๋วยเตี๋ยวที่นานกว่า คือ ~1.5 วินาที)
    elapsed_time = perf_counter() - start_time  # กำหนดหรือปรับค่าให้ elapsed_time
    print(f"{ctime()} | Total elapsed time: {elapsed_time:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน