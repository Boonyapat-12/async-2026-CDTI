from time import ctime, perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


def log(message):  # ประกาศฟังก์ชัน log สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} | {message}", flush=True)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


async def update_cup_number(customer_name):  # ประกาศฟังก์ชัน update_cup_number สำหรับรวมขั้นตอนการทำงาน
    log(f"LCD: Processing for customer {customer_name}...")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    log(f"LCD: Done for customer {customer_name}.")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


async def make_coffee(customer_name):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    log(f"Making coffee for {customer_name}...")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    await asyncio.sleep(1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    log(f"Coffee ready for {customer_name}!")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    await update_cup_number(customer_name)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop


async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue

    log("=== Asyncio Coffee Machine ===")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    start_time = perf_counter()  # กำหนดหรือปรับค่าให้ start_time

    tasks = []  # กำหนดหรือปรับค่าให้ tasks
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        task = asyncio.create_task(make_coffee(customer))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
        tasks.append(task)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    await asyncio.gather(*tasks)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์

    duration = perf_counter() - start_time  # กำหนดหรือปรับค่าให้ duration
    log(f"Total time: {duration:0.2f} seconds")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
