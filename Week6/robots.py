import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ==========================================
# 1. Configuration & Constants
# ==========================================
STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ STUDENT_ID
BASE_URL = "http://172.16.2.117:8088"  # กำหนดหรือปรับค่าให้ BASE_URL

# กำหนดลำดับชิ้นส่วนและหุ่นยนต์
PARTS = ["A", "B", "C"]  # กำหนดหรือปรับค่าให้ PARTS
ROBOTS = ["robot_1", "robot_2", "robot_3", "robot_4"]  # กำหนดหรือปรับค่าให้ ROBOTS

# ==========================================
# 2. Async Functions Development
# ==========================================

async def reset_factory(client: httpx.AsyncClient):  # ประกาศฟังก์ชัน reset_factory สำหรับรวมขั้นตอนการทำงาน
    """ส่ง Request เพื่อทำการ Reset สถานะของหุ่นยนต์ทั้งหมดของรหัสนักเรียนนี้"""

    # TODO: เติมโค้ดการส่ง POST request ไปยัง /student/{STUDENT_ID}/reset
    response = await client.post(f"/student/{STUDENT_ID}/reset")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    return response.json()  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def grab_part(client: httpx.AsyncClient, robot_id: str, part: str):  # ประกาศฟังก์ชัน grab_part สำหรับรวมขั้นตอนการทำงาน
    """สั่งให้หุ่นยนต์หยิบชิ้นส่วน 1 ชิ้น"""
    # TODO: เติมโค้ดส่ง POST request ไปยัง /student/{STUDENT_ID}/robot/{robot_id}/grab
    # พร้อมแนบ JSON Payload {"part": part}
    payload = {"part": part}  # กำหนดหรือปรับค่าให้ payload
    url_path = f"/student/{STUDENT_ID}/robot/{robot_id}/grab"  # กำหนดหรือปรับค่าให้ url_path

    response = await client.post(url_path, json=payload)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    return {"robot": robot_id, "part": part, "status": "success"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

async def run_robot_task(client: httpx.AsyncClient, robot_id: str):  # ประกาศฟังก์ชัน run_robot_task สำหรับรวมขั้นตอนการทำงาน
    """สั่งให้หุ่นยนต์ 1 ตัว ทำการหยิบชิ้นส่วน A, B, และ C ตามลำดับ"""
    # TODO: วนลูปหยิบชิ้นส่วนใน PARTS ตามลำดับเรียงกัน (Sequential inside single robot)
    for part in PARTS:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            await grab_part(client, robot_id, part)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

async def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    """ฟังก์ชันหลักสำหรับเริ่มการทำงานของหุ่นยนต์ทั้ง 4 ตัวแบบ Async"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:  # เปิดใช้งาน resource ภายใน context manager
        print("Resetting Factory...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        await reset_factory(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        
        start_time = time.time()  # กำหนดหรือปรับค่าให้ start_time
        print("Starting Async Robot Operation...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        
        # TODO: สั่งรัน run_robot_task ของหุ่นยนต์ทั้ง 4 ตัวพร้อมกันโดยใช้ asyncio.gather
        robot_tasks = [run_robot_task(client, robot_id) for robot_id in ROBOTS]  # กำหนดหรือปรับค่าให้ robot_tasks
        await asyncio.gather(*robot_tasks)  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์

        elapsed_time = time.time() - start_time  # กำหนดหรือปรับค่าให้ elapsed_time
        print(f"Finished all tasks in {elapsed_time:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except (httpx.HTTPError, ValueError) as error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print(f"Error: {error}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
