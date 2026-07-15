import json
import sys
import unittest
from pathlib import Path

import httpx


LIGHT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LIGHT_DIR))

from light_utils import (  # noqa: E402
    BASE_URL,
    LIGHT_IDS,
    STUDENT_ID,
    get_all_lights,
    reset_all_lights,
    set_light,
)


class TestLightUtils(unittest.IsolatedAsyncioTestCase):
    async def test_get_all_lights_uses_exact_path_and_returns_json(self):
        requests = []
        payload = {"light_1": {"status": "OFF"}}

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json=payload)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            result = await get_all_lights(client)

        self.assertEqual(result, payload)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, "GET")
        self.assertEqual(requests[0].url.path, f"/api/{STUDENT_ID}/lights")

    async def test_set_light_uses_exact_path_and_uppercase_json_body(self):
        requests = []
        payload = {
            "student_id": STUDENT_ID,
            "light_id": "light_2",
            "current_status": "ON",
        }

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json=payload)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            result = await set_light(client, "light_2", "on")

        self.assertEqual(result, payload)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(
            requests[0].url.path, f"/api/{STUDENT_ID}/lights/light_2"
        )
        self.assertEqual(json.loads(requests[0].content), {"status": "ON"})

    async def test_set_light_normalizes_lowercase_off(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={"current_status": "OFF"})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            await set_light(client, "light_1", "off")

        self.assertEqual(json.loads(requests[0].content), {"status": "OFF"})

    async def test_set_light_rejects_invalid_light_id_without_request(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            with self.assertRaises(ValueError):
                await set_light(client, "light_5", "ON")

        self.assertEqual(requests, [])

    async def test_set_light_rejects_invalid_status_without_request(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            with self.assertRaises(ValueError):
                await set_light(client, LIGHT_IDS[0], "DIM")

        self.assertEqual(requests, [])

    async def test_reset_all_lights_uses_exact_path_and_returns_json(self):
        requests = []
        payload = {"message": "reset complete"}

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json=payload)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            result = await reset_all_lights(client)

        self.assertEqual(result, payload)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, "DELETE")
        self.assertEqual(
            requests[0].url.path, f"/api/{STUDENT_ID}/lights/reset"
        )

    async def test_http_error_status_is_propagated(self):
        def handler(request):
            return httpx.Response(503, json={"detail": "unavailable"})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            with self.assertRaises(httpx.HTTPStatusError) as context:
                await get_all_lights(client)

        self.assertEqual(context.exception.response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
