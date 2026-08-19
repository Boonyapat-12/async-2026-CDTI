import asyncio
import unittest

import httpx

from server_example import STUDENTS, app, reset_coupon_state


async def request(method: str, path: str, **kwargs) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **kwargs)


class ServerExampleTests(unittest.TestCase):
    def setUp(self):
        reset_coupon_state()

    def test_my_coupons_returns_only_requested_students_claims(self):
        student_id = STUDENTS[0]

        first_claim = asyncio.run(
            request("POST", "/claim", json={"student_id": student_id})
        )
        second_claim = asyncio.run(
            request("POST", "/claim", json={"student_id": student_id})
        )
        response = asyncio.run(request("GET", f"/my-coupons/{student_id}"))

        self.assertEqual(first_claim.json()["status"], "SUCCESS")
        self.assertEqual(second_claim.json()["status"], "SUCCESS")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "student_id": student_id,
                "total_claimed": 2,
                "claimed_coupons": ["COUPON_01", "COUPON_02"],
            },
        )

    def test_my_coupons_rejects_unknown_student(self):
        response = asyncio.run(request("GET", "/my-coupons/unknown"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "ไม่พบรายชื่อในระบบ")


if __name__ == "__main__":
    unittest.main()
