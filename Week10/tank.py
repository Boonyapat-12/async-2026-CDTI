import sys
import json
import time
import redis
from pynput import keyboard

class KeyboardTankController:
    def __init__(self, team_name):
        self.team = team_name
        self.r = redis.Redis(host='172.20.56.216', port=6379, db=0, decode_responses=True)
        self.pubsub_channel = "game:state"
        self.command_channel = "game:commands"
        
        # ตัวแปรสำหรับป้องกันการส่ง Action ซ้ำกันรวดเร็วเกินไปขณะกดปุ่มค้าง
        self.last_send_time = 0.0
        self.send_cooldown = 0.05  # ส่งคำสั่งห่างกันอย่างน้อย 0.05 วินาที

    def register(self):
        """ส่งคำสั่งลงทะเบียนผู้เล่นไปยัง Server"""
        cmd = {"team": self.team, "action": "REGISTER"}
        self.r.publish(self.command_channel, json.dumps(cmd))
        print(f"✅ Registered team '{self.team}' with Server!")

    def send_action(self, action):
        """ส่งการกระทำไปยัง Server (Server จะเป็นผู้ตรวจสอบกฎ COOLDOWN และ LIMIT เอง)"""
        current_time = time.time()
        if current_time - self.last_send_time >= self.send_cooldown:
            cmd = {"team": self.team, "action": action}
            self.r.publish(self.command_channel, json.dumps(cmd))
            self.last_send_time = current_time

    def on_press(self, key):
        """Callback เมื่อมีการกดปุ่มบนคีย์บอร์ด"""
        try:
            # ตรวจจับปุ่มลูกศร
            if key == keyboard.Key.up:
                self.send_action("UP")
            elif key == keyboard.Key.down:
                self.send_action("DOWN")
            elif key == keyboard.Key.left:
                self.send_action("LEFT")
            elif key == keyboard.Key.right:
                self.send_action("RIGHT")
            # ตรวจจับปุ่ม Spacebar
            elif key == keyboard.Key.space:
                self.send_action("FIRE")
        except Exception as e:
            print(f"Error handling key press: {e}")

    def run(self):
        self.register()
        print("\n==================================================")
        print(f"🎮 MANUAL CONTROL READY: Team [{self.team}]")
        print("--------------------------------------------------")
        print(" ⬆️  UP    : Move / Face UP")
        print(" ⬇️  DOWN  : Move / Face DOWN")
        print(" ⬅️  LEFT  : Move / Face LEFT")
        print(" ➡️  RIGHT : Move / Face RIGHT")
        print(" 🟩 SPACE  : FIRE")
        print("==================================================")
        print("Press Ctrl+C in terminal to exit.\n")

        # เริ่มต้นฟังการกดปุ่มบนคีย์บอร์ด
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        # วนลูปรับฟังสถานะจาก Server เพื่อแสดงผลสถานะใน Terminal
        pubsub = self.r.pubsub()
        pubsub.subscribe(self.pubsub_channel)

        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    state = json.loads(message["data"])
                    status = state.get("status")
                    winner = state.get("winner")

                    if status == "GAME_OVER":
                        print("\n🏁 --- GAME OVER --- 🏁")
                        if winner == self.team:
                            print("🎉 YOU WIN! GREAT JOB!")
                        elif winner == "DRAW":
                            print("🤝 MATCH DRAW!")
                        else:
                            print(f"💀 YOU LOST! Winner is: {winner}")
                        break
        except KeyboardInterrupt:
            print("\nExiting player control...")
        finally:
            listener.stop()

if __name__ == "__main__":
    # ตรวจสอบการรับชื่อทีมผ่าน Argument
    if len(sys.argv) > 1:
        team_name = sys.argv[1]
    else:
        team_name = input("Enter your Team Name: ").strip()
        if not team_name:
            team_name = "Player_1"

    player = KeyboardTankController(team_name)
    player.run()