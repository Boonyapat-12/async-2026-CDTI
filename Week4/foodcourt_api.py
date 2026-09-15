# foodcourt_api.py
from fastapi import FastAPI, HTTPException  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from pydantic import BaseModel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from time import ctime  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(title="🍳 Smart Food Court API")  # กำหนดหรือปรับค่าให้ app

class OrderModel(BaseModel):  # ประกาศคลาส OrderModel สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    student_id: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    menu_name: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

# Mock cooking times for each shop (in seconds)
KITCHEN_LATENCY = {  # กำหนดหรือปรับค่าให้ KITCHEN_LATENCY
    "hainanese_chicken": 0.8,  # Fast: chopped and served quickly
    "noodle": 1.5,             # Medium: boiling noodles and soup
    "steak": 4.0               # Slowest: grilling thick meat
}  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

@app.post("/order/{shop_name}")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def cook_food(shop_name: str, order: OrderModel):  # ประกาศฟังก์ชัน cook_food สำหรับรวมขั้นตอนการทำงาน
    if shop_name not in KITCHEN_LATENCY:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        raise HTTPException(status_code=404, detail="Shop not found")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ
        
    cooking_time = KITCHEN_LATENCY[shop_name]  # กำหนดหรือปรับค่าให้ cooking_time
    
    print(f"{ctime()} | [📥 INBOUND ORDER from Student: {order.student_id}] Shop '{shop_name}' started cooking '{order.menu_name}'...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(cooking_time)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"{ctime()} | [🎯 COMPLETED] Shop '{shop_name}' finished cooking '{order.menu_name}'!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "status": "READY_FOR_PICKUP",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "student_id": order.student_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "shop": shop_name,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "menu": order.menu_name,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "cooking_seconds": cooking_time,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "timestamp": ctime()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

# How to run the server: uvicorn foodcourt_api:app --port 8088