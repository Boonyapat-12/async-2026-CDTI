import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from typing import Dict, List  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from fastapi import FastAPI  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from pydantic import BaseModel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import uvicorn  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

app = FastAPI()  # กำหนดหรือปรับค่าให้ app

SERVER_HOST = "0.0.0.0"  # กำหนดหรือปรับค่าให้ SERVER_HOST
SERVER_PORT = 8088  # กำหนดหรือปรับค่าให้ SERVER_PORT

STUDENTS = ["6710301017", "6710301019", "6710301020", "6710301033", "6710301034", "6710301043"]  # กำหนดหรือปรับค่าให้ STUDENTS
GROUP_SIZE = len(STUDENTS)  # กำหนดหรือปรับค่าให้ GROUP_SIZE
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1  # กำหนดหรือปรับค่าให้ TOTAL_COUPONS

coupons_db: List[str] = [f"COUPON_{i:02d}" for i in range(1, TOTAL_COUPONS + 1)]  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
current_coupon_index = 0  # กำหนดหรือปรับค่าให้ current_coupon_index
student_claims: Dict[str, List[str]] = {student_id: [] for student_id in STUDENTS}  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

# 1. ประกาศสร้าง Mutex Lock สำหรับควบคุมการเข้าถึงข้อมูลร่วม
coupon_lock = asyncio.Lock()  # กำหนดหรือปรับค่าให้ coupon_lock

class ClaimRequest(BaseModel):  # ประกาศคลาส ClaimRequest สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    student_id: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

@app.post("/claim")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def claim_coupon(req: ClaimRequest):  # ประกาศฟังก์ชัน claim_coupon สำหรับรวมขั้นตอนการทำงาน
    global current_coupon_index  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    student_id = req.student_id  # กำหนดหรือปรับค่าให้ student_id

    # 2. ใช้ async with coupon_lock ครอบ Critical Section
    async with coupon_lock:  # เปิดใช้งาน resource ภายใน context manager

        if student_id not in student_claims:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return {"status": "INVALID_STUDENT", "message": "ไม่พบรายชื่อในระบบ"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        if len(student_claims[student_id]) >= 2:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            return {"status": "LIMIT_REACHED", "message": "คุณรับคูปองครบ 2 ใบแล้ว"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        if current_coupon_index < len(coupons_db):  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            index_to_claim = current_coupon_index  # กำหนดหรือปรับค่าให้ index_to_claim

            # แม้จะมี sleep ระหว่างทาง Request อื่นต้องรอ Lock
            await asyncio.sleep(0.1)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

            coupon = coupons_db[index_to_claim]  # กำหนดหรือปรับค่าให้ coupon
            student_claims[student_id].append(coupon)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

            # ขยับ Index หลังแจกคูปองเสร็จ
            current_coupon_index = index_to_claim + 1  # กำหนดหรือปรับค่าให้ current_coupon_index

            return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
                "status": "SUCCESS",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "claimed_coupon": coupon,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "total_owned": len(student_claims[student_id])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        return {"status": "OUT_OF_STOCK", "message": "คูปองหมดแล้ว"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

@app.get("/summary")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def get_summary():  # ประกาศฟังก์ชัน get_summary สำหรับรวมขั้นตอนการทำงาน
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "remaining_stock": len(coupons_db) - current_coupon_index,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "student_claims": student_claims  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน