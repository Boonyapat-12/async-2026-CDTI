import asyncio

async def producer(queue: asyncio.Queue):
    print("[Producer] กำลังเตรียมส่งข้อมูลเข้าคิว...")
    for item in [" Order #1", "Order #2", "Order #3"]:
        print(f"[Producer] ส่งข้อมูล: {item}")
        await queue.put(item)  # ใส่ข้อมูลเข้าคิว (FIFO)
        await asyncio.sleep(0.5)

async def consumer(queue: asyncio.Queue):
    print("[Consumer] เริ่มการรอรับข้อมูลจากคิว...")
    while True:
        # ดึงข้อมูลออกจากคิว (ตัวที่เข้ามาก่อน จะถูกดึงออกมาก่อน)
        item = await queue.get()
        print(f"[Consumer] ดึงข้อมูลออกมาประมวลผล: {item}")
        await asyncio.sleep(1)
        
        # เงื่อนไขหยุดการทำงานเมื่อเจอรายการสุดท้าย
        if item == "Order #3":
            print("[Consumer] ประมวลผลครบหมดแล้ว!")
            break

async def main():
    # สร้าง asyncio.Queue บน Event Loop
    queue = asyncio.Queue()
    
    # รัน Producer และ Consumer ไปพร้อมกัน
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

if __name__ == "__main__":
    asyncio.run(main())