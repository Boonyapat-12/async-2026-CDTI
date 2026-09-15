import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


BASE_URL = "http://172.16.2.117:8088"  # กำหนดหรือปรับค่าให้ BASE_URL
STUDENT_ID = "6710301033"  # กำหนดหรือปรับค่าให้ STUDENT_ID
LIGHT_IDS = ("light_1", "light_2", "light_3", "light_4")  # กำหนดหรือปรับค่าให้ LIGHT_IDS
HARDWARE_SETTLE_DELAY = 2.0  # กำหนดหรือปรับค่าให้ HARDWARE_SETTLE_DELAY


async def get_all_lights(client: httpx.AsyncClient) -> dict:  # ประกาศฟังก์ชัน get_all_lights สำหรับรวมขั้นตอนการทำงาน
    response = await client.get(f"/api/{STUDENT_ID}/lights")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    return response.json()  # ส่งผลลัพธ์กลับไปยังผู้เรียก


async def set_light(  # ประกาศฟังก์ชัน set_light สำหรับรวมขั้นตอนการทำงาน
    client: httpx.AsyncClient, light_id: str, status: str  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
) -> dict:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
    if light_id not in LIGHT_IDS:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        raise ValueError(f"Unknown light ID: {light_id}")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

    normalized_status = status.upper()  # กำหนดหรือปรับค่าให้ normalized_status
    if normalized_status not in ("ON", "OFF"):  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        raise ValueError("Light status must be ON or OFF")  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

    response = await client.post(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        f"/api/{STUDENT_ID}/lights/{light_id}",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        json={"status": normalized_status},  # กำหนดหรือปรับค่าให้ json
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
    response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    return response.json()  # ส่งผลลัพธ์กลับไปยังผู้เรียก


async def set_lights_concurrently(  # ประกาศฟังก์ชัน set_lights_concurrently สำหรับรวมขั้นตอนการทำงาน
    client: httpx.AsyncClient, status: str  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
) -> list[dict]:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
    """Set every light concurrently, then report the first failure."""
    results = await asyncio.gather(  # รันงาน asynchronous หลายงานพร้อมกันและรวมผลลัพธ์
        *(set_light(client, light_id, status) for light_id in LIGHT_IDS),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        return_exceptions=True,  # ส่งผลลัพธ์กลับไปยังผู้เรียก
    )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    for result in results:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        if isinstance(result, BaseException):  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            raise result  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ

    return results  # ส่งผลลัพธ์กลับไปยังผู้เรียก


async def reset_all_lights(client: httpx.AsyncClient) -> dict:  # ประกาศฟังก์ชัน reset_all_lights สำหรับรวมขั้นตอนการทำงาน
    response = await client.delete(f"/api/{STUDENT_ID}/lights/reset")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
    response.raise_for_status()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    return response.json()  # ส่งผลลัพธ์กลับไปยังผู้เรียก


async def cleanup_lights(  # ประกาศฟังก์ชัน cleanup_lights สำหรับรวมขั้นตอนการทำงาน
    client: httpx.AsyncClient,  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
    settle_delay: float = HARDWARE_SETTLE_DELAY,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    original_error: BaseException | None = None,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
) -> dict | None:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
    """Wait for accepted operations, reset, and verify every light is OFF."""
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        await asyncio.sleep(settle_delay)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        await reset_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        lights = await get_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        lights_not_off = [  # กำหนดหรือปรับค่าให้ lights_not_off
            light_id  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            for light_id in LIGHT_IDS  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
            if lights.get(light_id, {}).get("status") != "OFF"  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
        ]  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        if lights_not_off:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            names = ", ".join(lights_not_off)  # กำหนดหรือปรับค่าให้ names
            raise RuntimeError(  # สร้างหรือส่งต่อข้อผิดพลาดให้ผู้เรียกจัดการ
                f"Cleanup verification failed; lights not OFF: {names}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        return lights  # ส่งผลลัพธ์กลับไปยังผู้เรียก
    except Exception as cleanup_error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        if original_error is None:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
            raise  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        original_error.add_note(f"Cleanup also failed: {cleanup_error}")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        return None  # ส่งผลลัพธ์กลับไปยังผู้เรียก
