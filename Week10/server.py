import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import random  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import sys  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

GRID_SIZE = 50           # กำหนดขนาดของตารางเกม (50x50)
TICK_RATE = 0.2          # 1 Tick = 0.2 วินาที (5 FPS)
FIRE_COOLDOWN = 0.5      # คุมที่ Server: ยิงได้ทุกๆ 0.5 วินาทีเท่านั้น
MAX_ACTIVE_BULLETS = 2   # คุมที่ Server: กระสุนในสนามของแต่ละทีมห้ามเกิน 2 นัด
GAME_DURATION = 180      # เวลาแข่งขันสูงสุด: 3 นาที (180 วินาที)

class SecureTankGameServer:  # ประกาศคลาส SecureTankGameServer สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        self.pubsub_channel = "game:state"  # กำหนดหรือปรับค่าให้ self.pubsub_channel
        self.command_channel = "game:commands"  # กำหนดหรือปรับค่าให้ self.command_channel
        self.players = {}  # กำหนดหรือปรับค่าให้ self.players
        self.bullets = []  # กำหนดหรือปรับค่าให้ self.bullets
        self.status = "WAITING"  # กำหนดหรือปรับค่าให้ self.status
        self.winner = None  # กำหนดหรือปรับค่าให้ self.winner
        self.start_time = None  # กำหนดหรือปรับค่าให้ self.start_time
        self.time_left = GAME_DURATION  # กำหนดหรือปรับค่าให้ self.time_left
        self.countdown = 0  # กำหนดหรือปรับค่าให้ self.countdown

    async def init_game(self):  # ประกาศฟังก์ชัน init_game สำหรับรวมขั้นตอนการทำงาน
        await self.r.flushdb()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print("==================================================")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" 🔒 SECURE TANK SERVER (MULTISHOT & RESTART ENABLED)")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("==================================================")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    async def reset_game(self):  # ประกาศฟังก์ชัน reset_game สำหรับรวมขั้นตอนการทำงาน
        """🧹 รีเซ็ตสถานะทั้งหมดกลับสู่เริ่มต้นเพื่อเตรียมเล่นรอบใหม่"""
        self.status = "WAITING"  # กำหนดหรือปรับค่าให้ self.status
        self.winner = None  # กำหนดหรือปรับค่าให้ self.winner
        self.time_left = GAME_DURATION  # กำหนดหรือปรับค่าให้ self.time_left
        self.bullets = []  # กำหนดหรือปรับค่าให้ self.bullets
        self.players = {}  # เคลียร์ผู้เล่นเดิมเพื่อให้ลงทะเบียนใหม่
        self.start_time = None  # กำหนดหรือปรับค่าให้ self.start_time
        self.countdown = 0  # กำหนดหรือปรับค่าให้ self.countdown
        print("\n🧹 [RESET] Game completely reset! Waiting for players to re-register...\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    async def start_countdown(self):  # ประกาศฟังก์ชัน start_countdown สำหรับรวมขั้นตอนการทำงาน
        """⏱️ นับถอยหลัง 3 2 1 ก่อนเริ่มเกมอย่างเป็นทางการ"""
        self.status = "COUNTDOWN"  # กำหนดหรือปรับค่าให้ self.status
        for count in range(3, 0, -1):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            self.countdown = count  # กำหนดหรือปรับค่าให้ self.countdown
            print(f"⏱️ Game starting in: {count}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            await asyncio.sleep(1.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        
        self.status = "IN_GAME"  # กำหนดหรือปรับค่าให้ self.status
        self.start_time = time.time()  # กำหนดหรือปรับค่าให้ self.start_time
        self.countdown = 0  # กำหนดหรือปรับค่าให้ self.countdown
        print("\n🚀🚀🚀 GAME STARTED! 3-MINUTE TIMER RUNNING 🚀🚀🚀\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    async def listen_commands(self):  # ประกาศฟังก์ชัน listen_commands สำหรับรวมขั้นตอนการทำงาน
        pubsub = self.r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
        await pubsub.subscribe(self.command_channel)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        
        async for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if message["type"] == "message":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
                    raw_data = json.loads(message["data"])  # กำหนดหรือปรับค่าให้ raw_data
                    team = str(raw_data.get("team", "")).strip()  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                    action = str(raw_data.get("action", "")).strip().upper()  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                    
                    if not team:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        continue  # ข้ามไปเริ่มรอบการวนซ้ำถัดไป

                    # รองรับทั้งคีย์คำสั่ง REGISTER และ JOIN
                    if action in ["REGISTER", "JOIN"] and team not in self.players:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        self.players[team] = {  # กำหนดหรือปรับค่าให้ self.players[team]
                            "x": random.randint(0, GRID_SIZE - 1),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "y": random.randint(0, GRID_SIZE - 1),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "hp": 100,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "dir": "UP",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "last_fire_time": 0.0,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "next_action": None  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
                        print(f"📌 [REGISTERED] Team '{team}' joined.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                    
                    elif self.status == "IN_GAME" and team in self.players and self.players[team]["hp"] > 0:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                        ALLOWED_ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "FIRE"]  # กำหนดหรือปรับค่าให้ ALLOWED_ACTIONS
                        if action in ALLOWED_ACTIONS:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                            self.players[team]["next_action"] = action  # กำหนดหรือปรับค่าให้ self.players[team]["next_action"]

                except Exception as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
                    print(f"⚠️ Command Error ignored: {e}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    def process_buffered_actions(self):  # ประกาศฟังก์ชัน process_buffered_actions สำหรับรวมขั้นตอนการทำงาน
        current_time = time.time()  # กำหนดหรือปรับค่าให้ current_time
        
        for team, p in self.players.items():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if p["hp"] <= 0 or not p["next_action"]:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                continue  # ข้ามไปเริ่มรอบการวนซ้ำถัดไป

            action = p["next_action"]  # กำหนดหรือปรับค่าให้ action
            p["next_action"] = None  # กำหนดหรือปรับค่าให้ p["next_action"]

            if action in ["UP", "DOWN", "LEFT", "RIGHT"]:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                p["dir"] = action  # กำหนดหรือปรับค่าให้ p["dir"]
                if action == "UP" and p["y"] > 0: p["y"] -= 1  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                elif action == "DOWN" and p["y"] < GRID_SIZE - 1: p["y"] += 1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                elif action == "LEFT" and p["x"] > 0: p["x"] -= 1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                elif action == "RIGHT" and p["x"] < GRID_SIZE - 1: p["x"] += 1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป

            elif action == "FIRE":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                team_bullet_count = sum(1 for b in self.bullets if b["owner"] == team)  # กำหนดหรือปรับค่าให้ team_bullet_count
                is_cooldown_passed = (current_time - p["last_fire_time"]) >= FIRE_COOLDOWN  # กำหนดหรือปรับค่าให้ is_cooldown_passed
                is_under_bullet_limit = team_bullet_count < MAX_ACTIVE_BULLETS  # กำหนดหรือปรับค่าให้ is_under_bullet_limit

                if is_cooldown_passed and is_under_bullet_limit:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    p["last_fire_time"] = current_time  # กำหนดหรือปรับค่าให้ p["last_fire_time"]
                    
                    dx, dy = 0, 0  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                    if p["dir"] == "UP": dy = -1  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    elif p["dir"] == "DOWN": dy = 1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    elif p["dir"] == "LEFT": dx = -1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    elif p["dir"] == "RIGHT": dx = 1  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    
                    bullet_x, bullet_y = p["x"] + dx, p["y"] + dy  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                    if 0 <= bullet_x < GRID_SIZE and 0 <= bullet_y < GRID_SIZE:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        self.bullets.append({  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
                            "x": bullet_x, "y": bullet_y,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "dx": dx, "dy": dy, "owner": team  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                        })  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    def update_bullets(self):  # ประกาศฟังก์ชัน update_bullets สำหรับรวมขั้นตอนการทำงาน
        remaining_bullets = []  # กำหนดหรือปรับค่าให้ remaining_bullets
        for b in self.bullets:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            hit = False  # กำหนดหรือปรับค่าให้ hit
            for team, p in list(self.players.items()):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                if p["hp"] > 0 and b["x"] == p["x"] and b["y"] == p["y"] and b["owner"] != team:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    p["hp"] = max(0, p["hp"] - 20)  # กำหนดหรือปรับค่าให้ p["hp"]
                    if p["hp"] <= 0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        print(f"💀 [DESTROYED] Team '{team}' eliminated!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                    hit = True  # กำหนดหรือปรับค่าให้ hit
                    break  # หยุดการวนซ้ำทันที
            
            if hit: continue  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน

            b["x"] += b["dx"]  # กำหนดหรือปรับค่าให้ b["x"]
            b["y"] += b["dy"]  # กำหนดหรือปรับค่าให้ b["y"]
            if 0 <= b["x"] < GRID_SIZE and 0 <= b["y"] < GRID_SIZE:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                remaining_bullets.append(b)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
                
        self.bullets = remaining_bullets  # กำหนดหรือปรับค่าให้ self.bullets

    def check_winner_and_timer(self):  # ประกาศฟังก์ชัน check_winner_and_timer สำหรับรวมขั้นตอนการทำงาน
        """⏱️ ตรวจสอบเงื่อนไขผู้ชนะ และเวลาถอยหลัง 3 นาที"""
        if self.status != "IN_GAME":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        # 1. อัปเดตเวลาที่เหลือ
        elapsed_time = time.time() - self.start_time  # กำหนดหรือปรับค่าให้ elapsed_time
        self.time_left = max(0, int(GAME_DURATION - elapsed_time))  # กำหนดหรือปรับค่าให้ self.time_left

        alive_teams = {team: p for team, p in self.players.items() if p["hp"] > 0}  # กำหนดหรือปรับค่าให้ alive_teams

        # 2. กรณีเหลือรอดเพียงทีมเดียว ก่อนหมดเวลา
        if len(self.players) >= 2 and len(alive_teams) == 1:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            self.winner = list(alive_teams.keys())[0]  # กำหนดหรือปรับค่าให้ self.winner
            self.status = "GAME_OVER"  # กำหนดหรือปรับค่าให้ self.status
            print(f"\n🏆 [GAME OVER] Winner (Last Standing): {self.winner}\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            return  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        elif len(self.players) >= 2 and len(alive_teams) == 0:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
            self.winner = "DRAW"  # กำหนดหรือปรับค่าให้ self.winner
            self.status = "GAME_OVER"  # กำหนดหรือปรับค่าให้ self.status
            print("\n💀 [GAME OVER] All players eliminated! Draw!\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            return  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        # 3. ⏱️ กรณีหมดเวลา 3 นาที (Timeout)
        if self.time_left <= 0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            self.status = "GAME_OVER"  # กำหนดหรือปรับค่าให้ self.status
            
            if not alive_teams:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                self.winner = "DRAW"  # กำหนดหรือปรับค่าให้ self.winner
                print("\n⏰ [TIME'S UP] Match ended - Draw (No survivors)!\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                return  # ส่งผลลัพธ์กลับไปยังผู้เรียก

            # หาค่า HP สูงสุด
            max_hp = max(p["hp"] for p in alive_teams.values())  # กำหนดหรือปรับค่าให้ max_hp
            top_teams = [team for team, p in alive_teams.items() if p["hp"] == max_hp]  # กำหนดหรือปรับค่าให้ top_teams

            if len(top_teams) == 1:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                self.winner = top_teams[0]  # กำหนดหรือปรับค่าให้ self.winner
                print(f"\n⏰ [TIME'S UP] Winner by Most HP ({max_hp} HP): {self.winner}\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
                self.winner = "DRAW"  # กำหนดหรือปรับค่าให้ self.winner
                print(f"\n⏰ [TIME'S UP] Match ended in Draw! Highest HP tied at {max_hp}.\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    async def wait_for_host_input(self):  # ประกาศฟังก์ชัน wait_for_host_input สำหรับรวมขั้นตอนการทำงาน
        """🔄 Loop สำหรับรอการกด [ENTER] เพื่อเริ่มเกม / เล่นรอบใหม่"""
        loop = asyncio.get_event_loop()  # กำหนดหรือปรับค่าให้ loop
        while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
            if self.status == "GAME_OVER":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                prompt = "\n👉 Press [ENTER] to RESTART / PLAY AGAIN 👈\n"  # กำหนดหรือปรับค่าให้ prompt
            else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
                prompt = "\n👉 Press [ENTER] when players have joined to START THE GAME! 👈\n"  # กำหนดหรือปรับค่าให้ prompt
            
            await loop.run_in_executor(None, sys.stdin.readline)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

            if self.status == "GAME_OVER":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                await self.reset_game()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

            elif self.status == "WAITING":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                if len(self.players) == 0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    print("⚠️ No bots/players connected yet! Please wait for players to join.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
                    await self.start_countdown()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    async def game_loop(self):  # ประกาศฟังก์ชัน game_loop สำหรับรวมขั้นตอนการทำงาน
        while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
            if self.status == "IN_GAME":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                self.process_buffered_actions()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                self.update_bullets()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                self.check_winner_and_timer()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            
            game_state = {  # กำหนดหรือปรับค่าให้ game_state
                "grid_size": GRID_SIZE,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "players": self.players,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "bullets": self.bullets,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "status": self.status,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "winner": self.winner,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "time_left": self.time_left,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "countdown": self.countdown  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            await self.r.publish(self.pubsub_channel, json.dumps(game_state))  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            await asyncio.sleep(TICK_RATE)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    async def run(self):  # ประกาศฟังก์ชัน run สำหรับรวมขั้นตอนการทำงาน
        await self.init_game()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        asyncio.create_task(self.listen_commands())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        asyncio.create_task(self.game_loop())  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        await self.wait_for_host_input()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    server = SecureTankGameServer()  # กำหนดหรือปรับค่าให้ server
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(server.run())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("\n🛑 Server closed.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        sys.exit(0)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน