"""
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import math

app = FastAPI()

# 📐 กำหนดขนาดขอบเขตสนาม (600x800)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class RocketSpaceManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.rockets: Dict[str, dict] = {}

    async def connect(self, rocket_id: str, websocket: WebSocket, is_dashboard: bool = False):
        await websocket.accept()
        self.connections[rocket_id] = websocket
        
        if not is_dashboard:
            # สุ่มตำแหน่งเริ่มต้นให้อยู่กลางๆ สนาม
            self.rockets[rocket_id] = {
                "x": SCREEN_WIDTH / 2,
                "y": SCREEN_HEIGHT / 2,
                "angle": 0,
                "color": f"hsl({(hash(rocket_id) % 360)}, 80%, 60%)"
            }
        
        await websocket.send_json({
            "type": "INIT",
            "rockets": self.rockets,
            "bounds": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        })

    def disconnect(self, rocket_id: str):
        if rocket_id in self.connections:
            del self.connections[rocket_id]
        if rocket_id in self.rockets:
            del self.rockets[rocket_id]

    async def broadcast(self, message: dict):
        for ws in list(self.connections.values()):
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = RocketSpaceManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    is_dashboard = (client_id == "DASHBOARD")
    await manager.connect(client_id, websocket, is_dashboard)
    
    if not is_dashboard:
        await manager.broadcast({
            "type": "SPAWN",
            "id": client_id,
            "rocket": manager.rockets[client_id]
        })

    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "CONTROL" and client_id in manager.rockets:
                rocket = manager.rockets[client_id]
                action = data["action"]
                
                speed = 8
                if action == "ROTATE_LEFT":
                    rocket["angle"] = (rocket["angle"] - 15) % 360
                elif action == "ROTATE_RIGHT":
                    rocket["angle"] = (rocket["angle"] + 15) % 360
                elif action == "THRUST":
                    rad = math.radians(rocket["angle"])
                    
                    # คำนวณพิกัดใหม่
                    new_x = rocket["x"] + speed * math.cos(rad)
                    new_y = rocket["y"] + speed * math.sin(rad)
                    
                    # 🔒 ล็อคพิกัดไม่ให้หลุดขอบ 800x600 (Padding 20px กันปีกจรวดเกิน)
                    rocket["x"] = max(20, min(SCREEN_WIDTH - 20, new_x))
                    rocket["y"] = max(20, min(SCREEN_HEIGHT - 20, new_y))

                await manager.broadcast({
                    "type": "UPDATE",
                    "id": client_id,
                    "rocket": rocket
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast({
            "type": "DESPAWN",
            "id": client_id
        })