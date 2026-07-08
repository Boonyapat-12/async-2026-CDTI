# mock_stock_api.py
from fastapi import FastAPI
import asyncio

app = FastAPI(title="Asyncio Week 3 Mock Stock API")

@app.get("/price/{server_name}")
async def get_stock_price(server_name: str):
    """ API จำลองราคาหุ้น โดยแต่ละสาขาจะมีความหน่วง (Latency) ไม่เท่ากัน """
    name_lower = server_name.lower()
    
    if name_lower == "alpha":
        await asyncio.sleep(3.0)  # ช้าที่สุด
        price = 152.50
    elif name_lower == "beta":
        await asyncio.sleep(0.8)  # เร็วที่สุด!
        price = 149.80
    elif name_lower == "gamma":
        await asyncio.sleep(1.5)  # ปานกลาง
        price = 150.20
    else:
        await asyncio.sleep(0.1)
        price = 100.00
        
    return {
        "server": server_name,
        "price_usd": price,
        "status": "success"
    }
# pip install fastapi uvicorn httpx
# วิธีรันเซิร์ฟเวอร์: uvicorn stock_api:app --reload --port 8088