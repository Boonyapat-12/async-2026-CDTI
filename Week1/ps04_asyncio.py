from time import ctime, time, process_time
import asyncio
import os
import threading
import psutil

# ฟังก์ชันจำลองการทำกาแฟแบบ Asynchronous
async def make_coffee(customer_name):
    # 1. ดู Process ID และ Thread ID (ซึ่งจะพบว่าเหมือนกันทุกคิว)
    pid = os.getpid()
    thread_id = threading.current_thread().native_id

    # 2. ดูข้อมูล Task ปัจจุบันของ asyncio
    current_task = asyncio.current_task()
    assert current_task is not None
    task_name = current_task.get_name() # ชื่อ Task

    # ใน Python 3.12+ สามารถใช้ดู Unique ID ของ Task ได้ผ่าน id(current_task)
    task_id = id(current_task)

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Async Task ID: {task_id}] [Task Name: {task_name}] กำลังชงกาแฟให้ ลูกค้า {customer_name}...")
    sum(i * i for i in range(1000000)) # จำลองงานคำนวณ (CPU-bound) เล็กน้อย และรอ 5 วินาที
    # จุดสลับงาน (Non-blocking wait)
    await asyncio.sleep(5)
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Async Task ID: {task_id}] [Task Name: {task_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")

async def main():
    queue = ['A', 'B', 'C']
    main_pid = os.getpid()
    main_tid = threading.current_thread().native_id

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] === เริ่มระบบจำลองตู้กาแฟแบบ asyncio ===")
    start_time = time()
    start_cpu = process_time()

    tasks = []
    for customer in queue:
        # สร้าง Coroutine
        coro = make_coffee(customer)
        # แปลง Coroutine ให้เป็น Task เพื่อให้ Event Loop บริหาร และตั้งชื่อได้
        task = asyncio.create_task(coro, name=f"Task-{customer}")
        tasks.append(task)

    # สั่งให้ทำพร้อมกัน
    await asyncio.gather(*tasks)

    duration = time() - start_time
    cpu_duration = process_time() - start_cpu

    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)

    print(f"[สรุปผล Asyncio]")
    print(f"เวลาที่ใช้จริง (Wall Time): {duration:0.2f} วินาที")
    print(f"เวลาที่ CPU ใช้ประมวลผลจริง (CPU Time): {cpu_duration:0.4f} วินาที")
    print(f"ทรัพยากร Memory (RAM) ที่ใช้: {mem_mb:.2f} MB")

if __name__ == "__main__":
    asyncio.run(main())