import pytest
import main


# test 1: ตรวจสอบโครงสร้างว่ามีฟังก์ชันที่กำหนด
@pytest.mark.score(5)
def test_function_structure():
    assert hasattr(main, "fetch_pokemon"), "ไม่มีฟังก์ชัน fetch_pokemon"
    assert hasattr(main, "get_pokemons_info"), "ไม่มีฟังก์ชัน get_pokemons_info"


# test 2: ทดสอบการดึงข้อมูล Pokémon 1 ตัว
@pytest.mark.asyncio
@pytest.mark.score(7)
async def test_fetch_single_pokemon():
    res = await main.fetch_pokemon("pikachu")

    assert isinstance(res, dict), "fetch_pokemon ต้อง return เป็น dict"
    assert res.get("name") == "pikachu", "ชื่อ Pokémon ไม่ถูกต้อง"
    assert res.get("type") == "electric", "type ของ pikachu ต้องเป็น electric"


# test 3: ทดสอบ asyncio.gather สำหรับ 3 ตัว
@pytest.mark.asyncio
@pytest.mark.score(8)
async def test_gather_pokemons_info():
    results = await main.get_pokemons_info()

    expected = [
        {"name": "ditto", "type": "normal"},
        {"name": "pikachu", "type": "electric"},
        {"name": "charizard", "type": "fire"},
    ]

    assert isinstance(
        results, (list, tuple)
    ), "ผลลัพธ์ต้องเป็น list หรือ tuple"

    assert len(results) == 3, (
        f"ต้องมีข้อมูล 3 ตัว แต่ได้รับ {len(results)}"
    )

    for i, exp in enumerate(expected):
        assert results[i]["name"].lower() == exp["name"], (
            f"ผลลัพธ์ตัวที่ {i} ชื่อไม่ตรงกับที่คาด"
        )

        assert results[i]["type"].lower() == exp["type"], (
            f"ผลลัพธ์ตัวที่ {i} type ไม่ตรงกับที่คาด"
        )