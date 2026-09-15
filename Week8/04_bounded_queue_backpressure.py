import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def fast_producer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน fast_producer สำหรับรวมขั้นตอนการทำงาน
    for i in range(1, 6):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        print(f"[Producer] พยายามใส่ Task #{i} เข้าคิว (คิวนับได้ {queue.qsize()} ชิ้น)")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        # หากคิวเต็ม (maxsize=2) คำสั่ง put() จะค้างรอ (Await) จนกว่าจะมีพื้นที่ว่าง
        await queue.put(f"Task #{i}")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f" -> [Producer] ใส่ Task #{i} สำเร็จ!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def slow_consumer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน slow_consumer สำหรับรวมขั้นตอนการทำงาน
    # รอให้ Producer เริ่มใส่ข้อมูลไปก่อนเล็กน้อย
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    while not queue.empty():  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        item = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"    [Consumer] ดึง {item} ออกไปทำงาน (ใช้เวลา 2 วินาที)...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(2)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    # กำหนดขนาดคิวสูงสุดได้เพียง 2 ชิ้นเท่านั้น (Bounded Queue)
    bounded_queue = asyncio.Queue(maxsize=2)  # กำหนดหรือปรับค่าให้ bounded_queue
    
    print("=== เริ่มทดสอบ Bounded Queue (maxsize=2) ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        fast_producer(bounded_queue),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        slow_consumer(bounded_queue)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน