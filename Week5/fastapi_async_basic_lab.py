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

import asyncio
import time
from fastapi import FastAPI

app = FastAPI(
    title="CS-302: Basic Async FastAPI Lab",
    description="A foundational lab to teach students the difference between blocking synchronous code and cooperative asynchronous code.",
    version="1.0.0"
)

@app.get("/sync-delay")
def sync_delay():
    """
    Step 1: Traditional Synchronous Blocking (def)
    ----------------------------------------------
    - We use 'time.sleep(3)' to simulate a heavy operation (like a slow database query).
    - Even though FastAPI runs standard 'def' in a thread pool to avoid freezing the main thread,
      each request still occupies and completely blocks an entire OS thread for 3 full seconds.
    """
    start_time = time.time()
    print("[SERVER LOG] Starting synchronous blocking sleep...")
    
    # This blocks the thread. No other code can run on this thread during this time.
    time.sleep(3) 
    
    duration = time.time() - start_time
    print(f"[SERVER LOG] Finished sync task in {duration:.2f} seconds!")
    
    return {
        "mode": "Synchronous (Blocking)",
        "message": "This task completely occupied a thread for 3 seconds.",
        "duration_seconds": round(duration, 2)
    }


@app.get("/async-delay")
async def async_delay():
    """
    Step 2: Cooperative Asynchronous (async def)
    ----------------------------------------------
    - We use 'async def' to run this function directly on the main Event Loop.
    - We use 'await asyncio.sleep(3)' to simulate waiting for an external response.
    - Crucial difference: The word 'await' tells the Event Loop, "I am going to wait for 3 seconds.
      Please feel free to pause me and go handle other incoming user requests in the meantime!"
    """
    start_time = time.time()
    print("[SERVER LOG] Starting cooperative asynchronous sleep...")
    
    # This does NOT block. It yields control back to the Event Loop.
    await asyncio.sleep(3) 
    
    duration = time.time() - start_time
    print(f"[SERVER LOG] Finished async task in {duration:.2f} seconds!")
    
    return {
        "mode": "Asynchronous (Non-Blocking)",
        "message": "The server yielded control to help other clients while waiting.",
        "duration_seconds": round(duration, 2)
    }


@app.get("/concurrent-tasks")
async def run_concurrent_tasks():
    """
    Step 3: Power of Concurrency (asyncio.gather)
    ---------------------------------------------
    - What if we have to fetch data from 3 different external APIs, and each takes 2 seconds?
    - Synchronous way: 2 + 2 + 2 = 6 seconds of total waiting.
    - Asynchronous way: We can fire all 3 requests at the same time and 'await' them concurrently.
    - Total waiting time drops to just ~2 seconds (the speed of the slowest task)!
    """
    start_time = time.time()
    print("[SERVER LOG] Starting 3 concurrent tasks...")

    # Define a simple helper async function inside
    async def fetch_data_from_api(api_name: str, wait_time: int):
        print(f"👉 [Task] Starting fetch from {api_name} (takes {wait_time}s)...")
        await asyncio.sleep(wait_time)
        print(f"✅ [Task] Finished fetch from {api_name}!")
        return f"Data from {api_name}"

    # We pack all tasks together and run them in parallel
    results = await asyncio.gather(
        fetch_data_from_api("API_Alpha", 2),
        fetch_data_from_api("API_Beta", 3),
        fetch_data_from_api("API_Gamma", 1)
    )

    duration = time.time() - start_time
    print(f"[SERVER LOG] All concurrent tasks completed in {duration:.2f} seconds!")

    return {
        "mode": "Concurrent Async Execution",
        "results_received": results,
        "efficiency_note": "If executed sequentially, it would have taken 6s (2+3+1). Concurrently, it took only ~3s!",
        "duration_seconds": round(duration, 2)
    }