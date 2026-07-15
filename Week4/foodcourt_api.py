# foodcourt_api.py
from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from time import ctime

app = FastAPI(title="🍳 Smart Food Court API")

class OrderModel(BaseModel):
    student_id: str
    menu_name: str

# Mock cooking times for each shop (in seconds)
KITCHEN_LATENCY = {
    "hainanese_chicken": 0.8,  # Fast: chopped and served quickly
    "noodle": 1.5,             # Medium: boiling noodles and soup
    "steak": 4.0               # Slowest: grilling thick meat
}

@app.post("/order/{shop_name}")
async def cook_food(shop_name: str, order: OrderModel):
    if shop_name not in KITCHEN_LATENCY:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    cooking_time = KITCHEN_LATENCY[shop_name]
    
    print(f"{ctime()} | [📥 INBOUND ORDER from Student: {order.student_id}] Shop '{shop_name}' started cooking '{order.menu_name}'...")
    await asyncio.sleep(cooking_time)
    print(f"{ctime()} | [🎯 COMPLETED] Shop '{shop_name}' finished cooking '{order.menu_name}'!")
    
    return {
        "status": "READY_FOR_PICKUP",
        "student_id": order.student_id,
        "shop": shop_name,
        "menu": order.menu_name,
        "cooking_seconds": cooking_time,
        "timestamp": ctime()
    }

# How to run the server: uvicorn foodcourt_api:app --port 8088