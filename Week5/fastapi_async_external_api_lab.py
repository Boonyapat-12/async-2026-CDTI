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

import asyncio
import time
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="CS-302: Async External HTTP Requests Lab",
    description="A lab session focusing on building async wrappers to fetch third-party public web APIs.",
    version="1.0.0"
)

# We define highly stable and free public endpoints for our experiments
CAT_FACT_API = "https://catfact.ninja/fact"
BITCOIN_PRICE_API = "https://api.coindesk.com/v1/bpi/currentprice.json"
JOKE_API = "https://official-joke-api.appspot.com/random_joke"

# Define fallback mock data for when remote servers are unreachable or rate-limited
MOCK_CAT_FACT = {"fact": "[Fallback Mock] Cats sleep for 70% of their lives.", "length": 41}
MOCK_BTC_PRICE = {"bpi": {"USD": {"rate": "95,430.00"}}}
MOCK_JOKE = {"setup": "[Fallback Mock] Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!"}

@app.get("/single-fetch")
async def fetch_single_api():
    """
    Step 1: Fetching a single external API asynchronously (With Fallback Grace)
    -----------------------------------------------------
    - We attempt a live fetch. If the remote server fails, we fall back to mock data
      to keep our endpoint alive and healthy (Graceful Degradation).
    """
    start_time = time.time()
    print("[SERVER LOG] Initiating single fetch request to CatFact API...")
    fallback_used = False

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CAT_FACT_API, timeout=3.0) # Faster timeout to avoid hanging
            response.raise_for_status() 
            data = response.json()
        except httpx.HTTPError as err:
            # Print the exact exception so the student/instructor can debug the network issue
            print(f"\n[NETWORK WARNING] CatFact API call failed: {str(err)}")
            print("[RESILIENCE] Gracefully falling back to local simulated data...\n")
            data = MOCK_CAT_FACT
            fallback_used = True

    duration = time.time() - start_time
    print(f"[SERVER LOG] Single fetch completed in {duration:.2f} seconds.")

    return {
        "status": "Success",
        "elapsed_seconds": round(duration, 2),
        "source": "CatFact Ninja",
        "fallback_activated": fallback_used,
        "fetched_payload": data
    }

@app.get("/sequential-fetch")
async def fetch_sequentially():
    """
    Step 2: The Bad Practice - Sequential Wait Loops (With Fallback Grace)
    ---------------------------------------------------------------------
    - Attempts to pull from all three APIs sequentially.
    - If any server fails or times out, we catch the warning, log it, and inject fallback data.
    """
    start_time = time.time()
    print("[SERVER LOG] Starting sequential requests to 3 endpoints...")

    results = {}
    fallback_active = False
    
    async with httpx.AsyncClient() as client:
        # 1. Fetch Cat Fact
        try:
            res_cat = await client.get(CAT_FACT_API, timeout=3.0)
            res_cat.raise_for_status()
            results["cat_fact"] = res_cat.json().get("fact")
        except httpx.HTTPError as err:
            print(f"[SEQUENTIAL-WARN] CatFact API unavailable: {str(err)}")
            results["cat_fact"] = MOCK_CAT_FACT.get("fact")
            fallback_active = True
            
        # 2. Fetch Bitcoin Price
        try:
            res_btc = await client.get(BITCOIN_PRICE_API, timeout=3.0)
            res_btc.raise_for_status()
            results["bitcoin_rate"] = res_btc.json().get("bpi", {}).get("USD", {}).get("rate")
        except httpx.HTTPError as err:
            print(f"[SEQUENTIAL-WARN] Bitcoin API unavailable: {str(err)}")
            results["bitcoin_rate"] = MOCK_BTC_PRICE.get("bpi", {}).get("USD", {}).get("rate")
            fallback_active = True
            
        # 3. Fetch Random Joke
        try:
            res_joke = await client.get(JOKE_API, timeout=3.0)
            res_joke.raise_for_status()
            joke_data = res_joke.json()
            results["random_joke"] = f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"
        except httpx.HTTPError as err:
            print(f"[SEQUENTIAL-WARN] Joke API unavailable: {str(err)}")
            joke_data = MOCK_JOKE
            results["random_joke"] = f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"
            fallback_active = True

    duration = time.time() - start_time
    print(f"[SERVER LOG] Sequential process completed in {duration:.2f} seconds.")

    return {
        "mode": "Sequential (Non-Parallel)",
        "elapsed_seconds": round(duration, 2),
        "fallback_activated": fallback_active,
        "results_accumulated": results,
        "critique": "Each request had to wait for the previous one to fully complete."
    }

@app.get("/concurrent-fetch")
async def fetch_concurrently():
    """
    Step 3: The Best Practice - Concurrent Gathering (With Fallback Grace)
    ----------------------------------------------------------------------
    - Fires all requests at once. If any fails, we handle them individually
      to prevent the whole batch from crashing.
    """
    start_time = time.time()
    print("[SERVER LOG] Spawning concurrent async tasks...")
    fallback_active = False

    # Define a helper that handles its own failure and logs details
    async def fetch_safely(client: httpx.AsyncClient, url: str, mock_data: dict, name: str):
        try:
            response = await client.get(url, timeout=3.0)
            response.raise_for_status()
            return response.json(), False
        except httpx.HTTPError as err:
            print(f"[CONCURRENT-WARN] {name} API failed: {str(err)}")
            return mock_data, True

    async with httpx.AsyncClient() as client:
        # Launch tasks concurrently using helper
        cat_task = fetch_safely(client, CAT_FACT_API, MOCK_CAT_FACT, "CatFact")
        btc_task = fetch_safely(client, BITCOIN_PRICE_API, MOCK_BTC_PRICE, "Bitcoin")
        joke_task = fetch_safely(client, JOKE_API, MOCK_JOKE, "Joke")

        # Gather parallel requests
        cat_res, btc_res, joke_res = await asyncio.gather(
            cat_task, btc_task, joke_task
        )
        
        cat_data, cat_fallback = cat_res
        btc_data, btc_fallback = btc_res
        joke_data, joke_fallback = joke_res
        
        fallback_active = cat_fallback or btc_fallback or joke_fallback

        processed_results = {
            "cat_fact": cat_data.get("fact"),
            "bitcoin_rate": btc_data.get("bpi", {}).get("USD", {}).get("rate"),
            "random_joke": f"{joke_data.get('setup')} -> {joke_data.get('punchline')}"
        }

    duration = time.time() - start_time
    print(f"[SERVER LOG] Concurrent process completed in {duration:.2f} seconds!")

    return {
        "mode": "Concurrent Async (Parallel Network I/O)",
        "elapsed_seconds": round(duration, 2),
        "fallback_activated": fallback_active,
        "results_accumulated": processed_results,
        "efficiency_note": "If sequential took ~3s, this took only the time of the slowest single request!"
    }