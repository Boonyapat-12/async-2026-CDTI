# Objective: Compare the structural and mechanical differences of both strategies in a racing scenario.  # เป้าหมายคือเทียบ gather กับ wait
import asyncio  # ใช้ asyncio สำหรับ gather, create_task, wait และ sleep
from time import ctime  # ใช้ ctime เพื่อแสดงเวลาใน output

async def runner(name, speed):  # coroutine จำลองนักวิ่ง โดยรับชื่อและความเร็วเป็นเวลารอ
    await asyncio.sleep(speed)  # จำลองเวลาที่นักวิ่งใช้วิ่งเข้าเส้นชัย
    return f"{name} crossed line!"  # คืนข้อความเมื่อนักวิ่งเข้าเส้นชัย

async def main():  # coroutine หลักของโปรแกรม
    # gather จะรอทุก runner ให้จบ แล้วคืนผลลัพธ์ทั้งหมดตามลำดับที่ส่งเข้าไป
    print(f"{ctime()} --- Starting gather() approach (Unified Aggregation) ---")  # แจ้งว่าเริ่มตัวอย่างแบบ gather
    all_finishes = await asyncio.gather(runner("A", 0.5), runner("B", 2.0))  # รอ runner A และ B ให้เสร็จทั้งหมด
    print(f"{ctime()} Gather output: {all_finishes}\n")  # แสดงผลลัพธ์ทั้งหมดที่ gather คืนมา
    
    # wait แบบ FIRST_COMPLETED ใช้เมื่อต้องการรู้ว่าใครเสร็จก่อน
    print(f"{ctime()} --- Starting wait() approach (State control / Racing) ---")  # แจ้งว่าเริ่มตัวอย่างแบบ wait
    active_tasks = {asyncio.create_task(runner("A", 0.5)), asyncio.create_task(runner("B", 2.0))}  # สร้าง task runner A และ B เพื่อให้แข่งกัน
    
    done, pending = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)  # รอจนมี runner ตัวแรกเข้าเส้นชัย
    print(f"{ctime()} Wait output: The winner of the race is -> {list(done)[0].result()}")  # แสดงผลลัพธ์ของผู้ชนะ
    
    # ยกเลิก runner ที่ยังไม่เสร็จ เพราะเรารู้ผู้ชนะแล้ว
    for t in pending:  # วนดู runner ที่ยังไม่เข้าเส้นชัย
        t.cancel()  # ยกเลิก runner ที่เหลือ

asyncio.run(main())  # เริ่ม event loop แล้วรัน main() จนจบ