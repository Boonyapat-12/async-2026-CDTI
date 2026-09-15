"""
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from typing import Dict  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import math  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

app = FastAPI()  # กำหนดหรือปรับค่าให้ app

# 📐 กำหนดขนาดขอบเขตสนาม (600x800)
SCREEN_WIDTH = 800  # กำหนดหรือปรับค่าให้ SCREEN_WIDTH
SCREEN_HEIGHT = 600  # กำหนดหรือปรับค่าให้ SCREEN_HEIGHT

class RocketSpaceManager:  # ประกาศคลาส RocketSpaceManager สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        self.connections: Dict[str, WebSocket] = {}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.rockets: Dict[str, dict] = {}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def connect(self, rocket_id: str, websocket: WebSocket, is_dashboard: bool = False):  # ประกาศฟังก์ชัน connect สำหรับรวมขั้นตอนการทำงาน
        await websocket.accept()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        self.connections[rocket_id] = websocket  # กำหนดหรือปรับค่าให้ self.connections[rocket_id]
        
        if not is_dashboard:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            # สุ่มตำแหน่งเริ่มต้นให้อยู่กลางๆ สนาม
            self.rockets[rocket_id] = {  # กำหนดหรือปรับค่าให้ self.rockets[rocket_id]
                "x": SCREEN_WIDTH / 2,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "y": SCREEN_HEIGHT / 2,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "angle": 0,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "color": f"hsl({(hash(rocket_id) % 360)}, 80%, 60%)"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        
        await websocket.send_json({  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            "type": "INIT",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "rockets": self.rockets,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "bounds": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        })  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    def disconnect(self, rocket_id: str):  # ประกาศฟังก์ชัน disconnect สำหรับรวมขั้นตอนการทำงาน
        if rocket_id in self.connections:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            del self.connections[rocket_id]  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        if rocket_id in self.rockets:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            del self.rockets[rocket_id]  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def broadcast(self, message: dict):  # ประกาศฟังก์ชัน broadcast สำหรับรวมขั้นตอนการทำงาน
        for ws in list(self.connections.values()):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
                await ws.send_json(message)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            except Exception:  # จัดการข้อผิดพลาดชนิดที่ระบุ
                pass  # เว้นพื้นที่ไว้โดยยังไม่เพิ่มการทำงานในบล็อกนี้

manager = RocketSpaceManager()  # กำหนดหรือปรับค่าให้ manager

@app.websocket("/ws/{client_id}")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def websocket_endpoint(websocket: WebSocket, client_id: str):  # ประกาศฟังก์ชัน websocket_endpoint สำหรับรวมขั้นตอนการทำงาน
    is_dashboard = (client_id == "DASHBOARD")  # กำหนดหรือปรับค่าให้ is_dashboard
    await manager.connect(client_id, websocket, is_dashboard)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    if not is_dashboard:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        await manager.broadcast({  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            "type": "SPAWN",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "id": client_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "rocket": manager.rockets[client_id]  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        })  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
            data = await websocket.receive_json()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            
            if data["type"] == "CONTROL" and client_id in manager.rockets:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                rocket = manager.rockets[client_id]  # กำหนดหรือปรับค่าให้ rocket
                action = data["action"]  # กำหนดหรือปรับค่าให้ action
                
                speed = 8  # กำหนดหรือปรับค่าให้ speed
                if action == "ROTATE_LEFT":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    rocket["angle"] = (rocket["angle"] - 15) % 360  # กำหนดหรือปรับค่าให้ rocket["angle"]
                elif action == "ROTATE_RIGHT":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    rocket["angle"] = (rocket["angle"] + 15) % 360  # กำหนดหรือปรับค่าให้ rocket["angle"]
                elif action == "THRUST":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    rad = math.radians(rocket["angle"])  # กำหนดหรือปรับค่าให้ rad
                    
                    # คำนวณพิกัดใหม่
                    new_x = rocket["x"] + speed * math.cos(rad)  # กำหนดหรือปรับค่าให้ new_x
                    new_y = rocket["y"] + speed * math.sin(rad)  # กำหนดหรือปรับค่าให้ new_y
                    
                    # 🔒 ล็อคพิกัดไม่ให้หลุดขอบ 800x600 (Padding 20px กันปีกจรวดเกิน)
                    rocket["x"] = max(20, min(SCREEN_WIDTH - 20, new_x))  # กำหนดหรือปรับค่าให้ rocket["x"]
                    rocket["y"] = max(20, min(SCREEN_HEIGHT - 20, new_y))  # กำหนดหรือปรับค่าให้ rocket["y"]

                await manager.broadcast({  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                    "type": "UPDATE",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                    "id": client_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                    "rocket": rocket  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                })  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    except WebSocketDisconnect:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        manager.disconnect(client_id)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        await manager.broadcast({  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            "type": "DESPAWN",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "id": client_id  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        })  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้