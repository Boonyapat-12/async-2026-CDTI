import asyncio
import json
import random
import sys
import time
import redis.asyncio as redis

GRID_SIZE = 10           # กำหนดขนาดของตารางเกม (10x10)
TICK_RATE = 0.2          # 1 Tick = 0.2 วินาที (5 FPS)
FIRE_COOLDOWN = 0.5      # คุมที่ Server: ยิงได้ทุกๆ 0.5 วินาทีเท่านั้น
MAX_ACTIVE_BULLETS = 2   # คุมที่ Server: กระสุนในสนามของแต่ละทีมห้ามเกิน 2 นัด
GAME_DURATION = 180      # เวลาแข่งขันสูงสุด: 3 นาที (180 วินาที)

class SecureTankGameServer:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.pubsub_channel = "game:state"
        self.command_channel = "game:commands"
        self.players = {}  
        self.bullets = []
        self.status = "WAITING"
        self.winner = None
        self.start_time = None
        self.time_left = GAME_DURATION
        self.countdown = 0

    async def init_game(self):
        await self.r.flushdb()
        print("==================================================")
        print(" 🔒 SECURE TANK SERVER (MULTISHOT & RESTART ENABLED)")
        print("==================================================")

    async def reset_game(self):
        """🧹 รีเซ็ตสถานะทั้งหมดกลับสู่เริ่มต้นเพื่อเตรียมเล่นรอบใหม่"""
        self.status = "WAITING"
        self.winner = None
        self.time_left = GAME_DURATION
        self.bullets = []
        self.players = {}  # เคลียร์ผู้เล่นเดิมเพื่อให้ลงทะเบียนใหม่
        self.start_time = None
        self.countdown = 0
        print("\n🧹 [RESET] Game completely reset! Waiting for players to re-register...\n")

    async def start_countdown(self):
        """⏱️ นับถอยหลัง 3 2 1 ก่อนเริ่มเกมอย่างเป็นทางการ"""
        self.status = "COUNTDOWN"
        for count in range(3, 0, -1):
            self.countdown = count
            print(f"⏱️ Game starting in: {count}...")
            await asyncio.sleep(1.0)
        
        self.status = "IN_GAME"
        self.start_time = time.time()
        self.countdown = 0
        print("\n🚀🚀🚀 GAME STARTED! 3-MINUTE TIMER RUNNING 🚀🚀🚀\n")

    async def listen_commands(self):
        pubsub = self.r.pubsub()
        await pubsub.subscribe(self.command_channel)
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    raw_data = json.loads(message["data"])
                    team = str(raw_data.get("team", "")).strip()
                    action = str(raw_data.get("action", "")).strip().upper()
                    
                    if not team:
                        continue

                    # รองรับทั้งคีย์คำสั่ง REGISTER และ JOIN
                    if action in ["REGISTER", "JOIN"] and team not in self.players:
                        self.players[team] = {
                            "x": random.randint(0, GRID_SIZE - 1),
                            "y": random.randint(0, GRID_SIZE - 1),
                            "hp": 100,
                            "dir": "UP",
                            "last_fire_time": 0.0,
                            "next_action": None
                        }
                        print(f"📌 [REGISTERED] Team '{team}' joined.")
                    
                    elif self.status == "IN_GAME" and team in self.players and self.players[team]["hp"] > 0:
                        ALLOWED_ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "FIRE"]
                        if action in ALLOWED_ACTIONS:
                            self.players[team]["next_action"] = action

                except Exception as e:
                    print(f"⚠️ Command Error ignored: {e}")

    def process_buffered_actions(self):
        current_time = time.time()
        
        for team, p in self.players.items():
            if p["hp"] <= 0 or not p["next_action"]:
                continue

            action = p["next_action"]
            p["next_action"] = None

            if action in ["UP", "DOWN", "LEFT", "RIGHT"]:
                p["dir"] = action
                if action == "UP" and p["y"] > 0: p["y"] -= 1
                elif action == "DOWN" and p["y"] < GRID_SIZE - 1: p["y"] += 1
                elif action == "LEFT" and p["x"] > 0: p["x"] -= 1
                elif action == "RIGHT" and p["x"] < GRID_SIZE - 1: p["x"] += 1

            elif action == "FIRE":
                team_bullet_count = sum(1 for b in self.bullets if b["owner"] == team)
                is_cooldown_passed = (current_time - p["last_fire_time"]) >= FIRE_COOLDOWN
                is_under_bullet_limit = team_bullet_count < MAX_ACTIVE_BULLETS

                if is_cooldown_passed and is_under_bullet_limit:
                    p["last_fire_time"] = current_time
                    
                    dx, dy = 0, 0
                    if p["dir"] == "UP": dy = -1
                    elif p["dir"] == "DOWN": dy = 1
                    elif p["dir"] == "LEFT": dx = -1
                    elif p["dir"] == "RIGHT": dx = 1
                    
                    bullet_x, bullet_y = p["x"] + dx, p["y"] + dy
                    if 0 <= bullet_x < GRID_SIZE and 0 <= bullet_y < GRID_SIZE:
                        self.bullets.append({
                            "x": bullet_x, "y": bullet_y,
                            "dx": dx, "dy": dy, "owner": team
                        })

    def update_bullets(self):
        remaining_bullets = []
        for b in self.bullets:
            hit = False
            for team, p in list(self.players.items()):
                if p["hp"] > 0 and b["x"] == p["x"] and b["y"] == p["y"] and b["owner"] != team:
                    p["hp"] = max(0, p["hp"] - 20)
                    if p["hp"] <= 0:
                        print(f"💀 [DESTROYED] Team '{team}' eliminated!")
                    hit = True
                    break
            
            if hit: continue

            b["x"] += b["dx"]
            b["y"] += b["dy"]
            if 0 <= b["x"] < GRID_SIZE and 0 <= b["y"] < GRID_SIZE:
                remaining_bullets.append(b)
                
        self.bullets = remaining_bullets

    def check_winner_and_timer(self):
        """⏱️ ตรวจสอบเงื่อนไขผู้ชนะ และเวลาถอยหลัง 3 นาที"""
        if self.status != "IN_GAME":
            return

        # 1. อัปเดตเวลาที่เหลือ
        elapsed_time = time.time() - self.start_time
        self.time_left = max(0, int(GAME_DURATION - elapsed_time))

        alive_teams = {team: p for team, p in self.players.items() if p["hp"] > 0}

        # 2. กรณีเหลือรอดเพียงทีมเดียว ก่อนหมดเวลา
        if len(self.players) >= 2 and len(alive_teams) == 1:
            self.winner = list(alive_teams.keys())[0]
            self.status = "GAME_OVER"
            print(f"\n🏆 [GAME OVER] Winner (Last Standing): {self.winner}\n")
            return

        elif len(self.players) >= 2 and len(alive_teams) == 0:
            self.winner = "DRAW"
            self.status = "GAME_OVER"
            print("\n💀 [GAME OVER] All players eliminated! Draw!\n")
            return

        # 3. ⏱️ กรณีหมดเวลา 3 นาที (Timeout)
        if self.time_left <= 0:
            self.status = "GAME_OVER"
            
            if not alive_teams:
                self.winner = "DRAW"
                print("\n⏰ [TIME'S UP] Match ended - Draw (No survivors)!\n")
                return

            # หาค่า HP สูงสุด
            max_hp = max(p["hp"] for p in alive_teams.values())
            top_teams = [team for team, p in alive_teams.items() if p["hp"] == max_hp]

            if len(top_teams) == 1:
                self.winner = top_teams[0]
                print(f"\n⏰ [TIME'S UP] Winner by Most HP ({max_hp} HP): {self.winner}\n")
            else:
                self.winner = "DRAW"
                print(f"\n⏰ [TIME'S UP] Match ended in Draw! Highest HP tied at {max_hp}.\n")

    async def wait_for_host_input(self):
        """🔄 Loop สำหรับรอการกด [ENTER] เพื่อเริ่มเกม / เล่นรอบใหม่"""
        loop = asyncio.get_event_loop()
        while True:
            if self.status == "GAME_OVER":
                prompt = "\n👉 Press [ENTER] to RESTART / PLAY AGAIN 👈\n"
            else:
                prompt = "\n👉 Press [ENTER] when players have joined to START THE GAME! 👈\n"
            
            await loop.run_in_executor(None, sys.stdin.readline)

            if self.status == "GAME_OVER":
                await self.reset_game()

            elif self.status == "WAITING":
                if len(self.players) == 0:
                    print("⚠️ No bots/players connected yet! Please wait for players to join.")
                else:
                    await self.start_countdown()

    async def game_loop(self):
        while True:
            if self.status == "IN_GAME":
                self.process_buffered_actions()
                self.update_bullets()
                self.check_winner_and_timer()
            
            game_state = {
                "grid_size": GRID_SIZE,
                "players": self.players,
                "bullets": self.bullets,
                "status": self.status,
                "winner": self.winner,
                "time_left": self.time_left,
                "countdown": self.countdown
            }
            await self.r.publish(self.pubsub_channel, json.dumps(game_state))
            await asyncio.sleep(TICK_RATE)

    async def run(self):
        await self.init_game()
        asyncio.create_task(self.listen_commands())
        asyncio.create_task(self.game_loop())
        await self.wait_for_host_input()

if __name__ == "__main__":
    server = SecureTankGameServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n🛑 Server closed.")
        sys.exit(0)