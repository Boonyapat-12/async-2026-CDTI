import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


async def producer(queue: asyncio.Queue, total_coupons: int):  # ประกาศฟังก์ชัน producer สำหรับรวมขั้นตอนการทำงาน
    """
    Producer: มีหน้าที่สร้าง Coupon จำนวน 20 ใบแล้วดันลง asyncio.Queue
    """
    print(f"[Producer] เริ่มสร้างคูปองจำนวน {total_coupons} ใบ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    for i in range(1, total_coupons + 1):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        coupon = f"COUPON-{i:02d}"  # กำหนดหรือปรับค่าให้ coupon
        await queue.put(coupon)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        print(f"  -- [Producer] สร้างและใส่คิวสำเร็จ: {coupon}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(0.02)  # จำลองระยะเวลาในการสร้างคูปอง

    print("[Producer] สร้างคูปองเสร็จสิ้นเรียบร้อยแล้ว!\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


async def consumer(queue: asyncio.Queue, consumer_name: str):  # ประกาศฟังก์ชัน consumer สำหรับรวมขั้นตอนการทำงาน
    """
    Consumer: 1 ตัว มีหน้าที่ดึงคูปองออกจาก asyncio.Queue มาเก็บไว้
    """
    claimed_coupons = []  # กำหนดหรือปรับค่าให้ claimed_coupons
    print(f"[{consumer_name}] เริ่มต้นรอรับคูปอง...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        # ดึงคูปองออกจากคิว (หากคิวว่าง จะสลับให้ Producer รันโดยไม่บล็อก Event Loop)
        coupon = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        # ตรวจสอบ Sentinel Value (สัญญาณแจ้งหยุดทำงาน)
        if coupon is None:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            queue.task_done()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            break  # หยุดการวนซ้ำทันที

        claimed_coupons.append(coupon)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        print(f"  -> [{consumer_name}] ได้รับคูปอง: {coupon} (รวมสะสม: {len(claimed_coupons)} ใบ)")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        # แจ้ง Queue ว่าประมวลผลคูปองชิ้นนี้เสร็จเรียบร้อย
        queue.task_done()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        await asyncio.sleep(0.05)  # จำลองระยะเวลาประมวลผลของ Consumer

    print(f"\n[{consumer_name}] ทำงานเสร็จสิ้น! รวมคูปองที่เก็บได้ทั้งหมด: {len(claimed_coupons)} ใบ")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"รายการคูปอง: {claimed_coupons}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    TOTAL_COUPONS = 20  # กำหนดหรือปรับค่าให้ TOTAL_COUPONS
    queue = asyncio.Queue()  # กำหนดหรือปรับค่าให้ queue

    # 1. สร้าง Task สำหรับ Producer และ Consumer (1 ตัว)
    prod_task = asyncio.create_task(producer(queue, TOTAL_COUPONS))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    cons_task = asyncio.create_task(consumer(queue, "Consumer_01"))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    # 2. รอให้ Producer สร้างคูปองจนครบ
    await prod_task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    # 3. รอให้ Consumer ดึงคูปองใน Queue ไปประมวลผลจนหมดทุกชิ้น
    await queue.join()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    # 4. ส่ง Sentinel Value (None) เพื่อแจ้งให้ Consumer หยุดลูปการทำงาน
    await queue.put(None)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await cons_task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
