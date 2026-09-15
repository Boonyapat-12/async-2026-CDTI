# foodcourt_03_wait_first.py
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from time import ctime, perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from food_utils import send_order_to_kitchen  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ STUDENT_ID
    
    print(f"{ctime()} | --- [Task 3] Practice using wait (FIRST_COMPLETED) ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # เริ่มจับเวลา
    start_time = perf_counter()  # กำหนดหรือปรับค่าให้ start_time
    
    # ห่อหุ้มคำสั่งเป็น Task objects ก่อน เพื่อให้สามารถใช้คำสั่ง .cancel() ในภายหลังได้
    task1 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "hainanese_chicken", "Chicken Rice Thigh"))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    task2 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "noodle", "Wonton Noodles"))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    task3 = asyncio.create_task(send_order_to_kitchen(STUDENT_ID, "steak", "Sizzling Steak"))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    
    # นำ Tasks ทั้งหมดใส่ List แล้วส่งเข้า asyncio.wait()
    # ตั้งค่า return_when เป็น FIRST_COMPLETED เพื่อให้ await หยุดรอแค่จานแรกที่เสร็จ
    done, pending = await asyncio.wait(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        [task1, task2, task3],  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        return_when=asyncio.FIRST_COMPLETED  # ส่งผลลัพธ์กลับไปยังผู้เรียก
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    
    # ดึงผลลัพธ์ของงานที่เสร็จแล้ว (done)
    # เนื่องจากเราใช้ FIRST_COMPLETED จึงมีแค่งานเดียวที่เสร็จก่อนใคร
    winner_task = done.pop()  # กำหนดหรือปรับค่าให้ winner_task
    result = winner_task.result()  # กำหนดหรือปรับค่าให้ result
    print(f"{ctime()} | Winner served dish: Shop: {result.get('shop')} | Menu: {result.get('menu')}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # ทำความสะอาดทรัพยากร (Active Resource Cleanup)
    # วนลูปเพื่อยกเลิกคำสั่งซื้อที่ยังค้างอยู่ (pending)
    print(f"{ctime()} | Cleaning up: Canceling {len(pending)} remaining pending orders...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    for task in pending:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        task.cancel()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        
    # สรุปเวลาที่ใช้ไปทั้งหมด
    elapsed_time = perf_counter() - start_time  # กำหนดหรือปรับค่าให้ elapsed_time
    print(f"{ctime()} | Total waiting time for the first dish: {elapsed_time:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน