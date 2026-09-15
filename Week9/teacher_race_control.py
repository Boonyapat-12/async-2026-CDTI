import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from rich.live import Live  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich.panel import Panel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich.table import Table  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich.console import Console  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

REDIS_HOST = 'localhost'  # IP เครื่องครู
TOTAL_GROUPS = 8          # จำนวนกลุ่มทั้งหมด (g01 - g08)
FINISH_DISTANCE = 10000.0 # 10 km (10,000 เมตร)

# ตัวแปร Global สำหรับเก็บข้อมูลการแข่งขัน
race_data = {}  # กำหนดหรือปรับค่าให้ race_data
leaderboard = []  # กำหนดหรือปรับค่าให้ leaderboard

def reset_race_state():  # ประกาศฟังก์ชัน reset_race_state สำหรับรวมขั้นตอนการทำงาน
    """ล้างข้อมูลการแข่งขันเพื่อเตรียมพร้อมสำหรับรอบใหม่"""
    global race_data, leaderboard  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    race_data = {  # กำหนดหรือปรับค่าให้ race_data
        f"g{i:02d}": {"distance": 0.0, "speed": 0.0, "finished": False}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        for i in range(1, TOTAL_GROUPS + 1)  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    leaderboard = []  # กำหนดหรือปรับค่าให้ leaderboard

def generate_race_ui(status_text):  # ประกาศฟังก์ชัน generate_race_ui สำหรับรวมขั้นตอนการทำงาน
    """สร้าง UI หน้าจอตารางการแข่งขันแบบ Real-time"""
    table = Table(title="🏎️ F1 GRAND PRIX - LIVE TELEMETRY LEADERBOARD", expand=True)  # กำหนดหรือปรับค่าให้ table
    table.add_column("Group", style="cyan", width=8)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_column("Live Progress (10,000 M)", width=40)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_column("Distance", justify="right")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_column("Speed", justify="right")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_column("Status", justify="center")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    # เรียงลำดับกลุ่มตามระยะทาง (Leaderboard)
    sorted_groups = sorted(race_data.items(), key=lambda x: x[1]['distance'], reverse=True)  # กำหนดหรือปรับค่าให้ sorted_groups

    for rank, (group_id, data) in enumerate(sorted_groups, 1):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        dist = data['distance']  # กำหนดหรือปรับค่าให้ dist
        pct = min(100.0, (dist / FINISH_DISTANCE) * 100.0)  # กำหนดหรือปรับค่าให้ pct
        
        # สร้าง Progress Bar
        bar_len = int(pct / 100 * 25)  # กำหนดหรือปรับค่าให้ bar_len
        bar_str = "█" * bar_len + "░" * (25 - bar_len)  # กำหนดหรือปรับค่าให้ bar_str
        
        speed_str = f"{data['speed']} km/h"  # กำหนดหรือปรับค่าให้ speed_str
        
        if data['finished']:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            rank_idx = leaderboard.index(group_id) + 1 if group_id in leaderboard else 'FIN'  # กำหนดหรือปรับค่าให้ rank_idx
            status = f"[bold green]🏆 FINISHED (#{rank_idx})[/bold green]"  # กำหนดหรือปรับค่าให้ status
        elif dist > 0:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
            status = f"[yellow]RACING (P{rank})[/yellow]"  # กำหนดหรือปรับค่าให้ status
        else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
            status = "[dim]GRID (WAITING)[/dim]"  # กำหนดหรือปรับค่าให้ status

        table.add_row(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            f"[bold]{group_id.upper()}[/bold]",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            f"[{bar_str}] {pct:.1f}%",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            f"{dist:.1f} m",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            speed_str,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            status  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    return Panel(table, title=f"🚦 Race Status: [bold green]{status_text}[/bold green]", border_style="bright_blue")  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def listen_to_pubsub(r):  # ประกาศฟังก์ชัน listen_to_pubsub สำหรับรวมขั้นตอนการทำงาน
    """ดักฟัง Pub/Sub ข้อมูล Telemetry จาก Student 5 ของทุกกลุ่ม"""
    pubsub = r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
    await pubsub.psubscribe("f1:dashboard:*", "f1:race:finish")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        async for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if message['type'] == 'pmessage':  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                channel = message['channel']  # กำหนดหรือปรับค่าให้ channel
                
                # ถ้ารับข้อมูล Telemetry จาก Student 5
                if "f1:dashboard:" in channel:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    group_id = channel.split(":")[-1]  # กำหนดหรือปรับค่าให้ group_id
                    data = json.loads(message['data'])  # กำหนดหรือปรับค่าให้ data
                    if group_id in race_data:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        race_data[group_id]['distance'] = float(data.get('distance', 0.0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                        race_data[group_id]['speed'] = float(data.get('speed', 0.0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                
                # ถ้ารับสัญญาณเข้าเส้นชัย
                elif channel == "f1:race:finish":  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                    data = json.loads(message['data'])  # กำหนดหรือปรับค่าให้ data
                    gid = data['group_id']  # กำหนดหรือปรับค่าให้ gid
                    if gid in race_data and not race_data[gid]['finished']:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                        race_data[gid]['finished'] = True  # กำหนดหรือปรับค่าให้ race_data[gid]['finished']
                        leaderboard.append(gid)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
    except asyncio.CancelledError:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        await pubsub.unsubscribe()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    console = Console()  # กำหนดหรือปรับค่าให้ console

    # เริ่ม Task ดักฟัง Pub/Sub ใน Background
    pubsub_task = asyncio.create_task(listen_to_pubsub(r))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        # 1. Reset สถานะใน Redis เป็น STOPPED เพื่อบล็อก Student 1 ไม่ให้แอบออกตัว
        await r.set("f1:race:status", "STOPPED")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        reset_race_state()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

        console.clear()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        console.print("\n[bold yellow]===================================================[/bold yellow]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        console.print("[bold cyan] 🏁 F1 RACE CONTROL - READY TO START THE GRAND PRIX [/bold cyan]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        console.print("[bold yellow]===================================================[/bold yellow]\n")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        
        # รอกด Enter บน Terminal ของครู
        await asyncio.to_thread(input, "👉 กด [ENTER] เพื่อปล่อยตัวนักเรียนรอบใหม่ (START RACE)...")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        # 2. เค้าท์ดาวน์ปล่อยตัว
        for i in range(3, 0, -1):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            console.print(f"🚦 [bold red]LIGHTS COUNTDOWN: {i}...[/bold red]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        # 3. ส่งสัญญาณ GREEN LIGHTS ออกไป
        await r.set("f1:race:status", "GREEN")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        console.print("🚦 [bold green]LIGHTS OUT AND AWAY WE GO! (GREEN LIGHTS BROADCASTED)[/bold green]\n")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

        # 4. แสดงผลหน้าจอ Real-time จนกว่าจะกด Ctrl+C เพื่อเริ่มรอบใหม่
        with Live(generate_race_ui("RACE IN PROGRESS"), refresh_per_second=10) as live:  # เปิดใช้งาน resource ภายใน context manager
            try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
                while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
                    live.update(generate_race_ui("RACE IN PROGRESS"))  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
                    await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
                console.print("\n[yellow]⚠️ Resetting Race Session...[/yellow]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                continue  # ข้ามไปเริ่มรอบการวนซ้ำถัดไป

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("\nRace Control Closed.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ