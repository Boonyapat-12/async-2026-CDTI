import asyncio

import httpx


BASE_URL = "http://172.16.2.117:8088"
STUDENT_ID = "6710301033"
LIGHT_IDS = ("light_1", "light_2", "light_3", "light_4")
HARDWARE_SETTLE_DELAY = 2.0


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


async def set_lights_concurrently(
    client: httpx.AsyncClient, status: str
) -> list[dict]:
    """Set every light concurrently, then report the first failure."""
    results = await asyncio.gather(
        *(set_light(client, light_id, status) for light_id in LIGHT_IDS),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, BaseException):
            raise result

    return results


async def reset_all_lights(client: httpx.AsyncClient) -> dict:
    response = await client.delete(f"/api/{STUDENT_ID}/lights/reset")
    response.raise_for_status()
    return response.json()


async def cleanup_lights(
    client: httpx.AsyncClient,
    settle_delay: float = HARDWARE_SETTLE_DELAY,
    original_error: BaseException | None = None,
) -> dict | None:
    """Wait for accepted operations, reset, and verify every light is OFF."""
    try:
        await asyncio.sleep(settle_delay)
        await reset_all_lights(client)
        lights = await get_all_lights(client)

        lights_not_off = [
            light_id
            for light_id in LIGHT_IDS
            if lights.get(light_id, {}).get("status") != "OFF"
        ]
        if lights_not_off:
            names = ", ".join(lights_not_off)
            raise RuntimeError(
                f"Cleanup verification failed; lights not OFF: {names}"
            )

        return lights
    except Exception as cleanup_error:
        if original_error is None:
            raise
        original_error.add_note(f"Cleanup also failed: {cleanup_error}")
        return None
