import json  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import sys  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import unittest  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
from pathlib import Path  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from unittest.mock import AsyncMock, patch  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

import httpx  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


LIGHT_DIR = Path(__file__).resolve().parents[1]  # กำหนดหรือปรับค่าให้ LIGHT_DIR
sys.path.insert(0, str(LIGHT_DIR))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

from light_utils import (  # noqa: E402
    BASE_URL,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    LIGHT_IDS,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    STUDENT_ID,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    get_all_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    cleanup_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    reset_all_lights,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    set_light,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    set_lights_concurrently,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
)  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
import light_01  # noqa: E402
import light_02  # noqa: E402


class FakeAsyncClient:  # ประกาศคลาส FakeAsyncClient สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    async def __aenter__(self):  # ประกาศฟังก์ชัน __aenter__ สำหรับรวมขั้นตอนการทำงาน
        return self  # ส่งผลลัพธ์กลับไปยังผู้เรียก

    async def __aexit__(self, exc_type, exc_value, traceback):  # ประกาศฟังก์ชัน __aexit__ สำหรับรวมขั้นตอนการทำงาน
        return False  # ส่งผลลัพธ์กลับไปยังผู้เรียก


class TestLightScripts(unittest.IsolatedAsyncioTestCase):  # ประกาศคลาส TestLightScripts สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    async def test_sequential_script_uses_verified_cleanup(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        responses = [{"light_id": light_id} for light_id in LIGHT_IDS]  # กำหนดหรือปรับค่าให้ responses
        with (  # เปิดใช้งาน resource ภายใน context manager
            patch.object(light_01.httpx, "AsyncClient", return_value=FakeAsyncClient()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_01, "reset_all_lights", new=AsyncMock()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_01, "get_all_lights", new=AsyncMock(return_value={})),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_01, "set_light", new=AsyncMock(side_effect=responses)),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                light_01, "cleanup_lights", new=AsyncMock(return_value={})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            ) as cleanup,  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            patch("builtins.print"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        ):  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            await light_01.main()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        cleanup.assert_awaited_once()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_concurrent_script_uses_batch_helper(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        responses = [{"light_id": light_id} for light_id in LIGHT_IDS]  # กำหนดหรือปรับค่าให้ responses
        with (  # เปิดใช้งาน resource ภายใน context manager
            patch.object(light_02.httpx, "AsyncClient", return_value=FakeAsyncClient()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_02, "reset_all_lights", new=AsyncMock()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_02, "get_all_lights", new=AsyncMock(return_value={})),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                light_02,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "set_lights_concurrently",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                new=AsyncMock(return_value=responses),  # กำหนดหรือปรับค่าให้ new
            ) as batch,  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            patch.object(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                light_02, "cleanup_lights", new=AsyncMock(return_value={})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            ),  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            patch("builtins.print"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        ):  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            await light_02.main()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        batch.assert_awaited_once_with(unittest.mock.ANY, "ON")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_concurrent_script_preserves_original_operation_error(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        operation_error = ValueError("operation failed")  # กำหนดหรือปรับค่าให้ operation_error
        with (  # เปิดใช้งาน resource ภายใน context manager
            patch.object(light_02.httpx, "AsyncClient", return_value=FakeAsyncClient()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_02, "reset_all_lights", new=AsyncMock()),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(light_02, "get_all_lights", new=AsyncMock(return_value={})),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            patch.object(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                light_02,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                "set_lights_concurrently",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
                new=AsyncMock(side_effect=operation_error),  # กำหนดหรือปรับค่าให้ new
            ),  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            patch.object(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                light_02, "cleanup_lights", new=AsyncMock(return_value=None)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            ) as cleanup,  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            patch("builtins.print"),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        ):  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            with self.assertRaises(ValueError) as context:  # เปิดใช้งาน resource ภายใน context manager
                await light_02.main()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertIs(context.exception, operation_error)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertIs(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            cleanup.await_args.kwargs["original_error"], operation_error  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


class TestLightUtils(unittest.IsolatedAsyncioTestCase):  # ประกาศคลาส TestLightUtils สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    async def test_concurrent_batch_waits_for_siblings_before_raising(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        slow_request_started = asyncio.Event()  # กำหนดหรือปรับค่าให้ slow_request_started
        release_slow_request = asyncio.Event()  # กำหนดหรือปรับค่าให้ release_slow_request
        error_response_seen = asyncio.Event()  # กำหนดหรือปรับค่าให้ error_response_seen
        completed_requests = []  # กำหนดหรือปรับค่าให้ completed_requests

        async def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            light_id = request.url.path.rsplit("/", 1)[-1]  # กำหนดหรือปรับค่าให้ light_id
            if light_id == "light_1":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                return httpx.Response(503, json={"detail": "unavailable"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

            slow_request_started.set()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            await release_slow_request.wait()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            completed_requests.append(light_id)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json={"light_id": light_id})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async def notice_error(response):  # ประกาศฟังก์ชัน notice_error สำหรับรวมขั้นตอนการทำงาน
            if response.status_code == 503:  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                error_response_seen.set()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler),  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            base_url=BASE_URL,  # กำหนดหรือปรับค่าให้ base_url
            event_hooks={"response": [notice_error]},  # กำหนดหรือปรับค่าให้ event_hooks
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            batch = asyncio.create_task(  # สร้าง task เพื่อให้ coroutine ทำงานแบบ concurrent
                set_lights_concurrently(client, "ON")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            await slow_request_started.wait()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            await error_response_seen.wait()  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
            await asyncio.sleep(0)  # Let the batch observe the HTTP error.

            self.assertFalse(batch.done())  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            release_slow_request.set()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            with self.assertRaises(httpx.HTTPStatusError) as context:  # เปิดใช้งาน resource ภายใน context manager
                await batch  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(context.exception.response.status_code, 503)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(completed_requests, list(LIGHT_IDS[1:]))  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_concurrent_batch_preserves_light_id_result_order(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        async def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            light_id = request.url.path.rsplit("/", 1)[-1]  # กำหนดหรือปรับค่าให้ light_id
            return httpx.Response(200, json={"light_id": light_id})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            results = await set_lights_concurrently(client, "ON")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            [result["light_id"] for result in results], list(LIGHT_IDS)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    async def test_cleanup_resets_and_verifies_every_light_is_off(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        methods = []  # กำหนดหรือปรับค่าให้ methods

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            methods.append(request.method)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
            if request.method == "DELETE":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                return httpx.Response(200, json={"message": "reset"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก
            lights = {  # กำหนดหรือปรับค่าให้ lights
                light_id: {"status": "OFF"} for light_id in LIGHT_IDS  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            return httpx.Response(200, json=lights)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            lights = await cleanup_lights(client, settle_delay=0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(methods, ["DELETE", "GET"])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertTrue(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            all(lights[light_id]["status"] == "OFF" for light_id in LIGHT_IDS)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    async def test_cleanup_raises_clear_error_when_a_light_remains_on(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            if request.method == "DELETE":  # ตรวจสอบเงื่อนไขก่อนเลือกเส้นทางการทำงาน
                return httpx.Response(200, json={"message": "reset"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก
            lights = {  # กำหนดหรือปรับค่าให้ lights
                light_id: {"status": "OFF"} for light_id in LIGHT_IDS  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
            lights["light_3"]["status"] = "ON"  # กำหนดหรือปรับค่าให้ lights["light_3"]["status"]
            return httpx.Response(200, json=lights)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            with self.assertRaisesRegex(  # เปิดใช้งาน resource ภายใน context manager
                RuntimeError, "Cleanup verification failed.*light_3"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            ):  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
                await cleanup_lights(client, settle_delay=0)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

    async def test_cleanup_failure_is_added_to_original_error(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            return httpx.Response(503, json={"detail": "reset unavailable"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        original_error = ValueError("operation failed")  # กำหนดหรือปรับค่าให้ original_error
        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            result = await cleanup_lights(  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop
                client, settle_delay=0, original_error=original_error  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        self.assertIsNone(result)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertIn("Cleanup also failed", original_error.__notes__[0])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertIn("503", original_error.__notes__[0])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_get_all_lights_uses_exact_path_and_returns_json(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests
        payload = {"light_1": {"status": "OFF"}}  # กำหนดหรือปรับค่าให้ payload

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json=payload)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            result = await get_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(result, payload)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(len(requests), 1)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(requests[0].method, "GET")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(requests[0].url.path, f"/api/{STUDENT_ID}/lights")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_set_light_uses_exact_path_and_uppercase_json_body(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests
        payload = {  # กำหนดหรือปรับค่าให้ payload
            "student_id": STUDENT_ID,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "light_id": "light_2",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "current_status": "ON",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json=payload)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            result = await set_light(client, "light_2", "on")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(result, payload)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(len(requests), 1)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(requests[0].method, "POST")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            requests[0].url.path, f"/api/{STUDENT_ID}/lights/light_2"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        self.assertEqual(json.loads(requests[0].content), {"status": "ON"})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_set_light_normalizes_lowercase_off(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json={"current_status": "OFF"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            await set_light(client, "light_1", "off")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(json.loads(requests[0].content), {"status": "OFF"})  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_set_light_rejects_invalid_light_id_without_request(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json={})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            with self.assertRaises(ValueError):  # เปิดใช้งาน resource ภายใน context manager
                await set_light(client, "light_5", "ON")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(requests, [])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_set_light_rejects_invalid_status_without_request(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json={})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            with self.assertRaises(ValueError):  # เปิดใช้งาน resource ภายใน context manager
                await set_light(client, LIGHT_IDS[0], "DIM")  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(requests, [])  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    async def test_reset_all_lights_uses_exact_path_and_returns_json(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        requests = []  # กำหนดหรือปรับค่าให้ requests
        payload = {"message": "reset complete"}  # กำหนดหรือปรับค่าให้ payload

        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            requests.append(request)  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
            return httpx.Response(200, json=payload)  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            result = await reset_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(result, payload)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(len(requests), 1)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(requests[0].method, "DELETE")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        self.assertEqual(  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            requests[0].url.path, f"/api/{STUDENT_ID}/lights/reset"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        )  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

    async def test_http_error_status_is_propagated(self):  # ประกาศกรณีทดสอบสำหรับตรวจสอบพฤติกรรมของโค้ด
        def handler(request):  # ประกาศฟังก์ชัน handler สำหรับรวมขั้นตอนการทำงาน
            return httpx.Response(503, json={"detail": "unavailable"})  # ส่งผลลัพธ์กลับไปยังผู้เรียก

        async with httpx.AsyncClient(  # เปิดใช้งาน resource ภายใน context manager
            transport=httpx.MockTransport(handler), base_url=BASE_URL  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        ) as client:  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            with self.assertRaises(httpx.HTTPStatusError) as context:  # เปิดใช้งาน resource ภายใน context manager
                await get_all_lights(client)  # รอผลลัพธ์ของงาน asynchronous โดยไม่บล็อก event loop

        self.assertEqual(context.exception.response.status_code, 503)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    unittest.main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
