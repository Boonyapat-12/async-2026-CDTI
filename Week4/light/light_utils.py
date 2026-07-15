import httpx


BASE_URL = "http://172.16.2.117:8088"
STUDENT_ID = "6710301033"
LIGHT_IDS = ("light_1", "light_2", "light_3", "light_4")


async def get_all_lights(client: httpx.AsyncClient) -> dict:
    response = await client.get(f"/api/{STUDENT_ID}/lights")
    response.raise_for_status()
    return response.json()


async def set_light(
    client: httpx.AsyncClient, light_id: str, status: str
) -> dict:
    if light_id not in LIGHT_IDS:
        raise ValueError(f"Unknown light ID: {light_id}")

    normalized_status = status.upper()
    if normalized_status not in ("ON", "OFF"):
        raise ValueError("Light status must be ON or OFF")

    response = await client.post(
        f"/api/{STUDENT_ID}/lights/{light_id}",
        json={"status": normalized_status},
    )
    response.raise_for_status()
    return response.json()


async def reset_all_lights(client: httpx.AsyncClient) -> dict:
    response = await client.delete(f"/api/{STUDENT_ID}/lights/reset")
    response.raise_for_status()
    return response.json()
