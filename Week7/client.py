import asyncio
import httpx

SERVER_IP = "172.20.58.26"
PORT = "8088"
SERVER_URL = f"http://{SERVER_IP}:{PORT}"

# ระบุรหัส/ชื่อนักเรียนของผู้เล่น
MY_STUDENT_ID = "6710301033"

async def hunt_coupons():
    async with httpx.AsyncClient() as client:
        print(f"[{MY_STUDENT_ID}] เริ่มต้นภารกิจล่าคูปอง...")

        # ยิงขอคูปองต่อเนื่องสูงสุด 5 ครั้ง เพื่อพยายามเก็บให้ได้ครบ 2 ใบ
        for attempt in range(1, 6):
            try:
                res = await client.post(
                    f"{SERVER_URL}/claim",
                    json={"student_id": MY_STUDENT_ID},
                    timeout=5.0
                )
                data = res.json()
                status = data.get("status")

                print(f"  -- ครั้งที่ {attempt}: [{status}] -> {data.get('message', data.get('claimed_coupon'))}")

                # หากได้ครบ 2 ใบ หรือคูปองหมดแล้ว ให้หยุดยิงทันที
                if status in ["LIMIT_REACHED", "OUT_OF_STOCK"]:
                    break

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

            # พักก่อนยิงรอบถัดไปเล็กน้อย
            await asyncio.sleep(0.01)

        # ------------------------------------------------------------
        # 1. ดึงสรุปคูปองส่วนตัว (เฉพาะของ MY_STUDENT_ID)
        # ------------------------------------------------------------
        print("\nกำลังดึงสรุปคูปองของตนเอง...")
        try:
            res = await client.get(f"{SERVER_URL}/my-coupons/{MY_STUDENT_ID}")
            if res.status_code == 200:
                summary = res.json()
                total = summary.get("total_claimed", 0)
                coupons = summary.get("claimed_coupons", [])
                print(f"สรุปของ [{MY_STUDENT_ID}]: ได้รับคูปองรวม {total} ใบ -> {coupons}")
            else:
                print(f"ดึงข้อมูลส่วนตัวไม่สำเร็จ Status Code: {res.status_code}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดึงข้อมูลส่วนตัว: {e}")

        # ------------------------------------------------------------
        # 2. เพิ่มการดึงสรุปภาพรวมทั้งหมด (/summary)
        # ------------------------------------------------------------
        print("\n กำลังดึงสรุปภาพรวมคูปองทั้งหมดจาก Server (/summary)...")
        try:
            res = await client.get(f"{SERVER_URL}/summary")
            if res.status_code == 200:
                summary_all = res.json()
                rem_stock = summary_all.get("remaining_stock", "N/A")
                claims = summary_all.get("student_claims", {})

                print(f"จำนวนคูปองคงเหลือใน Server: {rem_stock} ใบ")
                print("รายการคูปองที่นักเรียนแต่ละคนได้รับ:")

                for sid, coupons in claims.items():
                    print(f" -  {sid}: ได้รับ {len(coupons)} ใบ -> {coupons}")
            else:
                print(f"ดึงข้อมูลสรุปภาพรวมไม่สำเร็จ Status Code: {res.status_code}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดึงสรุปภาพรวม: {e}")

if __name__ == "__main__":
    asyncio.run(hunt_coupons())
