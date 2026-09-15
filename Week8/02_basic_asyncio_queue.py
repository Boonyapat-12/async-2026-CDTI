import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def producer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน producer สำหรับรวมขั้นตอนการทำงาน
    print("[Producer] กำลังเตรียมส่งข้อมูลเข้าคิว...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    for item in [" Order #1", "Order #2", "Order #3"]:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        print(f"[Producer] ส่งข้อมูล: {item}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await queue.put(item)  # ใส่ข้อมูลเข้าคิว (FIFO)
        await asyncio.sleep(0.5)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

async def consumer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน consumer สำหรับรวมขั้นตอนการทำงาน
    print("[Consumer] เริ่มการรอรับข้อมูลจากคิว...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        # ดึงข้อมูลออกจากคิว (ตัวที่เข้ามาก่อน จะถูกดึงออกมาก่อน)
        item = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"[Consumer] ดึงข้อมูลออกมาประมวลผล: {item}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        
        # เงื่อนไขหยุดการทำงานเมื่อเจอรายการสุดท้าย
        if item == "Order #3":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            print("[Consumer] ประมวลผลครบหมดแล้ว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            break  # หยุดการวนซ้ำทันที

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    # สร้าง asyncio.Queue บน Event Loop
    queue = asyncio.Queue()  # กำหนดหรือปรับค่าให้ queue
    
    # รัน Producer และ Consumer ไปพร้อมกัน
    await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        producer(queue),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        consumer(queue)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน