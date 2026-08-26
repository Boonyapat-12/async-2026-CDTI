import asyncio

async def slow_producer(queue: asyncio.Queue):
    print("[Producer] เริ่มผลิตงาน...")
    await asyncio.sleep(2)  # แกล้งทำเป็นทำงานช้า 2 วินาที
    
    print("[Producer] ผลิตงานชิ้นที่ 1 เสร็จแล้ว ดันเข้าคิว!")
    await queue.put("Data-Alpha")

async def eager_consumer(queue: asyncio.Queue):
    print("[Consumer] พยายามจะ get() ข้อมูลทันที...")
    
    # ณ จุดนี้ คิวยังว่างเปล่า! คำสั่ง await queue.get() จะทำให้ Consumer "รอ" 
    # โดยสลับไปให้ระบบรัน slow_producer ต่อโดยไม่แฮงก์
    data = await queue.get()
    print(f"[Consumer] ได้รับข้อมูลสำเร็จ: {data}")

async def main():
    queue = asyncio.Queue()
    
    print("=== เริ่มการทดสอบ Get ขณะคิวว่าง ===")
    await asyncio.gather(
        eager_consumer(queue),
        slow_producer(queue)
    )

if __name__ == "__main__":
    asyncio.run(main())