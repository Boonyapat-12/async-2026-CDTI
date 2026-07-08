# Objective: Enforce strict deadlines on operations and raise errors if exceeded.
import asyncio
from time import ctime

async def long_query_simulation():
    print(f"{ctime()} Database: Fetching data...")
    await asyncio.sleep(5.0) # จำลองงานที่ใช้เวลานานกว่ากำหนด timeout
    return "Heavy_Report_Data"

async def main():
    try:
        print(f"{ctime()} Main: Enforcing a strict 2-second timeout deadline...")
        # wait_for จะรอไม่เกินเวลาที่กำหนด ถ้าเกินจะโยน TimeoutError
        result = await asyncio.wait_for(long_query_simulation(), timeout=2.0)
        print(f"{ctime()} Result acquired: {result}")
    except asyncio.TimeoutError:
        # ถ้างานช้าเกิน 2 วินาที โปรแกรมจะเข้ามาจัดการ error ตรงนี้
        print(f"{ctime()} Main Error Alert: Operation timed out! Task terminated.")

asyncio.run(main())