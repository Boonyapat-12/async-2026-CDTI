import asyncio
import time

# --- แบบ 1: Synchronous (Blocking) ---
def sync_task(name, delay):
    print(f"[Sync] เริ่มงาน {name} (ต้องใช้เวลา {delay} วินาที)...")
    time.sleep(delay)  # CPU หยุดนิ่งเพื่อนั่งรอตรงนี้
    print(f"[Sync] งาน {name} เสร็จสิ้น!")

def main_sync():
    start_time = time.time()
    print("=== เริ่มทำงานแบบ Synchronous ===")
    sync_task("A", 2)
    sync_task("B", 3)
    print(f"เวลารวมแบบ Sync: {time.time() - start_time:.2f} วินาที\n")

# --- แบบ 2: Asynchronous (Non-blocking) ---
async def async_task(name, delay):
    print(f"[Async] เริ่มงาน {name} (ต้องใช้เวลา {delay} วินาที)...")
    await asyncio.sleep(delay)  # สลับให้ Event Loop ไปรันงานอื่นระหว่างรอ
    print(f"[Async] งาน {name} เสร็จสิ้น!")

async def main_async():
    start_time = time.time()
    print("=== เริ่มทำงานแบบ Asynchronous ===")
    # รันงาน A และ B พร้อมกันบน Event Loop
    await asyncio.gather(
        async_task("A", 2),
        async_task("B", 3)
    )
    print(f"เวลารวมแบบ Async: {time.time() - start_time:.2f} วินาที")

if __name__ == "__main__":
    main_sync()
    asyncio.run(main_async())