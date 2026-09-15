import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def worker(worker_id: int, queue: asyncio.Queue):  # ประกาศฟังก์ชัน worker สำหรับรวมขั้นตอนการทำงาน
    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        # ดึงงานออกจากคิว
        item = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        
        print(f"[Worker-{worker_id}] กำลังประมวลผล: {item}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(1)  # จำลองเวลาประมวลผล
        
        print(f"[Worker-{worker_id}] ประมวลผล {item} เสร็จสิ้น!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        # แจ้ง Queue ว่างานชิ้นที่ดึงมานี้ทำเสร็จสมบูรณ์แล้ว
        queue.task_done()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = asyncio.Queue()  # กำหนดหรือปรับค่าให้ queue

    # 1. ใส่ภาระงาน 5 ชิ้นลงในคิว
    for i in range(1, 6):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        await queue.put(f"Job #{i}")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    # 2. สร้าง Worker 2 ตัวรันขนานกันเป็น background tasks
    workers = []  # กำหนดหรือปรับค่าให้ workers
    for i in range(1, 3):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        task = asyncio.create_task(worker(i, queue))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        workers.append(task)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    print("=== โปรแกรมหลัก: กำลังรอให้งานในคิวถูกเคลียร์จนหมดด้วย queue.join() ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # บล็อกรอจนกว่าทุกงานที่ put เข้าไป จะถูกเรียก task_done() จนครบ
    await queue.join()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    
    print("=== งานทุกชิ้นถูกประมวลผลเสร็จสิ้นเรียบร้อยแล้ว! ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    # 3. ยกเลิกการทำงานของ Worker ที่รอลูปอยู่ใน Background
    for task in workers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        task.cancel()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน