import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from rich.live import Live  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich.panel import Panel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich.table import Table  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from rich import print as rprint  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

# ⚙️ CONFIGURATION
REDIS_HOST = '172.16.46.79'     # IP ของ Redis Server (เครื่องครู หรือ localhost)
GROUP_ID = 'g04'             # ระบุกลุ่มที่ต้องการดู เช่น g01
TOTAL_DISTANCE_M = 10000.0   # ระยะทางรวม 10 km (10,000 เมตร)

PUBSUB_CHANNEL = f"f1:dashboard:{GROUP_ID}"  # กำหนดหรือปรับค่าให้ PUBSUB_CHANNEL

def generate_dashboard_ui(data):  # ประกาศฟังก์ชัน generate_dashboard_ui สำหรับรวมขั้นตอนการทำงาน
    """สร้าง Layout UI แสดงระยะทางและความเร็วแบบ Real-time"""
    speed = float(data.get('speed', 0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    gear = data.get('gear', '-')  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    rpm = int(data.get('rpm', 0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    distance = float(data.get('distance', 0.0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    stream_id = data.get('stream_id', 'N/A')  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

    # 1. คำนวณหลอดความก้าวหน้าระยะทาง (Race Distance Progress Bar)
    dist_pct = min(100.0, (distance / TOTAL_DISTANCE_M) * 100.0)  # กำหนดหรือปรับค่าให้ dist_pct
    dist_bar_len = int(dist_pct / 100 * 30)  # กำหนดหรือปรับค่าให้ dist_bar_len
    dist_bar = "█" * dist_bar_len + "░" * (30 - dist_bar_len)  # กำหนดหรือปรับค่าให้ dist_bar

    # 2. สร้าง Gauge ความเร็ว (Speed Bar)
    speed_bar_len = int(speed / 350 * 30)  # กำหนดหรือปรับค่าให้ speed_bar_len
    speed_bar = "█" * speed_bar_len + "░" * (30 - speed_bar_len)  # กำหนดหรือปรับค่าให้ speed_bar
    speed_color = "bright_green" if speed < 250 else "bright_yellow" if speed < 300 else "bright_red"  # กำหนดหรือปรับค่าให้ speed_color

    # 3. จัดการตารางแสดงผล
    table = Table(title=f"🏎️ LIVE F1 TELEMETRY DASHBOARD [Team: {GROUP_ID.upper()}]", expand=True)  # กำหนดหรือปรับค่าให้ table
    table.add_column("Telemetry Metric", style="cyan", no_wrap=True)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_column("Real-Time Status & Gauges", style="bold white")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    table.add_row("Stream Packet ID", stream_id)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_row(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
        "Race Progress",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        f"[bold bright_cyan]{distance:.1f} / {TOTAL_DISTANCE_M:.0f} m ({dist_pct:.1f}%)[/bold bright_cyan]\n[bright_cyan][{dist_bar}][/bright_cyan]"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    table.add_row(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
        "Current Speed",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        f"[{speed_color}]{speed} km/h[/]\n[{speed_color}][{speed_bar}][/{speed_color}]"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    table.add_row("Engine Gear", f"[magenta]GEAR {gear}[/magenta]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    table.add_row("Engine RPM", f"[bold cyan]{rpm:,} RPM[/bold cyan]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    status_title = "🏁 FINISHED!" if dist_pct >= 100 else "📡 Live Stream Active"  # กำหนดหรือปรับค่าให้ status_title
    border = "bright_green" if dist_pct >= 100 else "bright_blue"  # กำหนดหรือปรับค่าให้ border

    return Panel(table, title=f"Team Dashboard: {status_title}", border_style=border)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def listen_to_dashboard():  # ประกาศฟังก์ชัน listen_to_dashboard สำหรับรวมขั้นตอนการทำงาน
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    pubsub = r.pubsub()  # กำหนดหรือปรับค่าให้ pubsub
    
    await pubsub.subscribe(PUBSUB_CHANNEL)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    rprint(f"[bold green]✅ Subscribed to Team Channel: '{PUBSUB_CHANNEL}'[/bold green]")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    rprint("[yellow]Waiting for Race Control to start and Student 5 to broadcast...[/yellow]\n")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    latest_data = {"speed": 0, "gear": 1, "rpm": 0, "distance": 0.0, "stream_id": "Waiting..."}  # กำหนดหรือปรับค่าให้ latest_data

    with Live(generate_dashboard_ui(latest_data), refresh_per_second=10) as live:  # เปิดใช้งาน resource ภายใน context manager
        async for message in pubsub.listen():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if message['type'] == 'message':  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                latest_data = json.loads(message['data'])  # กำหนดหรือปรับค่าให้ latest_data
                live.update(generate_dashboard_ui(latest_data))  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(listen_to_dashboard())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("\nDashboard Closed.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ