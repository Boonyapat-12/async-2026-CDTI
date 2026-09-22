# PreFinall Quiz: Questions 1–6
# แหล่งที่มา: https://persevere.cdti.ac.th/mod/quiz/review.php?attempt=23639&cmid=3974
# เอกสารนี้ย้ายโจทย์ ข้อกำหนด ตัวอย่างผลลัพธ์ เกณฑ์การประเมิน และ code จากหน้า quiz โดยไม่ตัดเนื้อหาออก
#
# ข้อ 6 — การดึงข้อมูลโปเกมอนจาก PokéAPI แบบ Asynchronous
#
# โจทย์
# ให้นักเรียนสร้าง Coroutine สำหรับดึงข้อมูลชื่อและประเภท (Type) ของโปเกมอนจาก PokéAPI จำนวน 3 ตัวพร้อมกันด้วย aiohttp หรือ urllib ร่วมกับ asyncio.gather()
#
# ข้อกำหนด
# - สร้าง Coroutine ฟังก์ชัน async def fetch_pokemon(pokemon_name: str):
# - ดึงข้อมูลจาก URL: https://pokeapi.co/api/v2/pokemon/{pokemon_name}
# - สกัดเอาข้อมูล Primary Type (ประเภทแรกในรายการ types) ออกมา
# - คืนค่า (return) เป็น dict ในรูปแบบ: {"name": pokemon_name, "type": primary_type}
# - สร้างฟังก์ชันหลัก async def get_pokemons_info():
# - เรียกใช้ fetch_pokemon พร้อมกัน 3 ตัวผ่าน asyncio.gather() ได้แก่: "ditto", "pikachu" และ "charizard"
# - คืนค่า (return) เป็น list ของข้อมูลโปเกมอนทั้ง 3 ตัวตามลำดับ
#
# ตัวอย่างผลลัพธ์ (Output)
# [
#   {'name': 'ditto', 'type': 'normal'},
#   {'name': 'pikachu', 'type': 'electric'},
#   {'name': 'charizard', 'type': 'fire'}
# ]
#
# เกณฑ์การประเมิน (คะแนนเต็ม 20 คะแนน)
# - 5 คะแนน: นิยามฟังก์ชันและเซตโครงสร้าง Async I/O ได้ถูกต้อง
# - 7 คะแนน: ดึงข้อมูล API และ Parse ค่า JSON เอา Primary Type ออกมาได้ถูกต้อง
# - 8 คะแนน: ใช้ asyncio.gather() ดึงข้อมูลทั้ง 3 รายการพร้อมกันได้สำเร็จ

import asyncio  # นำเข้าโมดูล asyncio สำหรับรันคำขอหลายรายการแบบ concurrent
import httpx  # นำเข้าไลบรารี httpx สำหรับส่ง HTTP request แบบ asynchronous


async def fetch_pokemon(pokemon_name: str):  # ประกาศ coroutine สำหรับดึงชื่อและประเภทแรกของโปเกมอนหนึ่งตัว
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"  # สร้าง URL ของ PokéAPI ตามชื่อโปเกมอนที่รับเข้ามา

    async with httpx.AsyncClient() as client:  # สร้าง asynchronous HTTP client และปิดทรัพยากรให้อัตโนมัติเมื่อใช้งานเสร็จ
        response = await client.get(url)  # ส่งคำขอ GET ไปยัง PokéAPI และรอผลลัพธ์แบบไม่บล็อกงานอื่น
        response.raise_for_status()  # แจ้งข้อผิดพลาดทันทีหาก API ตอบสถานะ HTTP ที่ไม่สำเร็จ
        data = response.json()  # แปลงข้อมูล JSON ที่ตอบกลับมาเป็น dictionary ของ Python

        primary_type = data["types"][0]["type"]["name"]  # อ่านชื่อประเภทแรกจากรายการ types ของโปเกมอน

        return {"name": pokemon_name, "type": primary_type}  # คืน dictionary ที่มีชื่อและประเภทแรกของโปเกมอน


async def get_pokemons_info():  # ประกาศ coroutine หลักสำหรับดึงข้อมูลโปเกมอนสามตัวพร้อมกัน
    pokemon_name = await asyncio.gather(  # รัน coroutine ดึงข้อมูลโปเกมอนทั้งสามพร้อมกันและเก็บผลลัพธ์เป็น list
        fetch_pokemon("ditto"),  # ดึงข้อมูลของ ditto
        fetch_pokemon("pikachu"),  # ดึงข้อมูลของ pikachu
        fetch_pokemon("charizard"),  # ดึงข้อมูลของ charizard
    )  # ปิดรายการ coroutine ที่ส่งให้ asyncio.gather
    print(pokemon_name)  # แสดง list ข้อมูลโปเกมอนทั้งสามตัว
    return pokemon_name  # คืน list ข้อมูลโปเกมอนให้ผู้เรียกใช้ฟังก์ชัน


asyncio.run(get_pokemons_info())  # สร้าง event loop และเริ่มรัน coroutine หลัก
