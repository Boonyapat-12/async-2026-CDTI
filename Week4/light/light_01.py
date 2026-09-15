import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from pprint import pprint  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from time import perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

from light_utils import (  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
    BASE_URL,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    LIGHT_IDS,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    cleanup_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    get_all_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    reset_all_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    set_light,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
)  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


async def main() -> None:  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    async with httpx.AsyncClient(base_url=BASE_URL) as client:  # เปิดใช้งาน resource ภายใน context manager
        await reset_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
        operation_error = None  # กำหนดหรือปรับค่าให้ operation_error
        try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
            print("Initial light status:")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            pprint(await get_all_lights(client))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

            started = perf_counter()  # กำหนดหรือปรับค่าให้ started
            responses = []  # กำหนดหรือปรับค่าให้ responses
            for light_id in LIGHT_IDS:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                responses.append(await set_light(client, light_id, "ON"))  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
            elapsed = perf_counter() - started  # กำหนดหรือปรับค่าให้ elapsed

            print("\nSequential responses:")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            for light_id, response in zip(LIGHT_IDS, responses):  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
                print(f"{light_id}: {response}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            print(f"Elapsed time: {elapsed:.2f} seconds")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

            print("\nFinal light status:")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
            pprint(await get_all_lights(client))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        except BaseException as error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            operation_error = error  # กำหนดหรือปรับค่าให้ operation_error
            raise  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        except BaseException as error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
            operation_error = error  # กำหนดหรือปรับค่าให้ operation_error
            raise  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        finally:  # ทำงานเก็บกวาดเสมอไม่ว่าผลลัพธ์จะสำเร็จหรือเกิดข้อผิดพลาด
            # เพิ่มเงื่อนไข: จะ cleanup ก็ต่อเมื่อเกิด error เท่านั้น
            if operation_error is not None:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                lights = await cleanup_lights(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                    client, original_error=operation_error  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
                if lights is not None:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                    print("\nError occurred: All lights reset and verified OFF.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    try:  # เริ่มบล็อกสำหรับดักจับข้อผิดพลาด
        asyncio.run(main())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    except (httpx.HTTPError, ValueError) as error:  # จัดการข้อผิดพลาดชนิดที่ระบุ
        print(f"Error: {error}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
