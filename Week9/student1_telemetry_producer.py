import asyncio
import random
import time
import json
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'     # IP ของ Redis Server (เครื่องครู)
GROUP_ID = 'g01'             # เลขกลุ่ม เช่น g01 - g08
STUDENT_ID = '66010001'      # รหัสนักศึกษาตนเอง

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
FINISH_DISTANCE = 10000.0    # 10,000 เมตร (10 km)

async def wait_for_new_green_light(r: redis.Redis):
    """ฟังก์ชันการันตีว่าจะต้องรอครูปดสัญญาณปล่อยตัวรอบใหม่เสมอ"""
    print(f"🏎️ [{GROUP_ID}] Checking Race Status...")
    
    # 1. หากสถานะปัจจุบันเป็น GREEN ค้างอยู่ (แข่งจบไปแล้วรอบนึง) ให้รอกระทั่งครู Reset เป็น STOPPED/RED
    current_status = await r.get("f1:race:status")
    if current_status == "GREEN":
        print(f"⏳ [{GROUP_ID}] Waiting for Teacher to RESET the race status (STOPPED)...")
        while True:
            status = await r.get("f1:race:status")
            if status != "GREEN":
                break
            await asyncio.sleep(0.5)

    # 2. เมื่อสถานะไม่ใช่ GREEN แล้ว ให้รอกระทั่งครูกดปล่อยตัว (GREEN) รอบใหม่
    print(f"🚦 [{GROUP_ID}] Ready on Grid! Waiting for Teacher's GREEN LIGHT...")
    while True:
        status = await r.get("f1:race:status")
        if status == "GREEN":
            print(f"🚦 [{GROUP_ID}] LIGHTS OUT AND AWAY WE GO!")
            break
        await asyncio.sleep(0.2)

async def produce_f1_telemetry():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

    # 🚦 เรียกใช้ฟังก์ชันรอสัญญาณปล่อยตัวรอบใหม่เสมอ
    await wait_for_new_green_light(r)

    total_distance_m = 0.0
    dt = 0.05  # ส่งข้อมูลทุก 0.05 วินาที (20 Hz)

    try:
        while True:
            speed_kmh = round(random.uniform(180.0, 330.0), 1)
            
            # คำนวณระยะทางที่เพิ่มขึ้นใน 0.05 วินาที
            distance_delta = (speed_kmh * 1000.0 / 3600.0) * dt
            total_distance_m += distance_delta

            payload = {
                "timestamp": time.time(),
                "speed": speed_kmh,
                "engine_temp": round(random.uniform(90.0, 125.0), 1),
                "tire_wear": round(random.uniform(5.0, 95.0), 1),
                "rpm": random.randint(10000, 15000),
                "gear": random.randint(3, 8),
                "distance": round(total_distance_m, 2)
            }

            # ส่งข้อมูลเข้า Redis Stream
            msg_id = await r.xadd(STREAM_KEY, payload, maxlen=1000, approximate=True)
            print(f"🏎️ [{GROUP_ID}] Sent ID: {msg_id} | Speed: {speed_kmh} km/h | Dist: {total_distance_m:.1f} m")

            # เช็กการเข้าเส้นชัย
            if total_distance_m >= FINISH_DISTANCE:
                print(f"🏁 🏆 [{GROUP_ID}] CHEQUERED FLAG! Finished race distance {total_distance_m:.1f} m")
                await r.publish("f1:race:finish", json.dumps({"group_id": GROUP_ID}))
                break

            await asyncio.sleep(dt)
    except asyncio.CancelledError:
        await r.close()

if __name__ == "__main__":
    asyncio.run(produce_f1_telemetry())