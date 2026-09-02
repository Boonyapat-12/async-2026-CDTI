import asyncio
import json
import redis.asyncio as redis
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Console

REDIS_HOST = 'localhost'  # IP เครื่องครู
TOTAL_GROUPS = 8          # จำนวนกลุ่มทั้งหมด (g01 - g08)
FINISH_DISTANCE = 10000.0 # 10 km (10,000 เมตร)

# ตัวแปร Global สำหรับเก็บข้อมูลการแข่งขัน
race_data = {}
leaderboard = []

def reset_race_state():
    """ล้างข้อมูลการแข่งขันเพื่อเตรียมพร้อมสำหรับรอบใหม่"""
    global race_data, leaderboard
    race_data = {
        f"g{i:02d}": {"distance": 0.0, "speed": 0.0, "finished": False} 
        for i in range(1, TOTAL_GROUPS + 1)
    }
    leaderboard = []

def generate_race_ui(status_text):
    """สร้าง UI หน้าจอตารางการแข่งขันแบบ Real-time"""
    table = Table(title="🏎️ F1 GRAND PRIX - LIVE TELEMETRY LEADERBOARD", expand=True)
    table.add_column("Group", style="cyan", width=8)
    table.add_column("Live Progress (10,000 M)", width=40)
    table.add_column("Distance", justify="right")
    table.add_column("Speed", justify="right")
    table.add_column("Status", justify="center")

    # เรียงลำดับกลุ่มตามระยะทาง (Leaderboard)
    sorted_groups = sorted(race_data.items(), key=lambda x: x[1]['distance'], reverse=True)

    for rank, (group_id, data) in enumerate(sorted_groups, 1):
        dist = data['distance']
        pct = min(100.0, (dist / FINISH_DISTANCE) * 100.0)
        
        # สร้าง Progress Bar
        bar_len = int(pct / 100 * 25)
        bar_str = "█" * bar_len + "░" * (25 - bar_len)
        
        speed_str = f"{data['speed']} km/h"
        
        if data['finished']:
            rank_idx = leaderboard.index(group_id) + 1 if group_id in leaderboard else 'FIN'
            status = f"[bold green]🏆 FINISHED (#{rank_idx})[/bold green]"
        elif dist > 0:
            status = f"[yellow]RACING (P{rank})[/yellow]"
        else:
            status = "[dim]GRID (WAITING)[/dim]"

        table.add_row(
            f"[bold]{group_id.upper()}[/bold]",
            f"[{bar_str}] {pct:.1f}%",
            f"{dist:.1f} m",
            speed_str,
            status
        )

    return Panel(table, title=f"🚦 Race Status: [bold green]{status_text}[/bold green]", border_style="bright_blue")

async def listen_to_pubsub(r):
    """ดักฟัง Pub/Sub ข้อมูล Telemetry จาก Student 5 ของทุกกลุ่ม"""
    pubsub = r.pubsub()
    await pubsub.psubscribe("f1:dashboard:*", "f1:race:finish")
    
    try:
        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                channel = message['channel']
                
                # ถ้ารับข้อมูล Telemetry จาก Student 5
                if "f1:dashboard:" in channel:
                    group_id = channel.split(":")[-1]
                    data = json.loads(message['data'])
                    if group_id in race_data:
                        race_data[group_id]['distance'] = float(data.get('distance', 0.0))
                        race_data[group_id]['speed'] = float(data.get('speed', 0.0))
                
                # ถ้ารับสัญญาณเข้าเส้นชัย
                elif channel == "f1:race:finish":
                    data = json.loads(message['data'])
                    gid = data['group_id']
                    if gid in race_data and not race_data[gid]['finished']:
                        race_data[gid]['finished'] = True
                        leaderboard.append(gid)
    except asyncio.CancelledError:
        await pubsub.unsubscribe()

async def main():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    console = Console()

    # เริ่ม Task ดักฟัง Pub/Sub ใน Background
    pubsub_task = asyncio.create_task(listen_to_pubsub(r))

    while True:
        # 1. Reset สถานะใน Redis เป็น STOPPED เพื่อบล็อก Student 1 ไม่ให้แอบออกตัว
        await r.set("f1:race:status", "STOPPED")
        reset_race_state()

        console.clear()
        console.print("\n[bold yellow]===================================================[/bold yellow]")
        console.print("[bold cyan] 🏁 F1 RACE CONTROL - READY TO START THE GRAND PRIX [/bold cyan]")
        console.print("[bold yellow]===================================================[/bold yellow]\n")
        
        # รอกด Enter บน Terminal ของครู
        await asyncio.to_thread(input, "👉 กด [ENTER] เพื่อปล่อยตัวนักเรียนรอบใหม่ (START RACE)...")

        # 2. เค้าท์ดาวน์ปล่อยตัว
        for i in range(3, 0, -1):
            console.print(f"🚦 [bold red]LIGHTS COUNTDOWN: {i}...[/bold red]")
            await asyncio.sleep(1)

        # 3. ส่งสัญญาณ GREEN LIGHTS ออกไป
        await r.set("f1:race:status", "GREEN")
        console.print("🚦 [bold green]LIGHTS OUT AND AWAY WE GO! (GREEN LIGHTS BROADCASTED)[/bold green]\n")

        # 4. แสดงผลหน้าจอ Real-time จนกว่าจะกด Ctrl+C เพื่อเริ่มรอบใหม่
        with Live(generate_race_ui("RACE IN PROGRESS"), refresh_per_second=10) as live:
            try:
                while True:
                    live.update(generate_race_ui("RACE IN PROGRESS"))
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️ Resetting Race Session...[/yellow]")
                continue

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nRace Control Closed.")