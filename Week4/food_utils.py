# food_utils.py
import httpx

async def send_order_to_kitchen(student_id: str, shop_name: str, menu_name: str) -> dict:
    url = f"http://172.16.2.117:8088/order/{shop_name}"
    payload = {"student_id": student_id, "menu_name": menu_name}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "ERROR", "detail": f"HTTP Error {response.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "detail": f"Connection failed: {e}"}