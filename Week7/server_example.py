import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from typing import Dict, List  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

import uvicorn  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from fastapi import FastAPI, HTTPException  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from pydantic import BaseModel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(title="Week 7 Coupon Server Example")  # กำหนดหรือปรับค่าให้ app

SERVER_HOST = "127.0.0.1"  # กำหนดหรือปรับค่าให้ SERVER_HOST
SERVER_PORT = 8088  # กำหนดหรือปรับค่าให้ SERVER_PORT
STUDENTS = [  # กำหนดหรือปรับค่าให้ STUDENTS
    "6710301017",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    "6710301019",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    "6710301020",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    "6710301033",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    "6710301034",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    "6710301043",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
]  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
GROUP_SIZE = len(STUDENTS)  # กำหนดหรือปรับค่าให้ GROUP_SIZE
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1  # กำหนดหรือปรับค่าให้ TOTAL_COUPONS

coupons_db: List[str] = [  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
    f"COUPON_{number:02d}" for number in range(1, TOTAL_COUPONS + 1)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
]  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
current_coupon_index = 0  # กำหนดหรือปรับค่าให้ current_coupon_index
student_claims: Dict[str, List[str]] = {  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
    student_id: [] for student_id in STUDENTS  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
}  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
coupon_lock = asyncio.Lock()  # กำหนดหรือปรับค่าให้ coupon_lock


class ClaimRequest(BaseModel):  # ประกาศคลาส ClaimRequest สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    student_id: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


def reset_coupon_state() -> None:  # ประกาศฟังก์ชัน reset_coupon_state สำหรับรวมขั้นตอนการทำงาน
    """รีเซ็ตข้อมูลในหน่วยความจำ เพื่อให้ตัวอย่างและชุดทดสอบเริ่มใหม่ได้"""
    global current_coupon_index  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    current_coupon_index = 0  # กำหนดหรือปรับค่าให้ current_coupon_index
    for claims in student_claims.values():  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        claims.clear()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


@app.post("/claim")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def claim_coupon(req: ClaimRequest):  # ประกาศฟังก์ชัน claim_coupon สำหรับรวมขั้นตอนการทำงาน
    global current_coupon_index  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async with coupon_lock:  # เปิดใช้งาน resource ภายใน context manager
        if req.student_id not in student_claims:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
                "status": "INVALID_STUDENT",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "message": "ไม่พบรายชื่อในระบบ",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        if len(student_claims[req.student_id]) >= 2:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
                "status": "LIMIT_REACHED",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "message": "คุณรับคูปองครบ 2 ใบแล้ว",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        if current_coupon_index >= len(coupons_db):  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return {"status": "OUT_OF_STOCK", "message": "คูปองหมดแล้ว"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        index_to_claim = current_coupon_index  # กำหนดหรือปรับค่าให้ index_to_claim
        await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        coupon = coupons_db[index_to_claim]  # กำหนดหรือปรับค่าให้ coupon
        student_claims[req.student_id].append(coupon)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        current_coupon_index = index_to_claim + 1  # กำหนดหรือปรับค่าให้ current_coupon_index

        return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
            "status": "SUCCESS",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "claimed_coupon": coupon,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "total_owned": len(student_claims[req.student_id]),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


@app.get("/my-coupons/{student_id}")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def get_my_coupons(student_id: str):  # ประกาศฟังก์ชัน get_my_coupons สำหรับรวมขั้นตอนการทำงาน
    if student_id not in student_claims:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        raise HTTPException(status_code=404, detail="ไม่พบรายชื่อในระบบ")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

    claims = student_claims[student_id]  # กำหนดหรือปรับค่าให้ claims
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "student_id": student_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "total_claimed": len(claims),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "claimed_coupons": claims,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


@app.get("/summary")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def get_summary():  # ประกาศฟังก์ชัน get_summary สำหรับรวมขั้นตอนการทำงาน
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "remaining_stock": len(coupons_db) - current_coupon_index,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "student_claims": student_claims,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    print(f"เปิด Coupon Server ที่ http://{SERVER_HOST}:{SERVER_PORT}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"Swagger UI: http://{SERVER_HOST}:{SERVER_PORT}/docs")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
