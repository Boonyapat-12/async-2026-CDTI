import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ⚙️ CONFIGURATION
REDIS_HOST = '172.16.46.79'     # IP ของ Redis Server (เครื่องครู)
GROUP_ID = 'g04'             # เลขกลุ่ม เช่น g01 - g08
STUDENT_ID = '6710301033'  # กำหนดหรือปรับค่าให้ STUDENT_ID

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"  # กำหนดหรือปรับค่าให้ STREAM_KEY
GROUP_NAME = "f1_pitwall"  # กำหนดหรือปรับค่าให้ GROUP_NAME
CONSUMER_NAME = f"engineer_dashboard_{STUDENT_ID}"  # กำหนดหรือปรับค่าให้ CONSUMER_NAME
PUBSUB_CHANNEL = f"f1:dashboard:{GROUP_ID}"  # กำหนดหรือปรับค่าให้ PUBSUB_CHANNEL

async def init_group(r: redis.Redis):  # ประกาศฟังก์ชัน init_group สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    except redis.ResponseError as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        if "BUSYGROUP" not in str(e): raise e  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน

async def dashboard_broadcaster_worker():  # ประกาศฟังก์ชัน dashboard_broadcaster_worker สำหรับรวมขั้นตอนการทำงาน
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    await init_group(r)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"📺 Dashboard Broadcaster Ready... [Consumer: {CONSUMER_NAME}]")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"📡 Listening Stream: '{STREAM_KEY}' ==> Broadcasting Channel: '{PUBSUB_CHANNEL}'\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            if entries:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                for stream, msgs in entries:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                    for msg_id, data in msgs:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                        speed = float(data.get('speed', 0.0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                        gear = data.get('gear', '-')  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                        rpm = int(data.get('rpm', 0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
                        distance = float(data.get('distance', 0.0))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

                        dashboard_packet = {  # กำหนดหรือปรับค่าให้ dashboard_packet
                            "speed": speed,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "gear": gear,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "rpm": rpm,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "distance": distance,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                            "stream_id": msg_id  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
                        
                        # 1. ยิงข้อมูลเข้า Redis Pub/Sub Channel
                        await r.publish(PUBSUB_CHANNEL, json.dumps(dashboard_packet))  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                        
                        # 2. ส่งสัญญาณ ACK เพื่อยืนยันว่าประมวลผลข้อความนี้เสร็จแล้ว
                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

                        # 3. แสดงผลค่าออกทาง Terminal
                        print(f"📡 [BROADCAST -> {PUBSUB_CHANNEL}] ID: {msg_id} | Speed: {speed:.1f} km/h | Gear: {gear} | RPM: {rpm:,} | Dist: {distance:.1f} m")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        except Exception as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"❌ Error: {e}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(0.01)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(dashboard_broadcaster_worker())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except KeyboardInterrupt:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print("\nBroadcaster Stopped.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ