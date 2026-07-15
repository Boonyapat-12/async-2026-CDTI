import asyncio
from pprint import pprint
from time import perf_counter

import httpx

from light_utils import (
    BASE_URL,
    LIGHT_IDS,
    get_all_lights,
    reset_all_lights,
    set_light,
)


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        await reset_all_lights(client)
        try:
            print("Initial light status:")
            pprint(await get_all_lights(client))

            started = perf_counter()
            responses = await asyncio.gather(
                *(set_light(client, light_id, "ON") for light_id in LIGHT_IDS)
            )
            elapsed = perf_counter() - started

            print("\nConcurrent responses:")
            for light_id, response in zip(LIGHT_IDS, responses):
                print(f"{light_id}: {response}")
            print(f"Elapsed time: {elapsed:.2f} seconds")

            print("\nFinal light status:")
            pprint(await get_all_lights(client))
        finally:
            await reset_all_lights(client)
            print("\nAll lights reset to OFF.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (httpx.HTTPError, ValueError) as error:
        print(f"Error: {error}")
