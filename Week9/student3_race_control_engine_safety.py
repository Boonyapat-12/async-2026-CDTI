import asyncio
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'
GROUP_ID = 'g01'
STUDENT_ID = '66010003'

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
GROUP_NAME = "f1_pitwall"
CONSUMER_NAME = f"engineer_safety_alert_{STUDENT_ID}"

async def init_group(r: redis.Redis):
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise e

async def safety_alert_worker():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    await init_group(r)
    print(f"🚨 Engine Safety Monitor Ready... [Consumer: {CONSUMER_NAME}]")

    while True:
        try:
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)
            if entries:
                for stream, msgs in entries:
                    for msg_id, data in msgs:
                        engine_temp = float(data['engine_temp'])
                        rpm = int(data['rpm'])

                        if engine_temp > 115.0:
                            print(f"🔥 ⚠️ [ENGINE ALERT] Overheating! {engine_temp}°C - Reduce Power!")
                        if rpm > 14500:
                            print(f"⚙️ ⚠️ [RPM ALERT] Over-revving detected: {rpm} RPM! Shift Up!")

                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(safety_alert_worker())