import webbrowser  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import uvicorn  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from fastapi import FastAPI  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from fastapi.responses import HTMLResponse  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

# 1. รับค่ารหัสนักศึกษา และ IP ของ Server
student_id = input("กรุณากรอกรหัสนักศึกษา (Student ID): ").strip()  # กำหนดหรือปรับค่าให้ student_id
server_ip = input("กรุณากรอก IP ของ Server (กด Enter หากเป็น localhost): ").strip() or "localhost"  # กำหนดหรือปรับค่าให้ server_ip

app = FastAPI(title=f"Client Screen - {student_id}")  # กำหนดหรือปรับค่าให้ app

# 2. โค้ด HTML แสดงผลหน้าจอ
# คอมเมนต์บรรทัดที่เริ่มข้อความหลายบรรทัด โดยไม่เปลี่ยนเนื้อหาภายใน string
html_code = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>หน้าจอแสดงผล - {student_id}</title>
        <style>
            body {{ font-family: sans-serif; margin: 30px; background: #0f172a; color: #f8fafc; }}
            .card {{ background: #1e293b; padding: 20px; border-radius: 8px; border-left: 6px solid #38bdf8; margin-bottom: 20px; }}
            #messages {{ border: 1px solid #334155; height: 300px; overflow-y: scroll; padding: 12px; background: #1e293b; border-radius: 6px; }}
            input, button {{ padding: 10px 14px; margin-top: 10px; border-radius: 4px; border: none; font-size: 14px; }}
            button {{ background: #3b82f6; color: white; cursor: pointer; font-weight: bold; }}
            button:hover {{ background: #2563eb; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>หน้าจอแสดงผลนักศึกษา</h1>
            <h3>รหัสนักศึกษา: <span style="color:#38bdf8;">{student_id}</span></h3>
            <p style="font-size: 0.85em; color: #94a3b8;">เชื่อมต่อไปยัง Server: ws://{server_ip}:8000/ws/{student_id}</p>
        </div>
        
        <div id="messages"></div>
        
        <input type="text" id="messageText" placeholder="พิมพ์ข้อความ..." autocomplete="off"/>
        <button onclick="sendMessage()">ส่งข้อความ (Broadcast)</button>

        <script>
            // เชื่อมต่อไปยัง Server หลักตาม IP และ Student ID
            const ws = new WebSocket("ws://{server_ip}:8088/ws/{student_id}");

            ws.onmessage = function(event) {{
                const messages = document.getElementById('messages');
                const message = document.createElement('div');
                message.style.padding = '4px 0';
                message.textContent = event.data;
                messages.appendChild(message);
                messages.scrollTop = messages.scrollHeight;
            }};

            function sendMessage() {{
                const input = document.getElementById("messageText");
                if (input.value) {{
                    ws.send(input.value);
                    input.value = '';
                }}
            }}
        </script>
    </body>
</html>
"""  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

@app.get("/")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def get_index():  # ประกาศฟังก์ชัน get_index สำหรับรวมขั้นตอนการทำงาน
    return HTMLResponse(html_code)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    # client port
    client_port = 8002  # กำหนดหรือปรับค่าให้ client_port
    # เปิด เบราว์เซอร์ อัตโนมัติไปยังหน้าจอ Client บนเครื่องนั้นๆ
    webbrowser.open(f"http://127.0.0.1:{client_port}")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    # รัน Local Web Server บน Port 8002
    uvicorn.run(app, host="127.0.0.1", port=client_port)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน