import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import os  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

class GameDashboard:  # ประกาศคลาส GameDashboard สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def __init__(self):  # ประกาศฟังก์ชัน __init__ สำหรับรวมขั้นตอนการทำงาน
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        self.pubsub_channel = "game:state"  # กำหนดหรือปรับค่าให้ self.pubsub_channel

    def clear_screen(self):  # ประกาศฟังก์ชัน clear_screen สำหรับรวมขั้นตอนการทำงาน
        os.system('cls' if os.name == 'nt' else 'clear')  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    def render_board(self, state):  # ประกาศฟังก์ชัน render_board สำหรับรวมขั้นตอนการทำงาน
        grid_size = state.get("grid_size", 10)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        players = state.get("players", {})  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        bullets = state.get("bullets", [])  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        is_over = state.get("is_over", False)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        winner = state.get("winner", None)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

        grid = [[" . " for _ in range(grid_size)] for _ in range(grid_size)]  # กำหนดหรือปรับค่าให้ grid
        
        for b in bullets:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            grid[b["y"]][b["x"]] = " * "  # กำหนดหรือปรับค่าให้ grid[b["y"]][b["x"]]

        for team_name, info in players.items():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if info.get("hp", 0) > 0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                grid[info["y"]][info["x"]] = f" {team_name[0].upper()} "  # กำหนดหรือปรับค่าให้ grid[info["y"]][info["x"]]

        self.clear_screen()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        print("=" * 40)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print(" 🎮 TANK BATTLE ARENA (LAST TANK STANDING) ")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("=" * 40)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("┌" + "─" * (grid_size * 3) + "┐")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        for row in grid:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            print("│" + "".join(row) + "│")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        print("└" + "─" * (grid_size * 3) + "┘")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
        print("\n📊 TEAM STATUS & HP:")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        for team_name, info in players.items():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            hp = info["hp"]  # กำหนดหรือปรับค่าให้ hp
            status = "ALIVE" if hp > 0 else "DESTROYED 💀"  # กำหนดหรือปรับค่าให้ status
            bar_count = max(0, hp // 10)  # กำหนดหรือปรับค่าให้ bar_count
            hp_bar = "█" * bar_count + "░" * (10 - bar_count)  # กำหนดหรือปรับค่าให้ hp_bar
            print(f"   • [{team_name[0].upper()}] {team_name:10s} | HP: {hp:3d} [{hp_bar}] | Status: {status}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        # แสดงป้ายประกาศผู้ชนะเมื่อเกมจบ
        if is_over:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            print("\n" + "=" * 40)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            print(f" 🏆 GAME OVER! WINNER: {winner} 🏆")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            print("=" * 40)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    async def run(self):  # ประกาศฟังก์ชัน run สำหรับรวมขั้นตอนการทำงาน
        pubsub = self.r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
        await pubsub.subscribe(self.pubsub_channel)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        async for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if message["type"] == "message":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                state = json.loads(message["data"])  # กำหนดหรือปรับค่าให้ state
                self.render_board(state)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    dashboard = GameDashboard()  # กำหนดหรือปรับค่าให้ dashboard
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(dashboard.run())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        pass  # เว้นพื้นที่ไว้โดยยังไม่เพิ่มการทำงานในบล็อกนี้