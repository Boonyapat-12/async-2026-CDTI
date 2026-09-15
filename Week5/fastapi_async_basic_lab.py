"""
================================================================================
CS-302: Introduction to FastAPI - Async Basics Lab 02
Topic: Understanding async, await, and Non-blocking Cooperative Multitasking
================================================================================

How to Run This Lab:
--------------------
1. Run the development server:
   $ uvicorn fastapi_async_basic_lab:app --reload --port 8000

2. Open your browser to test endpoints:
   - Sync Blocking:       http://127.0.0.1:8000/sync-delay
   - Async Non-Blocking:  http://127.0.0.1:8000/async-delay
   - Concurrent Tasks:    http://127.0.0.1:8000/concurrent-tasks
"""

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from fastapi import FastAPI  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(  # กำหนดหรือปรับค่าให้ app
    title="CS-302: Basic Async FastAPI Lab",  # กำหนดหรือปรับค่าให้ title
    description="A foundational lab to teach students the difference between blocking synchronous code and cooperative asynchronous code.",  # กำหนดหรือปรับค่าให้ description
    version="1.0.0"  # กำหนดหรือปรับค่าให้ version
)  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

@app.get("/sync-delay")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
def sync_delay():  # ประกาศฟังก์ชัน sync_delay สำหรับรวมขั้นตอนการทำงาน
    """
    Step 1: Traditional Synchronous Blocking (def)
    ----------------------------------------------
    - We use 'time.sleep(3)' to simulate a heavy operation (like a slow database query).
    - Even though FastAPI runs standard 'def' in a thread pool to avoid freezing the main thread,
      each request still occupies and completely blocks an entire OS thread for 3 full seconds.
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Starting synchronous blocking sleep...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # This blocks the thread. No other code can run on this thread during this time.
    time.sleep(3)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    
    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] Finished sync task in {duration:.2f} seconds!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "mode": "Synchronous (Blocking)",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "message": "This task completely occupied a thread for 3 seconds.",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "duration_seconds": round(duration, 2)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


@app.get("/async-delay")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def async_delay():  # ประกาศฟังก์ชัน async_delay สำหรับรวมขั้นตอนการทำงาน
    """
    Step 2: Cooperative Asynchronous (async def)
    ----------------------------------------------
    - We use 'async def' to run this function directly on the main Event Loop.
    - We use 'await asyncio.sleep(3)' to simulate waiting for an external response.
    - Crucial difference: The word 'await' tells the Event Loop, "I am going to wait for 3 seconds.
      Please feel free to pause me and go handle other incoming user requests in the meantime!"
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Starting cooperative asynchronous sleep...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # This does NOT block. It yields control back to the Event Loop.
    await asyncio.sleep(3)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] Finished async task in {duration:.2f} seconds!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "mode": "Asynchronous (Non-Blocking)",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "message": "The server yielded control to help other clients while waiting.",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "duration_seconds": round(duration, 2)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


@app.get("/concurrent-tasks")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def run_concurrent_tasks():  # ประกาศฟังก์ชัน run_concurrent_tasks สำหรับรวมขั้นตอนการทำงาน
    """
    Step 3: Power of Concurrency (asyncio.gather)
    ---------------------------------------------
    - What if we have to fetch data from 3 different external APIs, and each takes 2 seconds?
    - Synchronous way: 2 + 2 + 2 = 6 seconds of total waiting.
    - Asynchronous way: We can fire all 3 requests at the same time and 'await' them concurrently.
    - Total waiting time drops to just ~2 seconds (the speed of the slowest task)!
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Starting 3 concurrent tasks...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    # Define a simple helper async function inside
    async def fetch_data_from_api(api_name: str, wait_time: int):  # ประกาศฟังก์ชัน fetch_data_from_api สำหรับรวมขั้นตอนการทำงาน
        print(f"👉 [Task] Starting fetch from {api_name} (takes {wait_time}s)...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(wait_time)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"✅ [Task] Finished fetch from {api_name}!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        return f"Data from {api_name}"  # ส่งผลลัพธ์กลับไปยังผู้เรียก

    # We pack all tasks together and run them in parallel
    results = await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        fetch_data_from_api("API_Alpha", 2),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        fetch_data_from_api("API_Beta", 3),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        fetch_data_from_api("API_Gamma", 1)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] All concurrent tasks completed in {duration:.2f} seconds!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "mode": "Concurrent Async Execution",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "results_received": results,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "efficiency_note": "If executed sequentially, it would have taken 6s (2+3+1). Concurrently, it took only ~3s!",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "duration_seconds": round(duration, 2)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้