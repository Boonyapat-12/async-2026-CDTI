import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def slow_producer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน slow_producer สำหรับรวมขั้นตอนการทำงาน
    print("[Producer] เริ่มผลิตงาน...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(2)  # แกล้งทำเป็นทำงานช้า 2 วินาที
    
    print("[Producer] ผลิตงานชิ้นที่ 1 เสร็จแล้ว ดันเข้าคิว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await queue.put("Data-Alpha")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

async def eager_consumer(queue: asyncio.Queue):  # ประกาศฟังก์ชัน eager_consumer สำหรับรวมขั้นตอนการทำงาน
    print("[Consumer] พยายามจะ get() ข้อมูลทันที...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # ณ จุดนี้ คิวยังว่างเปล่า! คำสั่ง await queue.get() จะทำให้ Consumer "รอ" 
    # โดยสลับไปให้ระบบรัน slow_producer ต่อโดยไม่แฮงก์
    data = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    print(f"[Consumer] ได้รับข้อมูลสำเร็จ: {data}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = asyncio.Queue()  # กำหนดหรือปรับค่าให้ queue
    
    print("=== เริ่มการทดสอบ Get ขณะคิวว่าง ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        eager_consumer(queue),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        slow_producer(queue)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน