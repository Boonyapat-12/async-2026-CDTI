import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import redis.asyncio as redis
import uvicorn

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

async def redis_listener():
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe("game:state")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    listener_task = asyncio.create_task(redis_listener())
    yield
    listener_task.cancel()

app = FastAPI(lifespan=lifespan)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tank Game - Web Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        h1 {
            margin: 0 0 15px 0;
            color: #00e5ff;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
            font-size: 26px;
        }
        #main-layout {
            display: flex;
            gap: 20px;
            max-width: 1100px;
            width: 100%;
        }
        #game-container {
            position: relative;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid #333;
            background-color: #1a1a1a;
        }
        canvas {
            background-color: #242424;
            display: block;
        }
        #side-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
            min-width: 320px;
        }
        .card {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card-title {
            font-size: 14px;
            font-weight: bold;
            color: #888;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        #status-box {
            font-size: 16px;
            font-weight: bold;
            color: #ffca28;
            text-align: center;
            padding: 10px;
            background: #282828;
            border-radius: 6px;
            border-left: 4px solid #ffca28;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #timer-text {
            font-size: 20px;
            font-family: monospace;
            color: #00e5ff;
            background: #151515;
            padding: 2px 8px;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 8px 10px;
            text-align: left;
        }
        th {
            border-bottom: 2px solid #333;
            color: #aaa;
        }
        td {
            border-bottom: 1px solid #2a2a2a;
        }
        .color-badge {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
        }
        .hp-bar-bg {
            background-color: #333;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
            width: 80px;
            display: inline-block;
            vertical-align: middle;
        }
        .hp-bar-fill {
            height: 100%;
            width: 100%;
            transition: width 0.2s;
        }
        .status-dead { color: #ff5252; font-weight: bold; }
        .status-alive { color: #4caf50; font-weight: bold; }
        #event-log {
            height: 180px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            background-color: #151515;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .log-item { color: #bbb; }
        .log-hit { color: #ff5252; }
        .log-join { color: #00e5ff; }
        .log-system { color: #ffca28; }
    </style>
</head>
<body>

    <h1>🎮 TANK GAME LIVE DASHBOARD</h1>

    <div id="main-layout">
        <div id="game-container">
            <canvas id="gameCanvas" width="600" height="600"></canvas>
        </div>

        <div id="side-panel">
            <div id="status-box">
                <span id="status-title">CONNECTING...</span>
                <span id="timer-text">03:00</span>
            </div>

            <div class="card">
                <div class="card-title">📊 Player Status / Scoreboard</div>
                <table>
                    <thead>
                        <tr>
                            <th>Team</th>
                            <th>HP</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="player-table">
                        <tr><td colspan="3" style="text-align:center; color:#666;">No players joined</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="card-title">📜 Match Events Log</div>
                <div id="event-log">
                    <div class="log-item log-system">[SYSTEM] Dashboard initialized.</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusTitle = document.getElementById('status-title');
        const timerText = document.getElementById('timer-text');
        const statusBox = document.getElementById('status-box');
        const playerTable = document.getElementById('player-table');
        const eventLog = document.getElementById('event-log');

        // รับค่า Dynamic จาก Server (Default สำรอง = 10)
        let GRID_SIZE = 10;
        let CELL_SIZE = canvas.width / GRID_SIZE;

        let lastPlayersState = {};
        let lastStatus = "";

        const PLAYER_COLORS = [
            '#00e5ff', '#ff4081', '#76ff03', '#ffc400', 
            '#d500f9', '#00e676', '#ff3d00', '#3d5aff',
            '#1de9b6', '#ff9100', '#ea80fc', '#a7ffeb'
        ];

        function getTeamColor(teamName) {
            let hash = 0;
            for (let i = 0; i < teamName.length; i++) {
                hash = teamName.charCodeAt(i) + ((hash << 5) - hash);
            }
            const index = Math.abs(hash) % PLAYER_COLORS.length;
            return PLAYER_COLORS[index];
        }

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

        function formatTime(seconds) {
            const m = Math.floor(seconds / 60).toString().padStart(2, '0');
            const s = (seconds % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function logEvent(text, type = 'item') {
            const item = document.createElement('div');
            item.className = `log-item log-${type}`;
            const time = new Date().toLocaleTimeString();
            item.innerText = `[${time}] ${text}`;
            eventLog.appendChild(item);
            eventLog.scrollTop = eventLog.scrollHeight;
        }

        ws.onopen = () => {
            statusTitle.innerText = "WAITING FOR SERVER";
            statusBox.style.borderColor = "#ffca28";
            logEvent("Connected to Web Dashboard Server", "system");
        };

        ws.onmessage = (event) => {
            const gameState = JSON.parse(event.data);

            // 🎯 รับและคำนวณ GRID_SIZE ไดนามิกจาก Server เหมือน dashboard.py
            if (gameState.grid_size && gameState.grid_size !== GRID_SIZE) {
                GRID_SIZE = gameState.grid_size;
                CELL_SIZE = canvas.width / GRID_SIZE;
            }

            renderGame(gameState);
            updateDashboardInfo(gameState);
        };

        ws.onclose = () => {
            statusTitle.innerText = "DISCONNECTED";
            statusBox.style.borderColor = "#ff5252";
            logEvent("Disconnected from server", "hit");
        };

        function updateDashboardInfo(state) {
            if (state.time_left !== undefined) {
                timerText.innerText = formatTime(state.time_left);
            }

            if (state.status !== lastStatus) {
                lastStatus = state.status;
                if (state.status === "WAITING") {
                    statusTitle.innerText = "⏳ WAITING TO START";
                    statusBox.style.borderColor = "#ffca28";
                    logEvent("Game in lobby. Waiting for Host to start...", "system");
                } else if (state.status === "IN_GAME") {
                    statusTitle.innerText = "🚀 GAME IN PROGRESS";
                    statusBox.style.borderColor = "#00e5ff";
                    logEvent("🚀 Game started! Timer activated.", "system");
                } else if (state.status === "GAME_OVER") {
                    const winnerText = state.winner === "DRAW" ? "DRAW!" : `WINNER: ${state.winner}`;
                    statusTitle.innerText = `🏆 ${winnerText}`;
                    statusBox.style.borderColor = "#ff4081";
                    logEvent(`🏆 Game Over! Result: ${winnerText}`, "system");
                }
            }

            const players = state.players || {};
            Object.keys(players).forEach(team => {
                if (!lastPlayersState[team]) {
                    logEvent(`Player '${team}' joined the game.`, "join");
                } else if (lastPlayersState[team].hp > 0 && players[team].hp <= 0) {
                    logEvent(`💀 Player '${team}' was eliminated!`, "hit");
                } else if (lastPlayersState[team].hp > players[team].hp) {
                    const damage = lastPlayersState[team].hp - players[team].hp;
                    logEvent(`🎯 '${team}' took ${damage} damage! (HP: ${players[team].hp})`, "hit");
                }
            });
            lastPlayersState = JSON.parse(JSON.stringify(players));

            const teams = Object.keys(players);
            if (teams.length === 0) {
                playerTable.innerHTML = `<tr><td colspan="3" style="text-align:center; color:#666;">No players joined</td></tr>`;
                return;
            }

            playerTable.innerHTML = teams.map(team => {
                const p = players[team];
                const isAlive = p.hp > 0;
                const hpPercent = Math.max(0, p.hp);
                const teamColor = getTeamColor(team);
                const statusHtml = isAlive 
                    ? `<span class="status-alive">ALIVE</span>` 
                    : `<span class="status-dead">DEAD</span>`;

                return `
                    <tr>
                        <td>
                            <span class="color-badge" style="background-color: ${teamColor};"></span>
                            <b>${team}</b>
                        </td>
                        <td>
                            <div class="hp-bar-bg">
                                <div class="hp-bar-fill" style="width: ${hpPercent}%; background-color: ${teamColor};"></div>
                            </div>
                            <span style="font-size:12px; margin-left:5px;">${p.hp}</span>
                        </td>
                        <td>${statusHtml}</td>
                    </tr>
                `;
            }).join('');
        }

        function renderGame(state) {
            ctx.fillStyle = '#242424';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // วาดเส้น Grid ตามสเกล GRID_SIZE ล่าสุด
            ctx.strokeStyle = '#333333';
            ctx.lineWidth = 1;
            for (let i = 0; i <= GRID_SIZE; i++) {
                ctx.beginPath();
                ctx.moveTo(i * CELL_SIZE, 0);
                ctx.lineTo(i * CELL_SIZE, canvas.height);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, i * CELL_SIZE);
                ctx.lineTo(canvas.width, i * CELL_SIZE);
                ctx.stroke();
            }

            // วาดรถถัง
            const players = state.players || {};
            Object.keys(players).forEach(team => {
                const p = players[team];
                if (p.hp > 0) {
                    const centerX = p.x * CELL_SIZE + CELL_SIZE / 2;
                    const centerY = p.y * CELL_SIZE + CELL_SIZE / 2;
                    const radius = CELL_SIZE / 3;
                    const teamColor = getTeamColor(team);

                    ctx.beginPath();
                    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
                    ctx.fillStyle = teamColor;
                    ctx.fill();
                    ctx.lineWidth = 3;
                    ctx.strokeStyle = '#ffffff';
                    ctx.stroke();

                    // ปากกระบอกปืน
                    ctx.beginPath();
                    ctx.moveTo(centerX, centerY);
                    let gunX = centerX;
                    let gunY = centerY;
                    if (p.dir === "UP") gunY -= CELL_SIZE / 2.2;
                    else if (p.dir === "DOWN") gunY += CELL_SIZE / 2.2;
                    else if (p.dir === "LEFT") gunX -= CELL_SIZE / 2.2;
                    else if (p.dir === "RIGHT") gunX += CELL_SIZE / 2.2;

                    ctx.lineTo(gunX, gunY);
                    ctx.lineWidth = Math.max(2, CELL_SIZE / 8);
                    ctx.strokeStyle = '#ffffff';
                    ctx.stroke();

                    // ข้อความชื่อทีม
                    ctx.fillStyle = '#ffffff';
                    ctx.font = `bold ${Math.max(9, Math.floor(CELL_SIZE / 3))}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.fillText(team, centerX, p.y * CELL_SIZE + (CELL_SIZE > 30 ? 12 : 8));
                }
            });

            // วาดกระสุน
            const bullets = state.bullets || [];
            bullets.forEach(b => {
                const centerX = b.x * CELL_SIZE + CELL_SIZE / 2;
                const centerY = b.y * CELL_SIZE + CELL_SIZE / 2;

                ctx.beginPath();
                ctx.arc(centerX, centerY, Math.max(3, CELL_SIZE / 7), 0, 2 * Math.PI);
                ctx.fillStyle = '#ffeb3b';
                ctx.fill();
            });
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(HTML_CONTENT)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🌐 Web Dashboard running at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)