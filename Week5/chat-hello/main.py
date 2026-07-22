"""
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
"""
import asyncio
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="WebSocket Central Server")

# ------------------------------------------------------------------
# WebSocket Connection Manager
# ------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        # เก็บ WebSocket connection โดยใช้ student_id เป็น Key
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, student_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[student_id] = websocket

    def disconnect(self, student_id: str):
        if student_id in self.active_connections:
            del self.active_connections[student_id]

    async def broadcast(self, message: str):
        # กระจายข้อความไปยัง Client ทุกเครื่องที่เชื่อมต่ออยู่
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get_status():
    return {
        "status": "Server Online",
        "connected_students": list(manager.active_connections.keys())
    }

# ------------------------------------------------------------------
# WebSocket Endpoint (รับ student_id จาก URL)
# ------------------------------------------------------------------
@app.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(student_id, websocket)
    await manager.broadcast(f"[System]: รหัสนักศึกษา {student_id} เชื่อมต่อเข้าสู่ระบบ")
    
    try:
        while True:
            # รอรับข้อมูลจาก Client
            data = await websocket.receive_text()
            # กระจายข้อมูลให้ทุกหน้าจอ
            await manager.broadcast(f"[{student_id}]: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(student_id)
        await manager.broadcast(f"[System]: รหัสนักศึกษา {student_id} ออกจากระบบ")