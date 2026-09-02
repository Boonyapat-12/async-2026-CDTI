import asyncio
import redis.asyncio as redis

# ⚙️ CONFIGURATION
REDIS_HOST = 'localhost'
GROUP_ID = 'g01'
STUDENT_ID = '66010002'

STREAM_KEY = f"f1:telemetry:{GROUP_ID}"
GROUP_NAME = "f1_pitwall"
CONSUMER_NAME = f"engineer_pit_strategy_{STUDENT_ID}"

async def init_group(r: redis.Redis):
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)
        print(f"✅ Consumer Group '{GROUP_NAME}' initialized.")
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise e

async def pit_strategy_worker():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    await init_group(r)
    print(f"🔧 Pit Strategy Engineer Ready... [Consumer: {CONSUMER_NAME}]")

    while True:
        try:
            entries = await r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)
            if entries:
                for stream, msgs in entries:
                    for msg_id, data in msgs:
                        tire_wear = float(data['tire_wear'])
                        
                        if tire_wear > 75.0:
                            print(f"🛞 🚨 [PIT STRATEGY] BOX BOX BOX! Tires critical: {tire_wear}% (ID: {msg_id})")
                        elif tire_wear > 50.0:
                            print(f"🛞 ⚠️ [PIT STRATEGY] Prepare Soft Compound. Tires at {tire_wear}%")

                        await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(pit_strategy_worker())