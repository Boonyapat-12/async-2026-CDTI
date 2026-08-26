import asyncio

async def fast_producer(queue: asyncio.Queue):
    for i in range(1, 6):
        print(f"[Producer] พยายามใส่ Task #{i} เข้าคิว (คิวนับได้ {queue.qsize()} ชิ้น)")
        # หากคิวเต็ม (maxsize=2) คำสั่ง put() จะค้างรอ (Await) จนกว่าจะมีพื้นที่ว่าง
        await queue.put(f"Task #{i}")
        print(f" -> [Producer] ใส่ Task #{i} สำเร็จ!")

async def slow_consumer(queue: asyncio.Queue):
    # รอให้ Producer เริ่มใส่ข้อมูลไปก่อนเล็กน้อย
    await asyncio.sleep(1)
    while not queue.empty():
        item = await queue.get()
        print(f"    [Consumer] ดึง {item} ออกไปทำงาน (ใช้เวลา 2 วินาที)...")
        await asyncio.sleep(2)

async def main():
    # กำหนดขนาดคิวสูงสุดได้เพียง 2 ชิ้นเท่านั้น (Bounded Queue)
    bounded_queue = asyncio.Queue(maxsize=2)
    
    print("=== เริ่มทดสอบ Bounded Queue (maxsize=2) ===")
    await asyncio.gather(
        fast_producer(bounded_queue),
        slow_consumer(bounded_queue)
    )

if __name__ == "__main__":
    asyncio.run(main())