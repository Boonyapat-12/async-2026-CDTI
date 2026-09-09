import asyncio
import random
import time
import json
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = '172.16.46.79'     # IP ของ Redis Server (เครื่องครู)
GROUP_ID = 'g04'                # เลขกลุ่ม เช่น g01 - g08
STUDENT_ID = '6710301033'       # รหัสนักศึกษาตนเอง

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
FINISH_DISTANCE = 10000.0       # 10,000 เมตร (10 km)


async def wait_for_new_green_light(r: redis.Redis):
    """ฟังก์ชันการันตีว่าจะต้องรอครูกดสัญญาณปล่อยตัวรอบใหม่เสมอ"""

    print(f"🏎️ [{GROUP_ID}] Checking Race Status...")

    # 1. หากสถานะปัจจุบันเป็น GREEN ค้างอยู่
    # (แข่งจบไปแล้วรอบนึง)
    # ให้รอกระทั่งครู Reset เป็น STOPPED/RED
    current_status = await r.get("f1:race:status")

    if current_status == "GREEN":
        print(
            f"⏳ [{GROUP_ID}] "
            f"Waiting for Teacher to RESET the race status (STOPPED)..."
        )

        while True:
            status = await r.get("f1:race:status")

            if status != "GREEN":
                break

            await asyncio.sleep(0.5)

    # 2. เมื่อสถานะไม่ใช่ GREEN แล้ว
    # ให้รอกระทั่งครูกดปล่อยตัว (GREEN) รอบใหม่
    print(
        f"🚦 [{GROUP_ID}] "
        f"Ready on Grid! Waiting for Teacher's GREEN LIGHT..."
    )

    while True:
        status = await r.get("f1:race:status")

        if status == "GREEN":
            print(
                f"🚦 [{GROUP_ID}] "
                f"LIGHTS OUT AND AWAY WE GO!"
            )
            break

        # เดิม 0.2 วินาที
        # ลดเหลือ 0.05 เพื่อให้ตรวจพบ GREEN เร็วขึ้น
        # แต่ยังไม่ยิง Redis ถี่เกินไป
        await asyncio.sleep(0.05)


async def produce_f1_telemetry():

    r = redis.Redis(
        host=REDIS_HOST,
        port=6379,
        db=0,
        decode_responses=True
    )

    # 🚦 เรียกใช้ฟังก์ชันรอสัญญาณปล่อยตัวรอบใหม่เสมอ
    await wait_for_new_green_light(r)

    total_distance_m = 0.0

    dt = 0.05  # ส่งข้อมูลทุก 0.05 วินาที (20 Hz)

    # =========================
    # เพิ่มเข้ามา
    # =========================

    # ใช้ monotonic clock สำหรับจับเวลา loop
    # เพราะเหมาะสำหรับวัดช่วงเวลามากกว่า time.time()
    next_tick = time.monotonic()

    # ใช้นับจำนวน packet
    # เพื่อไม่ต้อง print ทุก packet
    packet_count = 0

    try:
        while True:

            # speed_kmh = round(random.uniform(180.0, 330.0), 1)

            speed_kmh = round(
                random.triangular(180.0, 330.0, 300.0),
                1
            )

            # คำนวณระยะทางที่เพิ่มขึ้นใน 0.05 วินาที
            distance_delta = (
                speed_kmh * 1000.0 / 3600.0
            ) * dt

            total_distance_m += distance_delta

            payload = {
                "timestamp": time.time(),
                "speed": speed_kmh,
                "engine_temp": round(
                    random.uniform(90.0, 125.0),
                    1
                ),
                "tire_wear": round(
                    random.uniform(5.0, 95.0),
                    1
                ),
                "rpm": random.randint(10000, 15000),
                "gear": random.randint(3, 8),
                "distance": round(total_distance_m, 2)
            }

            # ส่งข้อมูลเข้า Redis Stream
            msg_id = await r.xadd(
                STREAM_KEY,
                payload,
                maxlen=1000,
                approximate=True
            )

            # นับ packet ที่ส่งสำเร็จ
            packet_count += 1

            # เดิม print ทุก packet = ประมาณ 20 ครั้ง/วินาที
            #
            # ตอนนี้ print ทุก 20 packet
            # = ประมาณ 1 ครั้ง/วินาที
            #
            # ข้อมูลยังเหมือนเดิม เพียงไม่ให้ Terminal
            # สร้าง overhead ทุก ๆ 0.05 วินาที
            if packet_count % 20 == 0:
                print(
                    f"🏎️ [{GROUP_ID}] "
                    f"Sent ID: {msg_id} | "
                    f"Speed: {speed_kmh} km/h | "
                    f"Dist: {total_distance_m:.1f} m"
                )

            # เช็กการเข้าเส้นชัย
            if total_distance_m >= FINISH_DISTANCE:

                print(
                    f"🏁 🏆 [{GROUP_ID}] "
                    f"CHEQUERED FLAG! "
                    f"Finished race distance "
                    f"{total_distance_m:.1f} m"
                )

                await r.publish(
                    "f1:race:finish",
                    json.dumps(
                        {
                            "group_id": GROUP_ID
                        }
                    )
                )

                break

            # ============================================
            # จัดเวลาให้แต่ละรอบพยายามอยู่ที่ 0.05 วินาที
            # ============================================

            # เวลาที่รอบถัดไป "ควร" เริ่ม
            next_tick += dt

            # ดูว่าเหลือเวลาอีกเท่าไร
            sleep_time = next_tick - time.monotonic()

            # ถ้ายังเหลือเวลา จึงค่อย sleep
            #
            # เช่น:
            #
            # xadd + code อื่นใช้เวลา 0.008 sec
            #
            # จะ sleep:
            #
            # 0.05 - 0.008
            # = 0.042 sec
            #
            # รวมแล้วประมาณ 0.05 sec
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

            # ถ้า loop ช้ากว่ากำหนดไปแล้ว
            # จะไม่ sleep เพิ่มอีก
            else:
                next_tick = time.monotonic()

    except asyncio.CancelledError:
        await r.close()


if __name__ == "__main__":
    asyncio.run(produce_f1_telemetry())