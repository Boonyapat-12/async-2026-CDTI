"""
================================================================================
🎓 CS-302: Introduction to FastAPI - Async HTTP Client Lab 03
Topic: Consuming External APIs and Non-Blocking Network I/O with HTTPX
================================================================================

How to Run This Lab:
--------------------
1. Install requirements (httpx is mandatory for async request dispatching):
   $ pip install fastapi uvicorn httpx

2. Run the development server:
   $ uvicorn fastapi_async_external_api_lab:app --reload --port 8000

3. Open your browser:
   - Interactive UI Docs: http://127.0.0.1:8000/docs
"""

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from fastapi import FastAPI, HTTPException  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(  # กำหนดหรือปรับค่าให้ app
    title="CS-302: Async External HTTP Requests Lab",  # กำหนดหรือปรับค่าให้ title
    description="A lab session focusing on building async wrappers to fetch third-party public web APIs.",  # กำหนดหรือปรับค่าให้ description
    version="1.0.0"  # กำหนดหรือปรับค่าให้ version
)  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

# We define highly stable and free public endpoints for our experiments
CAT_FACT_API = "https://catfact.ninja/fact"  # กำหนดหรือปรับค่าให้ CAT_FACT_API
BITCOIN_PRICE_API = "https://api.coindesk.com/v1/bpi/currentprice.json"  # กำหนดหรือปรับค่าให้ BITCOIN_PRICE_API
JOKE_API = "https://official-joke-api.appspot.com/random_joke"  # กำหนดหรือปรับค่าให้ JOKE_API

# Define fallback mock data for when remote servers are unreachable or rate-limited
MOCK_CAT_FACT = {"fact": "[Fallback Mock] Cats sleep for 70% of their lives.", "length": 41}  # กำหนดหรือปรับค่าให้ MOCK_CAT_FACT
MOCK_BTC_PRICE = {"bpi": {"USD": {"rate": "95,430.00"}}}  # กำหนดหรือปรับค่าให้ MOCK_BTC_PRICE
MOCK_JOKE = {"setup": "[Fallback Mock] Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!"}  # กำหนดหรือปรับค่าให้ MOCK_JOKE

@app.get("/single-fetch")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def fetch_single_api():  # ประกาศฟังก์ชัน fetch_single_api สำหรับรวมขั้นตอนการทำงาน
    """
    Step 1: Fetching a single external API asynchronously (With Fallback Grace)
    -----------------------------------------------------
    - We attempt a live fetch. If the remote server fails, we fall back to mock data
      to keep our endpoint alive and healthy (Graceful Degradation).
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Initiating single fetch request to CatFact API...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    fallback_used = False  # กำหนดหรือปรับค่าให้ fallback_used

    async with httpx.AsyncClient() as client:  # เปิดใช้งาน resource ภายใน context manager
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            response = await client.get(CAT_FACT_API, timeout=3.0) # Faster timeout to avoid hanging
            response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            data = response.json()  # กำหนดหรือปรับค่าให้ data
        except httpx.HTTPError as err:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            # Print the exact exception so the student/instructor can debug the network issue
            print(f"\n[NETWORK WARNING] CatFact API call failed: {str(err)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            print("[RESILIENCE] Gracefully falling back to local simulated data...\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            data = MOCK_CAT_FACT  # กำหนดหรือปรับค่าให้ data
            fallback_used = True  # กำหนดหรือปรับค่าให้ fallback_used

    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] Single fetch completed in {duration:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "status": "Success",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "elapsed_seconds": round(duration, 2),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "source": "CatFact Ninja",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "fallback_activated": fallback_used,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "fetched_payload": data  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

@app.get("/sequential-fetch")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def fetch_sequentially():  # ประกาศฟังก์ชัน fetch_sequentially สำหรับรวมขั้นตอนการทำงาน
    """
    Step 2: The Bad Practice - Sequential Wait Loops (With Fallback Grace)
    ---------------------------------------------------------------------
    - Attempts to pull from all three APIs sequentially.
    - If any server fails or times out, we catch the warning, log it, and inject fallback data.
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Starting sequential requests to 3 endpoints...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    results = {}  # กำหนดหรือปรับค่าให้ results
    fallback_active = False  # กำหนดหรือปรับค่าให้ fallback_active
    
    async with httpx.AsyncClient() as client:  # เปิดใช้งาน resource ภายใน context manager
        # 1. Fetch Cat Fact
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            res_cat = await client.get(CAT_FACT_API, timeout=3.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            res_cat.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            results["cat_fact"] = res_cat.json().get("fact")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        except httpx.HTTPError as err:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"[SEQUENTIAL-WARN] CatFact API unavailable: {str(err)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            results["cat_fact"] = MOCK_CAT_FACT.get("fact")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            fallback_active = True  # กำหนดหรือปรับค่าให้ fallback_active
            
        # 2. Fetch Bitcoin Price
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            res_btc = await client.get(BITCOIN_PRICE_API, timeout=3.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            res_btc.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            results["bitcoin_rate"] = res_btc.json().get("bpi", {}).get("USD", {}).get("rate")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        except httpx.HTTPError as err:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"[SEQUENTIAL-WARN] Bitcoin API unavailable: {str(err)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            results["bitcoin_rate"] = MOCK_BTC_PRICE.get("bpi", {}).get("USD", {}).get("rate")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            fallback_active = True  # กำหนดหรือปรับค่าให้ fallback_active
            
        # 3. Fetch Random Joke
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            res_joke = await client.get(JOKE_API, timeout=3.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            res_joke.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            joke_data = res_joke.json()  # กำหนดหรือปรับค่าให้ joke_data
            results["random_joke"] = f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        except httpx.HTTPError as err:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"[SEQUENTIAL-WARN] Joke API unavailable: {str(err)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            joke_data = MOCK_JOKE  # กำหนดหรือปรับค่าให้ joke_data
            results["random_joke"] = f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            fallback_active = True  # กำหนดหรือปรับค่าให้ fallback_active

    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] Sequential process completed in {duration:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "mode": "Sequential (Non-Parallel)",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "elapsed_seconds": round(duration, 2),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "fallback_activated": fallback_active,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "results_accumulated": results,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "critique": "Each request had to wait for the previous one to fully complete."  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

@app.get("/concurrent-fetch")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def fetch_concurrently():  # ประกาศฟังก์ชัน fetch_concurrently สำหรับรวมขั้นตอนการทำงาน
    """
    Step 3: The Best Practice - Concurrent Gathering (With Fallback Grace)
    ----------------------------------------------------------------------
    - Fires all requests at once. If any fails, we handle them individually
      to prevent the whole batch from crashing.
    """
    start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
    print("[SERVER LOG] Spawning concurrent async tasks...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    fallback_active = False  # กำหนดหรือปรับค่าให้ fallback_active

    # Define a helper that handles its own failure and logs details
    async def fetch_safely(client: httpx.AsyncClient, url: str, mock_data: dict, name: str):  # ประกาศฟังก์ชัน fetch_safely สำหรับรวมขั้นตอนการทำงาน
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            response = await client.get(url, timeout=3.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            return response.json(), False  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        except httpx.HTTPError as err:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"[CONCURRENT-WARN] {name} API failed: {str(err)}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            return mock_data, True  # ส่งผลลัพธ์กลับไปยังผู้เรียก

    async with httpx.AsyncClient() as client:  # เปิดใช้งาน resource ภายใน context manager
        # Launch tasks concurrently using helper
        cat_task = fetch_safely(client, CAT_FACT_API, MOCK_CAT_FACT, "CatFact")  # กำหนดหรือปรับค่าให้ cat_task
        btc_task = fetch_safely(client, BITCOIN_PRICE_API, MOCK_BTC_PRICE, "Bitcoin")  # กำหนดหรือปรับค่าให้ btc_task
        joke_task = fetch_safely(client, JOKE_API, MOCK_JOKE, "Joke")  # กำหนดหรือปรับค่าให้ joke_task

        # Gather parallel requests
        cat_res, btc_res, joke_res = await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
            cat_task, btc_task, joke_task  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        
        cat_data, cat_fallback = cat_res  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        btc_data, btc_fallback = btc_res  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        joke_data, joke_fallback = joke_res  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        
        fallback_active = cat_fallback or btc_fallback or joke_fallback  # กำหนดหรือปรับค่าให้ fallback_active

        processed_results = {  # กำหนดหรือปรับค่าให้ processed_results
            "cat_fact": cat_data.get("fact"),  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            "bitcoin_rate": btc_data.get("bpi", {}).get("USD", {}).get("rate"),  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            "random_joke": f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    duration = time.time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"[SERVER LOG] Concurrent process completed in {duration:.2f} seconds!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "mode": "Concurrent Async (Parallel Network I/O)",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "elapsed_seconds": round(duration, 2),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "fallback_activated": fallback_active,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "results_accumulated": processed_results,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "efficiency_note": "If sequential took ~3s, this took only the time of the slowest single request!"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้