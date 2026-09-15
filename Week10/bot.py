import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import random  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import sys  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

class TankBot:  # ประกาศคลาส TankBot สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self, team_name):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        self.team_name = team_name  # กำหนดหรือปรับค่าให้ self.team_name
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        self.pubsub_channel = "game:state"  # กำหนดหรือปรับค่าให้ self.pubsub_channel
        self.command_channel = "game:commands"  # กำหนดหรือปรับค่าให้ self.command_channel
        self.current_state = None  # กำหนดหรือปรับค่าให้ self.current_state

    async def send_action(self, action):  # ประกาศฟังก์ชัน send_action สำหรับรวมขั้นตอนการทำงาน
        cmd = {  # กำหนดหรือปรับค่าให้ cmd
            "team": self.team_name,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "action": action  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        await self.r.publish(self.command_channel, json.dumps(cmd))  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    async def listen_game_state(self):  # ประกาศฟังก์ชัน listen_game_state สำหรับรวมขั้นตอนการทำงาน
        pubsub = self.r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
        await pubsub.subscribe(self.pubsub_channel)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        async for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if message["type"] == "message":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                self.current_state = json.loads(message["data"])  # กำหนดหรือปรับค่าให้ self.current_state

    async def brain_loop(self):  # ประกาศฟังก์ชัน brain_loop สำหรับรวมขั้นตอนการทำงาน
        await asyncio.sleep(0.5)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        await self.send_action("REGISTER")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"[{self.team_name}] Registered & Waiting in Lobby...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
            if self.current_state:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                game_status = self.current_state.get("status", "WAITING")  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                players = self.current_state.get("players", {})  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                my_info = players.get(self.team_name)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

                if game_status == "IN_GAME" and my_info and my_info["hp"] > 0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    actions = ["UP", "DOWN", "LEFT", "RIGHT", "FIRE"]  # กำหนดหรือปรับค่าให้ actions
                    chosen = random.choice(actions)  # กำหนดหรือปรับค่าให้ chosen
                    await self.send_action(chosen)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                
                elif game_status == "GAME_OVER":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    print(f"[{self.team_name}] Game Over! Winner: {self.current_state.get('winner')}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                    break  # หยุดการวนซ้ำทันที

            await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    async def run(self):  # ประกาศฟังก์ชัน run สำหรับรวมขั้นตอนการทำงาน
        await asyncio.gather(self.listen_game_state(), self.brain_loop())  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    team = sys.argv[1] if len(sys.argv) > 1 else f"Team_{random.randint(10, 99)}"  # กำหนดหรือปรับค่าให้ team
    bot = TankBot(team_name=team)  # กำหนดหรือปรับค่าให้ bot
    asyncio.run(bot.run())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน