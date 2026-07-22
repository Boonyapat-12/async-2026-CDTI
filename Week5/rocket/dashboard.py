import webbrowser
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

server_ip = input("กรุณากรอก IP ของ Server (กด Enter หากเป็น localhost): ").strip() or "localhost"

app = FastAPI(title="Mission Control Dashboard")

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🚀 Rocket Space Dashboard (800x600)</title>
    <style>
        body {{
            margin: 0; background-color: #0b0f19; color: white; font-family: sans-serif;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 100vh;
        }}
        #header {{ margin-bottom: 10px; text-align: center; }}
        #header h1 {{ margin: 0; font-size: 24px; }}
        #counter {{ font-size: 16px; color: #38bdf8; font-weight: bold; }}
        
        /* กำหนดขนาดกรอบ Canvas 800x600 */
        #canvas-container {{
            border: 3px solid #38bdf8;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
            overflow: hidden;
        }}
        canvas {{ display: block; background: radial-gradient(circle, #1a233a 0%, #0b0f19 100%); }}
    </style>
</head>
<body>

<div id="header">
    <h1>Mission Control Dashboard</h1>
    <div id="counter">Active Rockets: 0 | Arena: 800 x 600</div>
</div>

<div id="canvas-container">
    <canvas id="space" width="800" height="600"></canvas>
</div>

<script>
    const canvas = document.getElementById('space');
    const ctx = canvas.getContext('2d');

    const rockets = {{}};
    const ws = new WebSocket("ws://{server_ip}:8088/ws/DASHBOARD");

    ws.onmessage = (event) => {{
        const data = JSON.parse(event.data);

        if (data.type === 'INIT') {{
            Object.assign(rockets, data.rockets);
        }} else if (data.type === 'SPAWN' || data.type === 'UPDATE') {{
            rockets[data.id] = data.rocket;
        }} else if (data.type === 'DESPAWN') {{
            delete rockets[data.id];
        }}
        
        document.getElementById('counter').innerText = `Active Rockets: ${{Object.keys(rockets).length}} | Arena: 800 x 600`;
    }};

    function drawRocket(x, y, angle, color, id) {{
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle * Math.PI / 180);

        ctx.beginPath();
        ctx.moveTo(20, 0);
        ctx.lineTo(-15, -12);
        ctx.lineTo(-8, 0);
        ctx.lineTo(-15, 12);
        ctx.closePath();

        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.restore();

        ctx.fillStyle = '#ffffff';
        ctx.font = '12px monospace';
        ctx.fillText(id, x - 20, y - 25);
    }}

    function drawGrid(gridSize = 50) {{
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;

        for (let x = 0; x < canvas.width; x += gridSize) {{
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }}

        for (let y = 0; y < canvas.height; y += gridSize) {{
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }}
    }}

    function render() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        drawGrid(50);

        for (const [id, rocket] of Object.entries(rockets)) {{
            drawRocket(rocket.x, rocket.y, rocket.angle, rocket.color, id);
        }}

        requestAnimationFrame(render);
    }}
    render();
</script>
</body>
</html>
"""

@app.get("/")
async def get_dashboard():
    return HTMLResponse(html_code)

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)