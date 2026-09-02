import asyncio
import json
import redis.asyncio as redis
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'     # IP ของ Redis Server (เครื่องครู หรือ localhost)
GROUP_ID = 'g01'             # ระบุกลุ่มที่ต้องการดู เช่น g01
TOTAL_DISTANCE_M = 10000.0   # ระยะทางรวม 10 km (10,000 เมตร)

PUBSUB_CHANNEL = f"f1:dashboard:{GROUP_ID}"

def generate_dashboard_ui(data):
    """สร้าง Layout UI แสดงระยะทางและความเร็วแบบ Real-time"""
    speed = float(data.get('speed', 0))
    gear = data.get('gear', '-')
    rpm = int(data.get('rpm', 0))
    distance = float(data.get('distance', 0.0))
    stream_id = data.get('stream_id', 'N/A')

    # 1. คำนวณหลอดความก้าวหน้าระยะทาง (Race Distance Progress Bar)
    dist_pct = min(100.0, (distance / TOTAL_DISTANCE_M) * 100.0)
    dist_bar_len = int(dist_pct / 100 * 30)
    dist_bar = "█" * dist_bar_len + "░" * (30 - dist_bar_len)

    # 2. สร้าง Gauge ความเร็ว (Speed Bar)
    speed_bar_len = int(speed / 350 * 30)
    speed_bar = "█" * speed_bar_len + "░" * (30 - speed_bar_len)
    speed_color = "bright_green" if speed < 250 else "bright_yellow" if speed < 300 else "bright_red"

    # 3. จัดการตารางแสดงผล
    table = Table(title=f"🏎️ LIVE F1 TELEMETRY DASHBOARD [Team: {GROUP_ID.upper()}]", expand=True)
    table.add_column("Telemetry Metric", style="cyan", no_wrap=True)
    table.add_column("Real-Time Status & Gauges", style="bold white")

    table.add_row("Stream Packet ID", stream_id)
    table.add_row(
        "Race Progress", 
        f"[bold bright_cyan]{distance:.1f} / {TOTAL_DISTANCE_M:.0f} m ({dist_pct:.1f}%)[/bold bright_cyan]\n[bright_cyan][{dist_bar}][/bright_cyan]"
    )
    table.add_row(
        "Current Speed", 
        f"[{speed_color}]{speed} km/h[/]\n[{speed_color}][{speed_bar}][/{speed_color}]"
    )
    table.add_row("Engine Gear", f"[magenta]GEAR {gear}[/magenta]")
    table.add_row("Engine RPM", f"[bold cyan]{rpm:,} RPM[/bold cyan]")

    status_title = "🏁 FINISHED!" if dist_pct >= 100 else "📡 Live Stream Active"
    border = "bright_green" if dist_pct >= 100 else "bright_blue"

    return Panel(table, title=f"Team Dashboard: {status_title}", border_style=border)

async def listen_to_dashboard():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    
    await pubsub.subscribe(PUBSUB_CHANNEL)
    rprint(f"[bold green]✅ Subscribed to Team Channel: '{PUBSUB_CHANNEL}'[/bold green]")
    rprint("[yellow]Waiting for Race Control to start and Student 5 to broadcast...[/yellow]\n")

    latest_data = {"speed": 0, "gear": 1, "rpm": 0, "distance": 0.0, "stream_id": "Waiting..."}

    with Live(generate_dashboard_ui(latest_data), refresh_per_second=10) as live:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                latest_data = json.loads(message['data'])
                live.update(generate_dashboard_ui(latest_data))

if __name__ == "__main__":
    try:
        asyncio.run(listen_to_dashboard())
    except KeyboardInterrupt:
        print("\nDashboard Closed.")