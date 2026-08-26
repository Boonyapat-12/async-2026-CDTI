import asyncio

async def worker(worker_id: int, queue: asyncio.Queue):
    while True:
        # ดึงงานออกจากคิว
        item = await queue.get()
        
        print(f"[Worker-{worker_id}] กำลังประมวลผล: {item}")
        await asyncio.sleep(1)  # จำลองเวลาประมวลผล
        
        print(f"[Worker-{worker_id}] ประมวลผล {item} เสร็จสิ้น!")
        # แจ้ง Queue ว่างานชิ้นที่ดึงมานี้ทำเสร็จสมบูรณ์แล้ว
        queue.task_done()

async def main():
    queue = asyncio.Queue()

    # 1. ใส่ภาระงาน 5 ชิ้นลงในคิว
    for i in range(1, 6):
        await queue.put(f"Job #{i}")

    # 2. สร้าง Worker 2 ตัวรันขนานกันเป็น background tasks
    workers = []
    for i in range(1, 3):
        task = asyncio.create_task(worker(i, queue))
        workers.append(task)

    print("=== โปรแกรมหลัก: กำลังรอให้งานในคิวถูกเคลียร์จนหมดด้วย queue.join() ===")
    
    # บล็อกรอจนกว่าทุกงานที่ put เข้าไป จะถูกเรียก task_done() จนครบ
    await queue.join()
    
    print("=== งานทุกชิ้นถูกประมวลผลเสร็จสิ้นเรียบร้อยแล้ว! ===")

    # 3. ยกเลิกการทำงานของ Worker ที่รอลูปอยู่ใน Background
    for task in workers:
        task.cancel()

if __name__ == "__main__":
    asyncio.run(main())