# food_utils.py
import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

async def send_order_to_kitchen(student_id: str, shop_name: str, menu_name: str) -> dict:  # ประกาศฟังก์ชัน send_order_to_kitchen สำหรับรวมขั้นตอนการทำงาน
    url = f"http://172.16.2.117:8088/order/{shop_name}"  # กำหนดหรือปรับค่าให้ url
    payload = {"student_id": student_id, "menu_name": menu_name}  # กำหนดหรือปรับค่าให้ payload
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        async with httpx.AsyncClient() as client:  # เปิดใช้งาน resource ภายใน context manager
            response = await client.post(url, json=payload, timeout=10.0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            if response.status_code == 200:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                return response.json()  # ส่งผลลัพธ์กลับไปยังผู้เรียก
            else:  # ทำงานในกรณีที่เงื่อนไขก่อนหน้าไม่เป็นจริง
                return {"status": "ERROR", "detail": f"HTTP Error {response.status_code}"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก
    except Exception as e:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        return {"status": "ERROR", "detail": f"Connection failed: {e}"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก