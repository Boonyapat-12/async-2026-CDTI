import asyncio
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8088

STUDENTS = ["6710301034", "6710301043", "6710301033", "6710301017", "6710301020", "6710301019"]
GROUP_SIZE = len(STUDENTS)
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1

coupons_db: List[str] = [f"COUPON-{i:02d}" for i in range(1, TOTAL_COUPONS + 1)]

# ใช้ Pointer ชี้ตำแหน่งคูปองใบถัดไปที่จะแจก
current_coupon_index = 0

student_claims: Dict[str, List[str]] = {student_id: [] for student_id in STUDENTS}

class ClaimRequest(BaseModel):
    student_id: str

@app.post("/claim")
async def claim_coupon(req: ClaimRequest):
    global current_coupon_index
    student_id = req.student_id

    if student_id not in student_claims:
        return {"status": "INVALID_STUDENT", "message": "ไม่พบรายชื่อในระบบ"}

    if len(student_claims[student_id]) >= 2:
        return {"status": "LIMIT_REACHED", "message": "คุณรับคูปองครบ 2 ใบแล้ว"}

    # CRITICAL SECTION (ไม่มี Lock)
    if current_coupon_index < len(coupons_db):
        # 1. อ่านค่า Index ปัจจุบันมาเก็บไว้
        index_to_claim = current_coupon_index

        # หน่วงเวลาเปิดช่องให้ Race Condition เกิดขึ้น
        await asyncio.sleep(0.1)

        # 2. แจกคูปองตาม Index นั้น
        coupon = coupons_db[index_to_claim]
        student_claims[student_id].append(coupon)

        # 3. ขยับ Index ไปใบถัดไป (ถ้ามี Request เข้าพร้อมกัน ทั้งคู่อ่าน Index เดียวกัน จะแจกคูปองซ้ำใบเดียวกันทันที!)
        current_coupon_index = index_to_claim + 1

        return {"status": "SUCCESS", "claimed_coupon": coupon, "total_owned": len(student_claims[student_id])}

    return {"status": "OUT_OF_STOCK", "message": "คูปองหมดแล้ว"}

@app.get("/summary")
async def get_summary():
    return {
        "remaining_stock": len(coupons_db) - current_coupon_index,
        "student_claims": student_claims
    }

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)