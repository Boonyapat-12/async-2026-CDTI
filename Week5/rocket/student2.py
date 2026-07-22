import webbrowser
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# 1. รับค่ารหัสนักศึกษา และ IP ของ Server จาก Terminal
student_id = input("กรุณากรอกรหัสนักศึกษา (หรือชื่อจรวด): ").strip() or "Rocket_101"
server_ip = input("กรุณากรอก IP ของ Server (กด Enter หากเป็น localhost): ").strip() or "localhost"

app = FastAPI(title=f"Rocket Controller - {student_id}")

# 2. หน้าจอควบคุมจรวด (HTML + CSS + JavaScript)
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rocket Controller - {student_id}</title>
    <style>
        body {{
            background-color: #1e293b; color: white; font-family: sans-serif;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; margin: 0; user-select: none;
        }}
        .info {{
            text-align: center; margin-bottom: 20px;
        }}
        .id-box {{
            font-size: 24px; font-weight: bold; color: #38bdf8; background: #0f172a;
            padding: 8px 20px; border-radius: 8px; border: 1px solid #334155; display: inline-block; margin-top: 10px;
        }}
        .controls {{ display: grid; grid-template-columns: repeat(3, 100px); gap: 15px; margin-top: 20px; }}
        button {{
            height: 80px; background: #3b82f6; border: none; border-radius: 12px;
            color: white; font-size: 20px; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px #1d4ed8; transition: all 0.1s;
        }}
        button:active {{ transform: translateY(4px); box-shadow: none; }}
        .thrust {{ grid-column: span 3; background: #ef4444; box-shadow: 0 4px #b91c1c; font-size: 24px; }}
    </style>
</head>
<body>

    <div class="info">
        <h2>Rocket Controller</h2>
        <div class="id-box">ID: {student_id}</div>
        <p style="color: #94a3b8; font-size: 14px;">เชื่อมต่อไปยัง: ws://{server_ip}:8088/ws/{student_id}</p>
        <p>ใช้ปุ่มด้านล่าง หรือปุ่มลูกศร (← → ↑) บนคีย์บอร์ดเพื่อขับจรวด</p>
    </div>

    <div class="controls">
        <button onclick="sendControl('ROTATE_LEFT')">↺ Left</button>
        <div></div>
        <button onclick="sendControl('ROTATE_RIGHT')">Right ↻</button>
        <button class="thrust" onclick="sendControl('THRUST')">🔥 THRUST 🔥</button>
    </div>

<script>
    const studentId = "{student_id}";
    // เชื่อมต่อไปยัง Server หลัก (Port 8088)
    const ws = new WebSocket(`ws://{server_ip}:8088/ws/${{studentId}}`);

    function sendControl(action) {{
        if (ws.readyState === WebSocket.OPEN) {{
            ws.send(JSON.stringify({{
                type: 'CONTROL',
                action: action
            }}));
        }}
    }}

    // รองรับการกดปุ่มบนคีย์บอร์ด (Arrow Keys)
    window.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowLeft') sendControl('ROTATE_LEFT');
        if (e.key === 'ArrowRight') sendControl('ROTATE_RIGHT');
        if (e.key === 'ArrowUp') sendControl('THRUST');
    }});
</script>
</body>
</html>
"""

@app.get("/")
async def get_index():
    return HTMLResponse(html_code)

if __name__ == "__main__":
    # เปิดเบราว์เซอร์ไปที่ Port 8001 อัตโนมัติ
    webbrowser.open("http://127.0.0.1:8003")
    # รัน FastAPI Server บนเครื่องนักเรียน Port 8003
    uvicorn.run(app, host="127.0.0.1", port=8003)