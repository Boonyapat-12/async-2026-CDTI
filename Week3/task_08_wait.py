# Objective: Implement complex processing workflows based on task fulfillment conditions.
import asyncio
from time import ctime

async def network_probe(server_name, delay):
    await asyncio.sleep(delay)
    return f"Ping successful: {server_name}"

async def main():
    # สร้าง task หลายตัว เพื่อดูว่า server ไหนตอบกลับเร็วที่สุด
    tasks = {
        asyncio.create_task(network_probe("Primary-Server", 2.0)),
        asyncio.create_task(network_probe("Backup-Server-1", 0.5)),
        asyncio.create_task(network_probe("Backup-Server-2", 1.0))
    }
    
    # รอจนกว่าจะมี task ตัวแรกทำงานเสร็จ แล้วแยกเป็นกลุ่ม done กับ pending
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    print(f"{ctime()} Count of Tasks Done: {len(done)}")       # จำนวน task ที่เสร็จแล้ว
    print(f"{ctime()} Count of Tasks Pending: {len(pending)}") # จำนวน task ที่ยังทำงานไม่เสร็จ
    
    for finished_task in done:
        print(f"{ctime()} Fastest Task Result: {finished_task.result()}")
        
    # ยกเลิก task ที่เหลือ เพราะเราได้ผลลัพธ์ที่เร็วที่สุดแล้ว
    for ongoing_task in pending:
        ongoing_task.cancel()

asyncio.run(main())