import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import redis.asyncio as redis  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ⚙️ CONFIGURATION
REDIS_HOST = '172.16.46.79'     # IP ของ Redis Server (เครื่องครู)
GROUP_ID = 'g04'             # เลขกลุ่ม เช่น g01 - g08
STUDENT_ID = '6710301033'  # กำหนดหรือปรับค่าให้ STUDENT_ID

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"  # กำหนดหรือปรับค่าให้ STREAM_KEY
GROUP_NAME = "f1_pitwall"  # กำหนดหรือปรับค่าให้ GROUP_NAME
CONSUMER_NAME = f"engineer_pit_strategy_{STUDENT_ID}"  # กำหนดหรือปรับค่าให้ CONSUMER_NAME

async def init_group(r: redis.Redis):  # ประกาศฟังก์ชัน init_group สำหรับรวมขั้นตอนการทำงาน
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"✅ Consumer Group '{GROUP_NAME}' initialized.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    except redis.ResponseError as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        if "BUSYGROUP" not in str(e): raise e  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน

async def pit_strategy_worker():  # ประกาศฟังก์ชัน pit_strategy_worker สำหรับรวมขั้นตอนการทำงาน
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    await init_group(r)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"🔧 Pit Strategy Engineer Ready... [Consumer: {CONSUMER_NAME}]")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            if entries:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                for stream, msgs in entries:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                    for msg_id, data in msgs:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                        tire_wear = float(data['tire_wear'])  # กำหนดหรือปรับค่าให้ tire_wear
                        
                        if tire_wear > 75.0:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                            print(f"🛞 🚨 [PIT STRATEGY] BOX BOX BOX! Tires critical: {tire_wear}% (ID: {msg_id})")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                        elif tire_wear > 50.0:  # ตรวจสอบเงื่อนไขทางเลือกถัดไป
                            print(f"🛞 ⚠️ [PIT STRATEGY] Prepare Soft Compound. Tires at {tire_wear}%")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        except Exception as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            print(f"Error: {e}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(0.01)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(pit_strategy_worker())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน