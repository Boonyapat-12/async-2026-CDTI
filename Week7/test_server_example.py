import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import unittest  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

from server_example import STUDENTS, app, reset_coupon_state  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ


async def request(method: str, path: str, **kwargs) -> httpx.Response:  # ประกาศฟังก์ชัน request สำหรับรวมขั้นตอนการทำงาน
    transport = httpx.ASGITransport(app=app)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:  # เปิดใช้งาน resource ภายใน context manager
        return await client.request(method, path, **kwargs)  # ส่งผลลัพธ์กลับไปยังผู้เรียก


class ServerExampleTests(unittest.TestCase):  # ประกาศคลาส ServerExampleTests สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    def setUp(self):  # ประกาศฟังก์ชัน setUp สำหรับรวมขั้นตอนการทำงาน
        reset_coupon_state()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    def test_my_coupons_returns_only_requested_students_claims(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        student_id = STUDENTS[0]  # กำหนดหรือปรับค่าให้ student_id

        first_claim = asyncio.run(  # กำหนดหรือปรับค่าให้ first_claim
            request("POST", "/claim", json={"student_id": student_id})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        second_claim = asyncio.run(  # กำหนดหรือปรับค่าให้ second_claim
            request("POST", "/claim", json={"student_id": student_id})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        response = asyncio.run(request("GET", f"/my-coupons/{student_id}"))  # กำหนดหรือปรับค่าให้ response

        self.assertEqual(first_claim.json()["status"], "SUCCESS")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(second_claim.json()["status"], "SUCCESS")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(response.status_code, 200)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            response.json(),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            {  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                "student_id": student_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "total_claimed": 2,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "claimed_coupons": ["COUPON_01", "COUPON_02"],  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            },  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    def test_my_coupons_rejects_unknown_student(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        response = asyncio.run(request("GET", "/my-coupons/unknown"))  # กำหนดหรือปรับค่าให้ response

        self.assertEqual(response.status_code, 404)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(response.json()["detail"], "ไม่พบรายชื่อในระบบ")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    unittest.main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
