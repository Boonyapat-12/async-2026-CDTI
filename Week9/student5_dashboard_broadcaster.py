import asyncio
import json
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'
GROUP_ID = 'g01'
STUDENT_ID = '66010005'

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
GROUP_NAME = "f1_pitwall"
CONSUMER_NAME = f"engineer_dashboard_{STUDENT_ID}"
PUBSUB_CHANNEL = f"f1:dashboard:{GROUP_ID}"

async def init_group(r: redis.Redis):
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise e

async def dashboard_broadcaster_worker():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    await init_group(r)
    print(f"📺 Dashboard Broadcaster Ready... [Consumer: {CONSUMER_NAME}]")
    print(f"📡 Listening Stream: '{STREAM_KEY}' ==> Broadcasting Channel: '{PUBSUB_CHANNEL}'\n")

    while True:
        try:
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)
            if entries:
                for stream, msgs in entries:
                    for msg_id, data in msgs:
                        speed = float(data.get('speed', 0.0))
                        gear = data.get('gear', '-')
                        rpm = int(data.get('rpm', 0))
                        distance = float(data.get('distance', 0.0))

                        dashboard_packet = {
                            "speed": speed,
                            "gear": gear,
                            "rpm": rpm,
                            "distance": distance,
                            "stream_id": msg_id
                        }
                        
                        # 1. ยิงข้อมูลเข้า Redis Pub/Sub Channel
                        await r.publish(PUBSUB_CHANNEL, json.dumps(dashboard_packet))
                        
                        # 2. ส่งสัญญาณ ACK เพื่อยืนยันว่าประมวลผลข้อความนี้เสร็จแล้ว
                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)

                        # 3. แสดงผลค่าออกทาง Terminal
                        print(f"📡 [BROADCAST -> {PUBSUB_CHANNEL}] ID: {msg_id} | Speed: {speed:.1f} km/h | Gear: {gear} | RPM: {rpm:,} | Dist: {distance:.1f} m")

        except Exception as e:
            print(f"❌ Error: {e}")
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    try:
        asyncio.run(dashboard_broadcaster_worker())
    except KeyboardInterrupt:
        print("\nBroadcaster Stopped.")