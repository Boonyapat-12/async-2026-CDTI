# Objective: Attach a plain synchronous function that automatically triggers the moment a task finishes.
import asyncio
from time import ctime

def alert_manager(finished_task):
    # callback นี้จะถูกเรียกอัตโนมัติเมื่อ task ทำงานเสร็จ
    print(f"{ctime()} Callback Triggered! Task output fetched: {finished_task.result()}")

async def download_file():
    print(f"{ctime()} Downloading packet...")
    await asyncio.sleep(1.0)
    return "Data_Payload.zip"

async def main():
    task = asyncio.create_task(download_file())
    # ผูก callback เข้ากับ task เพื่อให้เรียก alert_manager ตอนงานเสร็จ
    task.add_done_callback(alert_manager)
    
    await task # รอ task หลักให้เสร็จ เพื่อไม่ให้โปรแกรมจบก่อน callback ทำงาน

asyncio.run(main())