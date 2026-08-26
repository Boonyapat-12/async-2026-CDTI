import asyncio

import httpx

SERVER_URL = "http://127.0.0.1:8088"
MY_STUDENT_ID = "6710301033"


async def hunt_coupons() -> None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        print(f"[{MY_STUDENT_ID}] เริ่มต้นภารกิจล่าคูปอง...")

        for attempt in range(1, 6):
            response = await client.post(
                f"{SERVER_URL}/claim",
                json={"student_id": MY_STUDENT_ID},
            )
            response.raise_for_status()
            data = response.json()
            status = data["status"]
            result = data.get("message", data.get("claimed_coupon"))
            print(f"  -- ครั้งที่ {attempt}: [{status}] -> {result}")

            if status in {"LIMIT_REACHED", "OUT_OF_STOCK"}:
                break

            await asyncio.sleep(0.02)

        print("\nกำลังดึงสรุปคูปองของตนเอง...")
        response = await client.get(
            f"{SERVER_URL}/my-coupons/{MY_STUDENT_ID}"
        )
        response.raise_for_status()
        my_summary = response.json()
        print(
            f"สรุปของ [{MY_STUDENT_ID}]: "
            f"ได้รับคูปองรวม {my_summary['total_claimed']} ใบ -> "
            f"{my_summary['claimed_coupons']}"
        )

        print("\nกำลังดึงสรุปภาพรวมคูปองทั้งหมดจาก Server...")
        response = await client.get(f"{SERVER_URL}/summary")
        response.raise_for_status()
        summary = response.json()
        print(f"จำนวนคูปองคงเหลือ: {summary['remaining_stock']} ใบ")

        for student_id, coupons in summary["student_claims"].items():
            print(
                f" - {student_id}: ได้รับ {len(coupons)} ใบ -> {coupons}"
            )


if __name__ == "__main__":
    try:
        asyncio.run(hunt_coupons())
    except httpx.HTTPError as error:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ Server: {error}")
