from time import ctime, time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import os  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ฟังก์ชันจำลองการทำกาแฟแบบ Asynchronous
async def make_coffee(customer_name):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    # 1. ดู Process ID และ Thread ID (ซึ่งจะพบว่าเหมือนกันทุกคิว)
    pid = os.getpid()  # กำหนดหรือปรับค่าให้ pid
    thread_id = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ thread_id

    # 2. ดูข้อมูล Task ปัจจุบันของ asyncio
    current_task = asyncio.current_task()  # กำหนดหรือปรับค่าให้ current_task
    assert current_task is not None  # ตรวจสอบเงื่อนไขที่ต้องเป็นจริง
    task_name = current_task.get_name() # ชื่อ Task

    # ใน Python 3.12+ สามารถใช้ดู Unique ID ของ Task ได้ผ่าน id(current_task)
    task_id = id(current_task)  # กำหนดหรือปรับค่าให้ task_id

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Async Task ID: {task_id}] [Task Name: {task_name}] กำลังชงกาแฟให้ ลูกค้า {customer_name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    # จุดสลับงาน (Non-blocking wait)
    await asyncio.sleep(5)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Async Task ID: {task_id}] [Task Name: {task_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue
    main_pid = os.getpid()  # กำหนดหรือปรับค่าให้ main_pid
    main_tid = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ main_tid

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] === เริ่มระบบจำลองตู้กาแฟแบบ asyncio ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time

    tasks = []  # กำหนดหรือปรับค่าให้ tasks
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        # สร้าง Coroutine
        coro = make_coffee(customer)  # กำหนดหรือปรับค่าให้ coro
        # แปลง Coroutine ให้เป็น Task เพื่อให้ Event Loop บริหาร และตั้งชื่อได้
        task = asyncio.create_task(coro, name=f"Task-{customer}")  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        tasks.append(task)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    # สั่งให้ทำพร้อมกัน
    await asyncio.gather(*tasks)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์

    duration = time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"{ctime()} | ใช้เวลารวมทั้งหมด: {duration:0.2f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน