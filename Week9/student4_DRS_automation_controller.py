import asyncio
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'
GROUP_ID = 'g01'
STUDENT_ID = '66010004'

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
GROUP_NAME = "f1_pitwall"
CONSUMER_NAME = f"engineer_drs_controller_{STUDENT_ID}"

async def init_group(r: redis.Redis):
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise e

async def drs_controller_worker():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    await init_group(r)
    print(f"🟢 DRS Controller Ready... [Consumer: {CONSUMER_NAME}]")

    while True:
        try:
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)
            if entries:
                for stream, msgs in entries:
                    for msg_id, data in msgs:
                        speed = float(data['speed'])
                        gear = int(data['gear'])

                        if speed > 250.0 and gear >= 7:
                            print(f"🟢 [DRS SYSTEM] DRS ENABLED! Speed: {speed} km/h (Gear {gear})")
                        else:
                            print(f"🔴 [DRS SYSTEM] DRS Disabled (Speed: {speed} km/h, Gear {gear})")

                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(drs_controller_worker())