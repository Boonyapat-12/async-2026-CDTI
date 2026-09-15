import sys  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from pynput import keyboard  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

class KeyboardTankController:  # ประกาศคลาส KeyboardTankController สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self, team_name):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        self.team = team_name  # กำหนดหรือปรับค่าให้ self.team
        self.r = redis.Redis(host='172.20.56.216', port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        self.pubsub_channel = "game:state"  # กำหนดหรือปรับค่าให้ self.pubsub_channel
        self.command_channel = "game:commands"  # กำหนดหรือปรับค่าให้ self.command_channel
        
        # ตัวแปรสำหรับป้องกันการส่ง Action ซ้ำกันรวดเร็วเกินไปขณะกดปุ่มค้าง
        self.last_send_time = 0.0  # กำหนดหรือปรับค่าให้ self.last_send_time
        self.send_cooldown = 0.05  # ส่งคำสั่งห่างกันอย่างน้อย 0.05 วินาที

    def register(self):  # ประกาศฟังก์ชัน register สำหรับรวมขั้นตอนการทำงาน
        """ส่งคำสั่งลงทะเบียนผู้เล่นไปยัง Server"""
        cmd = {"team": self.team, "action": "REGISTER"}  # กำหนดหรือปรับค่าให้ cmd
        self.r.publish(self.command_channel, json.dumps(cmd))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        print(f"✅ Registered team '{self.team}' with Server!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    def send_action(self, action):  # ประกาศฟังก์ชัน send_action สำหรับรวมขั้นตอนการทำงาน
        """ส่งการกระทำไปยัง Server (Server จะเป็นผู้ตรวจสอบกฎ COOLDOWN และ LIMIT เอง)"""
        current_time = time.time()  # กำหนดหรือปรับค่าให้ current_time
        if current_time - self.last_send_time >= self.send_cooldown:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            cmd = {"team": self.team, "action": action}  # กำหนดหรือปรับค่าให้ cmd
            self.r.publish(self.command_channel, json.dumps(cmd))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            self.last_send_time = current_time  # กำหนดหรือปรับค่าให้ self.last_send_time

    def on_press(self, key):  # ประกาศฟังก์ชัน on_press สำหรับรวมขั้นตอนการทำงาน
        """Callback เมื่อมีการกดปุ่มบนคีย์บอร์ด"""
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            # ตรวจจับปุ่มลูกศร
            if key == keyboard.Key.up:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                self.send_action("UP")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            elif key == keyboard.Key.down:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                self.send_action("DOWN")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            elif key == keyboard.Key.left:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                self.send_action("LEFT")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            elif key == keyboard.Key.right:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                self.send_action("RIGHT")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            # ตรวจจับปุ่ม Spacebar
            elif key == keyboard.Key.space:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                self.send_action("FIRE")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        except Exception as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"Error handling key press: {e}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    def run(self):  # ประกาศฟังก์ชัน run สำหรับรวมขั้นตอนการทำงาน
        self.register()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        print("\n==================================================")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(f"🎮 MANUAL CONTROL READY: Team [{self.team}]")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("--------------------------------------------------")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" ⬆️  UP    : Move / Face UP")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" ⬇️  DOWN  : Move / Face DOWN")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" ⬅️  LEFT  : Move / Face LEFT")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" ➡️  RIGHT : Move / Face RIGHT")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" 🟩 SPACE  : FIRE")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("==================================================")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("Press Ctrl+C in terminal to exit.\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        # เริ่มต้นฟังการกดปุ่มบนคีย์บอร์ด
        listener = keyboard.Listener(on_press=self.on_press)  # กำหนดหรือปรับค่าให้ listener
        listener.start()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

        # วนลูปรับฟังสถานะจาก Server เพื่อแสดงผลสถานะใน Terminal
        pubsub = self.r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
        pubsub.subscribe(self.pubsub_channel)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                if message["type"] == "message":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    state = json.loads(message["data"])  # กำหนดหรือปรับค่าให้ state
                    status = state.get("status")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                    winner = state.get("winner")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

                    if status == "GAME_OVER":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        print("\n🏁 --- GAME OVER --- 🏁")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                        if winner == self.team:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                            print("🎉 YOU WIN! GREAT JOB!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                        elif winner == "DRAW":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                            print("🤝 MATCH DRAW!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                        else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
                            print(f"💀 YOU LOST! Winner is: {winner}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                        break  # หยุดการวนซ้ำทันที
        except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print("\nExiting player control...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        finally:  # ทำงานเก็บกวาดเสมอไม่ว่าผลลัพธ์จะสำเร็จหรือเกิดข้อผิดพลาด
            listener.stop()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    # ตรวจสอบการรับชื่อทีมผ่าน Argument
    if len(sys.argv) > 1:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        team_name = sys.argv[1]  # กำหนดหรือปรับค่าให้ team_name
    else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
        team_name = input("Enter your Team Name: ").strip()  # กำหนดหรือปรับค่าให้ team_name
        if not team_name:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            team_name = "Player_1"  # กำหนดหรือปรับค่าให้ team_name

    player = KeyboardTankController(team_name)  # กำหนดหรือปรับค่าให้ player
    player.run()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน