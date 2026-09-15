import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

SERVER_URL = "http://127.0.0.1:8088"  # กำหนดหรือปรับค่าให้ SERVER_URL
MY_STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ MY_STUDENT_ID


async def hunt_coupons() -> None:  # ประกาศฟังก์ชัน hunt_coupons สำหรับรวมขั้นตอนการทำงาน
    async with httpx.AsyncClient(timeout=5.0) as client:  # เปิดใช้งาน resource ภายใน context manager
        print(f"[{MY_STUDENT_ID}] เริ่มต้นภารกิจล่าคูปอง...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        for attempt in range(1, 6):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            response = await client.post(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                f"{SERVER_URL}/claim",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                json={"student_id": MY_STUDENT_ID},  # กำหนดหรือปรับค่าให้ json
            )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            data = response.json()  # กำหนดหรือปรับค่าให้ data
            status = data["status"]  # กำหนดหรือปรับค่าให้ status
            result = data.get("message", data.get("claimed_coupon"))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            print(f"  -- ครั้งที่ {attempt}: [{status}] -> {result}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

            if status in {"LIMIT_REACHED", "OUT_OF_STOCK"}:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                break  # หยุดการวนซ้ำทันที

            await asyncio.sleep(0.02)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        print("\nกำลังดึงสรุปคูปองของตนเอง...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        response = await client.get(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            f"{SERVER_URL}/my-coupons/{MY_STUDENT_ID}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        my_summary = response.json()  # กำหนดหรือปรับค่าให้ my_summary
        print(  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            # คอมเมนต์บรรทัดที่เริ่มข้อความหลายบรรทัด โดยไม่เปลี่ยนเนื้อหาภายใน string
            f"สรุปของ [{MY_STUDENT_ID}]: "
            f"ได้รับคูปองรวม {my_summary['total_claimed']} ใบ -> "
            f"{my_summary['claimed_coupons']}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        print("\nกำลังดึงสรุปภาพรวมคูปองทั้งหมดจาก Server...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
        response = await client.get(f"{SERVER_URL}/summary")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        summary = response.json()  # กำหนดหรือปรับค่าให้ summary
        print(f"จำนวนคูปองคงเหลือ: {summary['remaining_stock']} ใบ")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

        for student_id, coupons in summary["student_claims"].items():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            print(  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
                f" - {student_id}: ได้รับ {len(coupons)} ใบ -> {coupons}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(hunt_coupons())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except httpx.HTTPError as error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ Server: {error}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
