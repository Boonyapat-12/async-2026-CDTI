# stock_api.py  # ไฟล์นี้เป็น Mock Stock API Server สำหรับให้ stock_price_httpx.py ยิง request เข้ามา
from fastapi import FastAPI  # import FastAPI เพื่อสร้างเว็บ API server
import asyncio  # import asyncio เพื่อจำลอง latency ของแต่ละ endpoint ด้วย async sleep

app = FastAPI(title="Asyncio Week 3 Mock Stock API")  # สร้างแอป FastAPI และตั้งชื่อ API สำหรับดูใน docs

@app.get("/price/{server_name}")  # ประกาศ endpoint แบบ GET โดยรับชื่อ server ผ่าน path เช่น /price/Beta
async def get_stock_price(server_name: str):  # coroutine endpoint ที่รับชื่อ server เป็น string
    """ API จำลองราคาหุ้น โดยแต่ละสาขาจะมีความหน่วง (Latency) ไม่เท่ากัน """  # docstring อธิบายว่า API นี้จำลองราคาและความหน่วง
    name_lower = server_name.lower()  # แปลงชื่อ server เป็นตัวพิมพ์เล็ก เพื่อให้เทียบชื่อได้ง่ายและไม่สนตัวใหญ่เล็ก
    
    if name_lower == "alpha":  # ถ้าผู้ใช้เรียก server Alpha
        await asyncio.sleep(3.0)  # ช้าที่สุด
        price = 152.50  # กำหนดราคาหุ้นจำลองของ Alpha
    elif name_lower == "beta":  # ถ้าผู้ใช้เรียก server Beta
        await asyncio.sleep(0.8)  # เร็วที่สุด!
        price = 149.80  # กำหนดราคาหุ้นจำลองของ Beta
    elif name_lower == "gamma":  # ถ้าผู้ใช้เรียก server Gamma
        await asyncio.sleep(1.5)  # ปานกลาง
        price = 150.20  # กำหนดราคาหุ้นจำลองของ Gamma
    else:  # ถ้าชื่อ server ไม่ใช่ Alpha, Beta หรือ Gamma
        await asyncio.sleep(0.1)  # รอสั้น ๆ เพื่อจำลองการตอบกลับของ server อื่น
        price = 100.00  # กำหนดราคาค่าเริ่มต้นให้ server ที่ไม่รู้จัก
        
    return {  # ส่งข้อมูลกลับเป็น JSON response
        "server": server_name,  # คืนชื่อ server ตามที่ผู้ใช้ส่งเข้ามา
        "price_usd": price,  # คืนราคาหุ้นหน่วย USD
        "status": "success"  # คืนสถานะว่า request สำเร็จ
    }  # ปิด dictionary ของ response


if __name__ == "__main__":  # ถ้ารันไฟล์นี้โดยตรง ให้เริ่ม server ทันที
    import uvicorn  # import uvicorn ซึ่งเป็น ASGI server สำหรับรัน FastAPI

    uvicorn.run(app, host="0.0.0.0", port=8088)  # รัน API บนทุก network interface ที่ port 8088


# pip install fastapi uvicorn httpx  # คำสั่งติดตั้ง library ที่ต้องใช้กับ lab นี้
# วิธีรันเซิร์ฟเวอร์: python stock_api.py  # วิธีรันแบบง่ายโดยใช้ block __main__ ด้านบน
# หรือ uvicorn stock_api:app --reload --port 8088  # วิธีรันผ่าน uvicorn โดยตรงพร้อม reload ตอนแก้ไฟล์