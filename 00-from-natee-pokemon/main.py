import asyncio
import aiohttp

async def fetch_pokemon(pokemon_name: str):
    """
    Coroutine ดึงข้อมูลจาก PokéAPI โดยใช้ aiohttp:
    1. ส่ง GET Request ไปยัง PokéAPI
    2. อ่าน JSON และดึงค่าประเภทแรก (types[0]['type']['name'])
    3. return dict {"name": pokemon_name, "type": primary_type}
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            primary_type = data['types'][0]['type']['name']
            return {"name": pokemon_name, "type": primary_type}

async def get_pokemons_info():
    pokemons = ["ditto", "pikachu", "charizard"]
    tasks = await asyncio.gather(
        *[fetch_pokemon(name) for name in pokemons]
    )

    print(tasks)
    print(type(tasks))
    return tasks

if __name__ == "__main__":
    asyncio.run(get_pokemons_info())