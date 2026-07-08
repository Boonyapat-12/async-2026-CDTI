import asyncio  # เรียกใช้ asyncio สำหรับสร้าง coroutine, task, sleep แบบ async และ cancel task
from time import ctime  # เรียกใช้ ctime เพื่อพิมพ์เวลาปัจจุบันให้อ่านง่ายใน output


async def delivery_task(package_id, duration):  # สร้าง coroutine สำหรับจำลองงานส่งพัสดุ 1 ชิ้น โดยรับรหัสพัสดุและเวลาที่ใช้ส่ง
    try:  # เปิดบล็อก try เพื่อให้จับเหตุการณ์ตอน task ถูกยกเลิกได้
        print(f"{ctime()} Courier started delivering {package_id}...")  # แจ้งว่า courier เริ่มส่งพัสดุรหัสนี้แล้ว
        await asyncio.sleep(duration)  # จำลองเวลาส่งพัสดุแบบไม่บล็อก event loop ตาม duration ที่ส่งเข้ามา
        return f"Package {package_id} Delivered!"  # ถ้าส่งสำเร็จให้คืนข้อความว่าพัสดุถูกส่งแล้ว
    except asyncio.CancelledError:  # ดักจับเมื่อ task นี้ถูกสั่ง cancel จากภายนอก
        print(f"{ctime()} Delivery Canceled! Returning package to warehouse.")  # แจ้งว่าการส่งถูกยกเลิกและต้องนำพัสดุกลับคลัง
        raise  # ส่งสัญญาณ CancelledError ต่อไป เพื่อให้สถานะ task เป็น cancelled จริง


async def main():  # coroutine หลักที่ใช้ควบคุม flow ของโปรแกรมทั้งหมด
    task = asyncio.create_task(  # สร้าง task จาก coroutine delivery_task เพื่อให้ event loop จัดการงานส่งพัสดุ
        delivery_task(package_id="P001", duration=5.0),  # เรียกงานส่งพัสดุ P001 โดยจำลองว่าจะใช้เวลา 5 วินาที
        name="Express-Courier"  # ตั้งชื่อ task เป็น Express-Courier เพื่อใช้ตรวจสอบและแสดงใน output
    )  # ปิดคำสั่งสร้าง task

    await asyncio.sleep(2.0)  # ให้โปรแกรมหลักรอ 2 วินาทีก่อนเข้าไปตรวจว่างานส่งเสร็จหรือยัง

    print(f"{ctime()} Checking task '{task.get_name()}'. Is it done? {task.done()}")  # แสดงชื่อ task และสถานะว่าเสร็จแล้วหรือยัง

    if not task.done():  # ถ้า task ยังไม่เสร็จหลังจากรอไปแล้ว 2 วินาที ให้ถือว่านานเกินไป
        print(f"{ctime()} Taking too long! Canceling the task...")  # แจ้งว่ากำลังยกเลิก task เพราะใช้เวลานานเกินไป
        task.cancel()  # ส่งคำสั่งยกเลิก task ที่กำลังทำงานอยู่

    try:  # เปิดบล็อก try เพื่อรอ task และรับมือกับการถูก cancel
        await task  # รอให้ task ตอบสนองต่อคำสั่ง cancel จนสถานะสุดท้ายชัดเจน
    except asyncio.CancelledError:  # ถ้า await แล้วเจอว่า task ถูก cancel ให้เข้ามาตรงนี้
        pass  # ไม่ต้องทำอะไรเพิ่ม เพราะ delivery_task พิมพ์ข้อความยกเลิกไปแล้ว

    print(f"{ctime()} Final verify: Is task officially canceled? {task.cancelled()}")  # ตรวจสอบสุดท้ายว่า task ถูกยกเลิกจริงหรือไม่


asyncio.run(main())  # เริ่ม event loop และสั่งให้ main() ทำงานจนจบ
