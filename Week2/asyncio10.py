# Program 10: Extracting Return Values from Tasks
# Concept: Accessing returned results from completed Task objects using .result() or direct assignment.

import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def calculate_bill(customer, base_price):  # ประกาศฟังก์ชัน calculate_bill สำหรับรวมขั้นตอนการทำงาน
    print(f"Calculating bill for {customer}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    await asyncio.sleep(2)  # Simulate a delay in calculation
    final_price = base_price * 1.07  # Adding 7% vat
    return final_price  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    # Create tasks for two customers
    task_a = asyncio.create_task(calculate_bill("A", 100))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
    task_b = asyncio.create_task(calculate_bill("B", 200))  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent

    # Await the tasks and get their results
    result_a = await task_a  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    result_b = await task_b  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    print(f"Final Bill A: ${result_a:.2f}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"Final Bill B: ${result_b:.2f}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"Total bill: ${result_a + result_b:.2f}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
