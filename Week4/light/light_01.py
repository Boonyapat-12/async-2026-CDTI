import asyncio
from pprint import pprint
from time import perf_counter

import httpx

from light_utils import (
    BASE_URL,
    LIGHT_IDS,
    cleanup_lights,
    get_all_lights,
    reset_all_lights,
    set_light,
)


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        await reset_all_lights(client)
        operation_error = None
        try:
            print("Initial light status:")
            pprint(await get_all_lights(client))

            started = perf_counter()
            responses = []
            for light_id in LIGHT_IDS:
                responses.append(await set_light(client, light_id, "ON"))
            elapsed = perf_counter() - started

            print("\nSequential responses:")
            for light_id, response in zip(LIGHT_IDS, responses):
                print(f"{light_id}: {response}")
            print(f"Elapsed time: {elapsed:.2f} seconds")

            print("\nFinal light status:")
            pprint(await get_all_lights(client))
        except BaseException as error:
            operation_error = error
            raise
        except BaseException as error:
            operation_error = error
            raise
        finally:
            # เพิ่มเงื่อนไข: จะ cleanup ก็ต่อเมื่อเกิด error เท่านั้น
            if operation_error is not None:
                lights = await cleanup_lights(
                    client, original_error=operation_error
                )
                if lights is not None:
                    print("\nError occurred: All lights reset and verified OFF.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (httpx.HTTPError, ValueError) as error:
        print(f"Error: {error}")
