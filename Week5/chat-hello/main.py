"""
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
"""
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from typing import Dict  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(title="WebSocket Central Server")  # กำหนดหรือปรับค่าให้ app

# ------------------------------------------------------------------
# WebSocket Connection Manager
# ------------------------------------------------------------------
class ConnectionManager:  # ประกาศคลาส ConnectionManager สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        # เก็บ WebSocket connection โดยใช้ student_id เป็น Key
        self.active_connections: Dict[str, WebSocket] = {}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def connect(self, student_id: str, websocket: WebSocket):  # ประกาศฟังก์ชัน connect สำหรับรวมขั้นตอนการทำงาน
        await websocket.accept()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        self.active_connections[student_id] = websocket  # กำหนดหรือปรับค่าให้ self.active_connections[student_id]

    def disconnect(self, student_id: str):  # ประกาศฟังก์ชัน disconnect สำหรับรวมขั้นตอนการทำงาน
        if student_id in self.active_connections:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            del self.active_connections[student_id]  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def broadcast(self, message: str):  # ประกาศฟังก์ชัน broadcast สำหรับรวมขั้นตอนการทำงาน
        # กระจายข้อความไปยัง Client ทุกเครื่องที่เชื่อมต่ออยู่
        for connection in self.active_connections.values():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            await connection.send_text(message)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

manager = ConnectionManager()  # กำหนดหรือปรับค่าให้ manager

@app.get("/")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def get_status():  # ประกาศฟังก์ชัน get_status สำหรับรวมขั้นตอนการทำงาน
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "status": "Server Online",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "connected_students": list(manager.active_connections.keys())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

# ------------------------------------------------------------------
# WebSocket Endpoint (รับ student_id จาก URL)
# ------------------------------------------------------------------
@app.websocket("/ws/{student_id}")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def websocket_endpoint(websocket: WebSocket, student_id: str):  # ประกาศฟังก์ชัน websocket_endpoint สำหรับรวมขั้นตอนการทำงาน
    await manager.connect(student_id, websocket)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await manager.broadcast(f"[System]: รหัสนักศึกษา {student_id} เชื่อมต่อเข้าสู่ระบบ")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
            # รอรับข้อมูลจาก Client
            data = await websocket.receive_text()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            # กระจายข้อมูลให้ทุกหน้าจอ
            await manager.broadcast(f"[{student_id}]: {data}")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            
    except WebSocketDisconnect:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        manager.disconnect(student_id)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        await manager.broadcast(f"[System]: รหัสนักศึกษา {student_id} ออกจากระบบ")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop