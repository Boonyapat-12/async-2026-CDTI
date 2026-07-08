# Objective: Implement complex processing workflows based on task fulfillment conditions.  # เป้าหมายคือใช้ wait แยกงานเสร็จกับงานค้าง
import asyncio  # ใช้ asyncio สำหรับสร้าง task, wait และ cancel
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาใน output

async def network_probe(server_name, delay):  # coroutine จำลองการ ping server หนึ่งตัว
    await asyncio.sleep(delay)  # จำลองเวลาตอบกลับของ server
    return f"Ping successful: {server_name}"  # คืนข้อความว่า ping server นี้สำเร็จ

async def main():  # coroutine หลักของโปรแกรม
    # สร้าง task หลายตัว เพื่อดูว่า server ไหนตอบกลับเร็วที่สุด
    tasks = {  # สร้าง set ของ task ที่จะแข่งกัน
        asyncio.create_task(network_probe("Primary-Server", 2.0)),  # task ของ Primary-Server ใช้เวลา 2.0 วินาที
        asyncio.create_task(network_probe("Backup-Server-1", 0.5)),  # task ของ Backup-Server-1 ใช้เวลา 0.5 วินาที
        asyncio.create_task(network_probe("Backup-Server-2", 1.0))  # task ของ Backup-Server-2 ใช้เวลา 1.0 วินาที
    }  # ปิด set ของ task
    
    # รอจนกว่าจะมี task ตัวแรกทำงานเสร็จ แล้วแยกเป็นกลุ่ม done กับ pending
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)  # รอแค่ตัวแรกที่เสร็จ แล้วคืน done/pending
    
    print(f"{ctime()} Count of Tasks Done: {len(done)}")       # จำนวน task ที่เสร็จแล้ว
    print(f"{ctime()} Count of Tasks Pending: {len(pending)}") # จำนวน task ที่ยังทำงานไม่เสร็จ
    
    for finished_task in done:  # วนดู task ที่เสร็จแล้ว
        print(f"{ctime()} Fastest Task Result: {finished_task.result()}")  # แสดงผลลัพธ์ของ task ที่เร็วที่สุด
        
    # ยกเลิก task ที่เหลือ เพราะเราได้ผลลัพธ์ที่เร็วที่สุดแล้ว
    for ongoing_task in pending:  # วนดู task ที่ยังไม่เสร็จ
        ongoing_task.cancel()  # ยกเลิก task ที่เหลือ

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ