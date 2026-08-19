import asyncio
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Week 7 Coupon Server Example")

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8088
STUDENTS = [
    "6710301017",
    "6710301019",
    "6710301020",
    "6710301033",
    "6710301034",
    "6710301043",
]
GROUP_SIZE = len(STUDENTS)
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1

coupons_db: List[str] = [
    f"COUPON_{number:02d}" for number in range(1, TOTAL_COUPONS + 1)
]
current_coupon_index = 0
student_claims: Dict[str, List[str]] = {
    student_id: [] for student_id in STUDENTS
}
coupon_lock = asyncio.Lock()


class ClaimRequest(BaseModel):
    student_id: str


def reset_coupon_state() -> None:
    """รีเซ็ตข้อมูลในหน่วยความจำ เพื่อให้ตัวอย่างและชุดทดสอบเริ่มใหม่ได้"""
    global current_coupon_index
    current_coupon_index = 0
    for claims in student_claims.values():
        claims.clear()


@app.post("/claim")
async def claim_coupon(req: ClaimRequest):
    global current_coupon_index

    async with coupon_lock:
        if req.student_id not in student_claims:
            return {
                "status": "INVALID_STUDENT",
                "message": "ไม่พบรายชื่อในระบบ",
            }

        if len(student_claims[req.student_id]) >= 2:
            return {
                "status": "LIMIT_REACHED",
                "message": "คุณรับคูปองครบ 2 ใบแล้ว",
            }

        if current_coupon_index >= len(coupons_db):
            return {"status": "OUT_OF_STOCK", "message": "คูปองหมดแล้ว"}

        index_to_claim = current_coupon_index
        await asyncio.sleep(0.1)

        coupon = coupons_db[index_to_claim]
        student_claims[req.student_id].append(coupon)
        current_coupon_index = index_to_claim + 1

        return {
            "status": "SUCCESS",
            "claimed_coupon": coupon,
            "total_owned": len(student_claims[req.student_id]),
        }


@app.get("/my-coupons/{student_id}")
async def get_my_coupons(student_id: str):
    if student_id not in student_claims:
        raise HTTPException(status_code=404, detail="ไม่พบรายชื่อในระบบ")

    claims = student_claims[student_id]
    return {
        "student_id": student_id,
        "total_claimed": len(claims),
        "claimed_coupons": claims,
    }


@app.get("/summary")
async def get_summary():
    return {
        "remaining_stock": len(coupons_db) - current_coupon_index,
        "student_claims": student_claims,
    }


if __name__ == "__main__":
    print(f"เปิด Coupon Server ที่ http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"Swagger UI: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
