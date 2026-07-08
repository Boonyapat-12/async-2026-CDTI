# Objective: Stop an ongoing execution prematurely by triggering a cancellation exception.
import asyncio
from time import ctime

async def background_loop():
    try:
        print(f"{ctime()} Worker: Starting long infinite process...")
        while True:
            await asyncio.sleep(1)
            print(f"{ctime()} Worker: Still ticking...")
    except asyncio.CancelledError:
        # เมื่อ task ถูก cancel จะเข้ามาตรงนี้เพื่อจัดการก่อนจบงาน
        print(f"{ctime()} Worker: Interrupted! Executing clean-up logic before exit...")

async def main():
    task = asyncio.create_task(background_loop())
    await asyncio.sleep(2.5) # ปล่อยให้ worker ทำงานไปสักพักก่อน
    
    print(f"{ctime()} Main: Changing plans, canceling the worker task now!")
    task.cancel() # สั่งยกเลิก task ที่กำลังทำงานอยู่
    await asyncio.sleep(0.1) # ให้เวลา event loop ส่งสัญญาณ cancel ไปถึง task

asyncio.run(main())