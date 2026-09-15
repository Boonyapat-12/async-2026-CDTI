import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def link_scraper(queue: asyncio.Queue, page_urls: list[str]):  # ประกาศฟังก์ชัน link_scraper สำหรับรวมขั้นตอนการทำงาน
    """Producer: สแกนหาลิงก์รูปภาพแล้วใส่ลง Queue"""
    print("[Producer] เริ่มสแกนหาลิงก์รูปภาพ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    for page in page_urls:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        print(f"  -- [Producer] สแกนหน้าเว็บ: {page}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(0.3)  # จำลองเวลาอ่าน HTML

        # เจอลิงก์รูปภาพ 2 รูปต่อ 1 หน้า
        img_url_1 = f"https://example.com/images/{page}_img1.jpg"  # กำหนดหรือปรับค่าให้ img_url_1
        img_url_2 = f"https://example.com/images/{page}_img2.jpg"  # กำหนดหรือปรับค่าให้ img_url_2

        await queue.put(img_url_1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        await queue.put(img_url_2)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    print("[Producer] สแกนหาลิงก์รูปภาพเสร็จสิ้น!\n")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

async def image_downloader(queue: asyncio.Queue, worker_name: str):  # ประกาศฟังก์ชัน image_downloader สำหรับรวมขั้นตอนการทำงาน
    """Consumer (1 ตัว): ดึงลิงก์จาก Queue ทีละใบมาทำการดาวน์โหลด"""
    downloaded_count = 0  # กำหนดหรือปรับค่าให้ downloaded_count
    print(f"[{worker_name}] สตาร์ทเตรียมพร้อมโหลดรูป...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    while True:  # วนซ้ำตราบใดที่เงื่อนไขยังเป็นจริง
        # ดึงลิงก์ออกจาก Queue
        img_url = await queue.get()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        # ตรวจสอบสัญญาณหยุด (Sentinel Value)
        if img_url is None:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            queue.task_done()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            break  # หยุดการวนซ้ำทันที

        downloaded_count += 1  # กำหนดหรือปรับค่าให้ downloaded_count
        print(f"  -> [{worker_name}] (รูปที่ {downloaded_count}) กำลังโหลด: {img_url}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await asyncio.sleep(0.5)  # จำลองระยะเวลาดาวน์โหลดไฟล์ผ่าน Network

        # แจ้ง Queue ว่าประมวลผลลิงก์นี้เรียบร้อยแล้ว
        queue.task_done()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    print(f"[{worker_name}] ทำงานเสร็จสิ้น! ดาวน์โหลดรวมทั้งหมด {downloaded_count} รูป")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    pages = ["page_1", "page_2", "page_3"]  # กำหนดหรือปรับค่าให้ pages
    queue = asyncio.Queue()  # กำหนดหรือปรับค่าให้ queue

    # 1. สร้าง Task สำหรับ Producer และ Consumer (1 ตัว)
    producer_task = asyncio.create_task(link_scraper(queue, pages))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    downloader_task = asyncio.create_task(image_downloader(queue, "Downloader_01"))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    # 2. รอให้ Producer หาลิงก์จนครบ
    await producer_task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    # 3. รอให้ Consumer เคลียร์งานใน Queue จนหมด
    await queue.join()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    # 4. ส่ง None 1 ครั้ง เพื่อแจ้งให้ Downloader ตัวเดียวนี้หยุดทำงาน
    await queue.put(None)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    await downloader_task  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
