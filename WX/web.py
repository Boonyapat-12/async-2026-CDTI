import asyncio
import httpx

# ฟังก์ชันดึงชื่อผู้ใช้แบบ Async ผ่าน HTTPS
async def get_user_name(user_id):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()["name"]

async def main():
    # รันแบบ Asynchronous ขนานกัน (ยิงพร้อมกัน 2 Requests)
    name1, name2 = await asyncio.gather(get_user_name(1), get_user_name(2))
    print(f"User 1: {name1} | User 2: {name2}")

if __name__ == "__main__":
    asyncio.run(main())
    