import json
import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx


LIGHT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LIGHT_DIR))

from light_utils import (  # noqa: E402
    BASE_URL,
    LIGHT_IDS,
    STUDENT_ID,
    get_all_lights,
    cleanup_lights,
    reset_all_lights,
    set_light,
    set_lights_concurrently,
)
import light_01  # noqa: E402
import light_02  # noqa: E402


class FakeAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


class TestLightScripts(unittest.IsolatedAsyncioTestCase):
    async def test_sequential_script_uses_verified_cleanup(self):
        responses = [{"light_id": light_id} for light_id in LIGHT_IDS]
        with (
            patch.object(light_01.httpx, "AsyncClient", return_value=FakeAsyncClient()),
            patch.object(light_01, "reset_all_lights", new=AsyncMock()),
            patch.object(light_01, "get_all_lights", new=AsyncMock(return_value={})),
            patch.object(light_01, "set_light", new=AsyncMock(side_effect=responses)),
            patch.object(
                light_01, "cleanup_lights", new=AsyncMock(return_value={})
            ) as cleanup,
            patch("builtins.print"),
        ):
            await light_01.main()

        cleanup.assert_awaited_once()

    async def test_concurrent_script_uses_batch_helper(self):
        responses = [{"light_id": light_id} for light_id in LIGHT_IDS]
        with (
            patch.object(light_02.httpx, "AsyncClient", return_value=FakeAsyncClient()),
            patch.object(light_02, "reset_all_lights", new=AsyncMock()),
            patch.object(light_02, "get_all_lights", new=AsyncMock(return_value={})),
            patch.object(
                light_02,
                "set_lights_concurrently",
                new=AsyncMock(return_value=responses),
            ) as batch,
            patch.object(
                light_02, "cleanup_lights", new=AsyncMock(return_value={})
            ),
            patch("builtins.print"),
        ):
            await light_02.main()

        batch.assert_awaited_once_with(unittest.mock.ANY, "ON")

    async def test_concurrent_script_preserves_original_operation_error(self):
        operation_error = ValueError("operation failed")
        with (
            patch.object(light_02.httpx, "AsyncClient", return_value=FakeAsyncClient()),
            patch.object(light_02, "reset_all_lights", new=AsyncMock()),
            patch.object(light_02, "get_all_lights", new=AsyncMock(return_value={})),
            patch.object(
                light_02,
                "set_lights_concurrently",
                new=AsyncMock(side_effect=operation_error),
            ),
            patch.object(
                light_02, "cleanup_lights", new=AsyncMock(return_value=None)
            ) as cleanup,
            patch("builtins.print"),
        ):
            with self.assertRaises(ValueError) as context:
                await light_02.main()

        self.assertIs(context.exception, operation_error)
        self.assertIs(
            cleanup.await_args.kwargs["original_error"], operation_error
        )


class TestLightUtils(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_batch_waits_for_siblings_before_raising(self):
        slow_request_started = asyncio.Event()
        release_slow_request = asyncio.Event()
        error_response_seen = asyncio.Event()
        completed_requests = []

        async def handler(request):
            light_id = request.url.path.rsplit("/", 1)[-1]
            if light_id == "light_1":
                return httpx.Response(503, json={"detail": "unavailable"})

            slow_request_started.set()
            await release_slow_request.wait()
            completed_requests.append(light_id)
            return httpx.Response(200, json={"light_id": light_id})

        async def notice_error(response):
            if response.status_code == 503:
                error_response_seen.set()

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=BASE_URL,
            event_hooks={"response": [notice_error]},
        ) as client:
            batch = asyncio.create_task(
                set_lights_concurrently(client, "ON")
            )
            await slow_request_started.wait()
            await error_response_seen.wait()
            await asyncio.sleep(0)  # Let the batch observe the HTTP error.

            self.assertFalse(batch.done())
            release_slow_request.set()
            with self.assertRaises(httpx.HTTPStatusError) as context:
                await batch

        self.assertEqual(context.exception.response.status_code, 503)
        self.assertEqual(completed_requests, list(LIGHT_IDS[1:]))

    async def test_concurrent_batch_preserves_light_id_result_order(self):
        async def handler(request):
            light_id = request.url.path.rsplit("/", 1)[-1]
            return httpx.Response(200, json={"light_id": light_id})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            results = await set_lights_concurrently(client, "ON")

        self.assertEqual(
            [result["light_id"] for result in results], list(LIGHT_IDS)
        )

    async def test_cleanup_resets_and_verifies_every_light_is_off(self):
        methods = []

        def handler(request):
            methods.append(request.method)
            if request.method == "DELETE":
                return httpx.Response(200, json={"message": "reset"})
            lights = {
                light_id: {"status": "OFF"} for light_id in LIGHT_IDS
            }
            return httpx.Response(200, json=lights)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            lights = await cleanup_lights(client, settle_delay=0)

        self.assertEqual(methods, ["DELETE", "GET"])
        self.assertTrue(
            all(lights[light_id]["status"] == "OFF" for light_id in LIGHT_IDS)
        )

    async def test_cleanup_raises_clear_error_when_a_light_remains_on(self):
        def handler(request):
            if request.method == "DELETE":
                return httpx.Response(200, json={"message": "reset"})
            lights = {
                light_id: {"status": "OFF"} for light_id in LIGHT_IDS
            }
            lights["light_3"]["status"] = "ON"
            return httpx.Response(200, json=lights)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            with self.assertRaisesRegex(
                RuntimeError, "Cleanup verification failed.*light_3"
            ):
                await cleanup_lights(client, settle_delay=0)

    async def test_cleanup_failure_is_added_to_original_error(self):
        def handler(request):
            return httpx.Response(503, json={"detail": "reset unavailable"})

        original_error = ValueError("operation failed")
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url=BASE_URL
        ) as client:
            result = await cleanup_lights(
                client, settle_delay=0, original_error=original_error
            )

        self.assertIsNone(result)
        self.assertIn("Cleanup also failed", original_error.__notes__[0])
        self.assertIn("503", original_error.__notes__[0])

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
