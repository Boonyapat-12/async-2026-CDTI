import asyncio  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import time  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

@app.get("/sync-blocking")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
async def blocking_endpoint():  # ประกาศฟังก์ชัน blocking_endpoint สำหรับรวมขั้นตอนการทำงาน
    time.sleep(10)  # Simulate a blocking operation
    return {"message": "Done"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก

