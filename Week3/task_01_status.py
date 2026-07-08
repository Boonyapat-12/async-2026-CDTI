# Objective: Learn how to query the lifecycle status of a task object.
import asyncio
from time import ctime

async def short_job():
    await asyncio.sleep(1)
    return "Success"

async def main():
    task = asyncio.create_task(short_job())
    
    #  Inspect status immediately while it is still running
    print(f"{ctime()} Is task done? {task.done()}")          # ตอนนี้ task ยังทำงานอยู่ จึงน่าจะยังไม่เสร็จ
    print(f"{ctime()} Is task canceled? {task.cancelled()}")  # เช็กว่า task ถูกยกเลิกไปแล้วหรือยัง
    
    await task # รอให้ short_job ทำงานจนเสร็จก่อนค่อยไปบรรทัดถัดไป
    
    # Inspect status again after it finishes
    print(f"{ctime()} Is task done now? {task.done()}")      # หลัง await แล้ว task ควรเสร็จเรียบร้อย
    print(f"{ctime()} Is task canceled now? {task.cancelled()}") # ถึง task จะเสร็จแล้ว แต่ไม่ได้แปลว่าถูกยกเลิก

asyncio.run(main())