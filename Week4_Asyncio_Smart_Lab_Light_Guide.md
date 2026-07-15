# Week 4 Asyncio Smart Lab Light Guide

คู่มือนี้เขียนสำหรับใบเพื่อใช้อ่านทำความเข้าใจและทบทวนก่อนสอบ โดยอ้างอิงจาก:

- API specification: `Week4/light/Readme.md`
- โปรแกรมที่ใช้ทำ Lab: `Week4/light/light_01.py` และ `Week4/light/light_02.py`
- REST helper: `Week4/light/light_utils.py`
- Dashboard ของใบ: `http://172.16.2.117:8088/6710301033`
- Student ID: `6710301033`

> เป้าหมาย: อ่านจบแล้วอธิบายได้ว่า Python client, REST API, Server และ WebSocket Dashboard ทำงานร่วมกันอย่างไร รวมถึงเข้าใจว่าทำไม `asyncio.gather()` จึงควบคุมไฟหลายดวงได้เร็วกว่าการ `await` ทีละดวงค่ะ

---

## 1. ภาพรวม Week 4 Light Lab

ระบบนี้จำลองห้องปฏิบัติการที่มีไฟ 4 ดวง แต่ละดวงมีเวลาในการตอบสนองไม่เท่ากัน

ใบไม่ได้ต่อกับหลอดไฟจริง โปรแกรมของใบจะส่ง HTTP request ไปยัง Server ของอาจารย์ แล้ว Server จะ:

1. รับคำสั่งจาก Python
2. รอตาม Hardware Delay ของไฟดวงนั้น
3. เปลี่ยนสถานะเป็น `ON` หรือ `OFF`
4. ส่ง JSON response กลับมา
5. Broadcast สถานะใหม่ผ่าน WebSocket
6. Dashboard ของใบเปลี่ยนแบบ real-time

ภาพรวม:

```text
Python ของใบ
    |
    | GET / POST / DELETE ผ่าน HTTPX
    v
Server ของอาจารย์
    |
    | จำลอง Hardware Delay
    | เปลี่ยนสถานะไฟ
    v
WebSocket Broadcast
    |
    v
Dashboard ของใบอัปเดตทันที
```

---

## 2. ไฟทั้ง 4 ดวง

| Light ID | ชื่อ | Hardware Delay |
|---|---|---:|
| `light_1` | ไฟหน้าประตู (Light 1) | 0.5 วินาที |
| `light_2` | ไฟโต๊ะปฏิบัติการ A (Light 2) | 1.2 วินาที |
| `light_3` | ไฟโต๊ะปฏิบัติการ B (Light 3) | 2.0 วินาที |
| `light_4` | ไฟกระดานหน้าห้อง (Light 4) | 0.8 วินาที |

เรียงจากเร็วที่สุดไปช้าที่สุด:

```text
light_1 = 0.5s
light_4 = 0.8s
light_2 = 1.2s
light_3 = 2.0s
```

ค่า delay นี้เป็นหัวใจของ Lab เพราะทำให้เราเห็นความต่างระหว่าง:

- ทำงานแบบ Sequential
- ทำงานแบบ Concurrent ด้วย `asyncio.gather()`

---

## 3. คำศัพท์ที่ต้องรู้

| คำ | ความหมายง่าย ๆ | ใน Lab นี้ |
|---|---|---|
| Client | โปรแกรมที่ส่งคำขอ | Python ของใบ |
| Server | โปรแกรมที่รับคำขอและส่งผลกลับ | Server `172.16.2.117:8088` |
| REST API | ช่องทาง HTTP ที่ Client ใช้สั่ง Server | GET, POST, DELETE |
| Endpoint | Method และ URL ที่ใช้เรียกงานหนึ่งอย่าง | `POST /api/.../lights/light_1` |
| Request | ข้อมูลที่ Client ส่งไป | JSON `{"status": "ON"}` |
| Response | ข้อมูลที่ Server ตอบกลับ | JSON สถานะปัจจุบัน |
| JSON | รูปแบบข้อมูล key-value | `{"light_id": "light_1"}` |
| Latency | เวลาหน่วงก่อน Server ตอบ | `light_3` ใช้ 2.0 วินาที |
| Coroutine | งานที่ประกาศด้วย `async def` | `set_light()` |
| Task | Coroutine ที่ Event Loop รับไปจัดการ | งานจาก `asyncio.gather()` |
| Event Loop | ตัวสลับและจัดคิวงาน async | เริ่มด้วย `asyncio.run()` |
| Sequential | ทำทีละงานและรอทีละงาน | `light_01.py` |
| Concurrent | หลายงานคืบหน้าในช่วงเวลาเดียวกัน | `light_02.py` |
| WebSocket | Connection ที่ Server push ข้อมูลมาได้ | Dashboard รับสถานะใหม่ทันที |
| Timeout | เวลารอสูงสุด | HTTPX timeout |

---

## 4. URL ที่ใช้จริง

README ยกตัวอย่าง Local Server ว่า:

```text
HTTP:      http://127.0.0.1:8000
WebSocket: ws://127.0.0.1:8000
```

แต่ Server ห้องเรียนที่ใบกำลังใช้จริงคือ:

```text
HTTP:      http://172.16.2.117:8088
WebSocket: ws://172.16.2.117:8088
```

Dashboard ของใบ:

```text
http://172.16.2.117:8088/6710301033
```

ข้อควรจำ:

- `127.0.0.1` หมายถึงเครื่องของตัวเอง
- `172.16.2.117` หมายถึงเครื่อง Server ในเครือข่ายห้องเรียน
- `8088` คือ port ที่ Server เปิดรับ request
- `6710301033` ทำให้สถานะไฟของใบแยกจากนักศึกษาคนอื่น

---

# Part A — REST API

## 5. อ่านสถานะไฟทั้งหมดด้วย GET

Endpoint:

```text
GET /api/{student_id}/lights
```

ของใบ:

```text
GET http://172.16.2.117:8088/api/6710301033/lights
```

Server จะตอบข้อมูลไฟทั้ง 4 ดวง:

```json
{
  "light_1": {
    "name": "ไฟหน้าประตู (Light 1)",
    "status": "OFF",
    "delay": 0.5
  },
  "light_2": {
    "name": "ไฟโต๊ะปฏิบัติการ A (Light 2)",
    "status": "OFF",
    "delay": 1.2
  },
  "light_3": {
    "name": "ไฟโต๊ะปฏิบัติการ B (Light 3)",
    "status": "OFF",
    "delay": 2.0
  },
  "light_4": {
    "name": "ไฟกระดานหน้าห้อง (Light 4)",
    "status": "OFF",
    "delay": 0.8
  }
}
```

`GET` ใช้สำหรับอ่านข้อมูล ไม่ควรเปลี่ยนสถานะไฟ

---

## 6. เปิดหรือปิดไฟด้วย POST

Endpoint:

```text
POST /api/{student_id}/lights/{light_id}
```

ตัวอย่างเปิด `light_1`:

```text
POST http://172.16.2.117:8088/api/6710301033/lights/light_1
```

JSON body:

```json
{
  "status": "ON"
}
```

ถ้าจะปิด:

```json
{
  "status": "OFF"
}
```

Response สำเร็จ:

```json
{
  "student_id": "6710301033",
  "light_id": "light_1",
  "current_status": "ON"
}
```

Server จะตอบหลังจากรอ Hardware Delay ของไฟดวงนั้นเสร็จแล้ว

---

## 7. รีเซ็ตไฟทั้งหมดด้วย DELETE

Endpoint:

```text
DELETE /api/{student_id}/lights/reset
```

ของใบ:

```text
DELETE http://172.16.2.117:8088/api/6710301033/lights/reset
```

คำสั่งนี้ทำให้ไฟทั้ง 4 ดวงกลับเป็น `OFF`

เหตุผลที่ควร reset ก่อนทดสอบ:

- ทำให้ทุกการทดลองเริ่มจากสถานะเดียวกัน
- ผลจากรอบก่อนไม่รบกวนรอบใหม่
- ดู Dashboard แล้วเข้าใจง่าย

เหตุผลที่ควร reset หลังทดสอบ:

- ไม่ทิ้งสถานะไฟของใบค้างไว้
- พร้อมเริ่มการทดลองรอบถัดไป

---

## 8. Error จาก API ที่ต้องรู้

| HTTP Status | ความหมาย | ตัวอย่างสาเหตุ |
|---:|---|---|
| `200` | สำเร็จ | เปิดไฟได้ |
| `400` | ค่าที่ส่งไม่ถูกต้อง | ส่ง `OPEN` แทน `ON` |
| `404` | ไม่พบ resource | ใช้ `light_5` |
| `422` | JSON ไม่ตรงรูปแบบ | ไม่ส่ง field `status` |

ตัวอย่าง 404:

```json
{
  "detail": "ไม่พบหลอดไฟที่ระบุ"
}
```

ตัวอย่าง 400:

```json
{
  "detail": "สถานะต้องเป็น ON หรือ OFF เท่านั้น"
}
```

---

# Part B — Python และ HTTPX

## 9. ทำไมใช้ `httpx.AsyncClient`

`httpx` เป็น library สำหรับส่ง HTTP request จาก Python

แบบ async ใช้:

```python
async with httpx.AsyncClient(...) as client:
    response = await client.get(...)
```

ข้อดี:

- รองรับ `await`
- ระหว่างรอ network Event Loop ไปจัดการงานอื่นได้
- ใช้กับ `asyncio.gather()` ได้
- เหมาะกับการส่งหลาย request พร้อมกัน

`async with` ช่วยเปิดและปิด connection อย่างถูกต้อง

---

## 10. `async def` และ `await`

ประกาศ coroutine function:

```python
async def get_all_lights(client):
    ...
```

รอ HTTP response:

```python
response = await client.get(url)
```

`await` ไม่ได้หมายถึงหยุดโปรแกรมทั้งหมด แต่หมายถึง:

```text
งานนี้กำลังรอ I/O
Event Loop สามารถไปดูงาน async อื่นก่อนได้
```

ถ้ามีงานเดียว ผลอาจดูเหมือนการรอปกติ แต่ถ้ามีหลายงาน `await` ทำให้เกิด concurrency ได้

---

## 11. `asyncio.run(main())`

ไฟล์ async ต้องมีจุดเริ่ม Event Loop:

```python
if __name__ == "__main__":
    asyncio.run(main())
```

ลำดับคือ:

```text
Python เริ่มไฟล์
    |
    v
asyncio.run(main())
    |
    v
เปิด Event Loop
    |
    v
รัน main coroutine
    |
    v
ปิด Event Loop เมื่อจบ
```

ถ้าเรียก `main()` ตรง ๆ โดยไม่ await หรือ `asyncio.run()` จะได้ coroutine object แต่โค้ดข้างในยังไม่ทำงานจริง

---

## 12. `light_utils.py` มีหน้าที่อะไร

ไฟล์นี้รวม logic ที่ใช้ซ้ำ เพื่อไม่ต้องเขียน URL และ HTTP request ซ้ำใน `light_01.py` กับ `light_02.py`

ค่าหลัก:

```python
BASE_URL = "http://172.16.2.117:8088"
STUDENT_ID = "6710301033"
LIGHT_IDS = ("light_1", "light_2", "light_3", "light_4")
```

ฟังก์ชันหลัก:

| Function | Method | หน้าที่ |
|---|---|---|
| `get_all_lights()` | GET | อ่านไฟทั้งหมด |
| `set_light()` | POST | เปิดหรือปิดไฟหนึ่งดวง |
| `reset_all_lights()` | DELETE | รีเซ็ตทุกดวงเป็น OFF |

### ทำไมส่ง `client` เข้า function

แทนที่จะสร้าง HTTP client ใหม่ทุก request เราใช้ client เดิม:

```python
async with httpx.AsyncClient(base_url=BASE_URL) as client:
    await get_all_lights(client)
    await set_light(client, "light_1", "ON")
```

ข้อดี:

- reuse connection
- ลด overhead
- ทดสอบง่ายด้วย MockTransport
- แยกหน้าที่ชัดเจน

### Validation

`set_light()` ควรรับเฉพาะ:

```text
light_1, light_2, light_3, light_4
ON, OFF
```

ถ้าส่ง `off` ตัวเล็ก โปรแกรมสามารถ normalize เป็น `OFF` ก่อนส่ง

---

# Part C — ไฟล์ Lab

## 13. `light_01.py` — Sequential REST Flow

ไฟล์นี้สอนการควบคุมไฟแบบ **Sequential** หรือทำทีละดวง

Flow:

```text
Reset ไฟทั้งหมดเป็น OFF
        |
        v
GET สถานะเริ่มต้น
        |
        v
POST เปิด light_1 -> รอ 0.5s
        |
        v
POST เปิด light_2 -> รอ 1.2s
        |
        v
POST เปิด light_3 -> รอ 2.0s
        |
        v
POST เปิด light_4 -> รอ 0.8s
        |
        v
GET สถานะสุดท้าย
        |
        v
Reset กลับเป็น OFF
```

หัวใจของโค้ด:

```python
for light_id in LIGHT_IDS:
    result = await set_light(client, light_id, "ON")
```

จุดสำคัญคือ loop จะรอแต่ละ request ให้เสร็จก่อนเริ่มตัวถัดไป

### เวลาที่คาด

```text
light_1  0.5s
light_2  1.2s
light_3  2.0s
light_4  0.8s
----------------
รวม      4.5s
```

เวลาจริงอาจมากกว่า 4.5 วินาทีเล็กน้อยเพราะ:

- Network overhead
- HTTP processing
- Python runtime
- Server load

### สิ่งที่ควรเห็นบน Dashboard

```text
light_1 เปิดก่อน
จากนั้น light_2
จากนั้น light_3
จากนั้น light_4
```

ไฟจะไม่ได้เปลี่ยนเป็น ON พร้อมกันค่ะ

---

## 14. `light_02.py` — Concurrent ด้วย `asyncio.gather()`

ไฟล์นี้สอนการเปิดไฟทั้ง 4 ดวงแบบ Concurrent

Flow:

```text
Reset ไฟทั้งหมดเป็น OFF
        |
        v
GET สถานะเริ่มต้น
        |
        v
สร้างคำสั่ง POST ทั้ง 4 ดวง
        |
        v
asyncio.gather()
        |
        ├── light_1 รอ 0.5s
        ├── light_2 รอ 1.2s
        ├── light_3 รอ 2.0s
        └── light_4 รอ 0.8s
        |
        v
รอจนทุกดวงเสร็จ
        |
        v
GET สถานะสุดท้าย
        |
        v
Reset กลับเป็น OFF
```

หัวใจของโค้ด:

```python
results = await asyncio.gather(
    *(set_light(client, light_id, "ON") for light_id in LIGHT_IDS)
)
```

### `*` ทำอะไร

ส่วนนี้สร้างงานหลายตัว:

```python
set_light(client, "light_1", "ON")
set_light(client, "light_2", "ON")
set_light(client, "light_3", "ON")
set_light(client, "light_4", "ON")
```

เครื่องหมาย `*` แตก iterable ให้กลายเป็น argument หลายตัวของ `gather()`

### เวลาที่คาด

ทุก request เริ่มใกล้กัน เวลารวมจึงขึ้นกับไฟที่ช้าที่สุด:

```text
max(0.5, 1.2, 2.0, 0.8) = 2.0 วินาที
```

ไม่ใช่ผลรวม 4.5 วินาที

### ลำดับของ `results`

`gather()` คืนผลลัพธ์ตามลำดับ argument ที่ส่งเข้าไป:

```text
results[0] -> light_1
results[1] -> light_2
results[2] -> light_3
results[3] -> light_4
```

แม้ลำดับเวลาที่ Server ทำเสร็จจะเป็น:

```text
light_1 -> light_4 -> light_2 -> light_3
```

นี่เป็นคำถามที่มีโอกาสออกสอบค่ะ

---

## 15. เปรียบเทียบ Sequential กับ Concurrent

| เรื่อง | `light_01.py` | `light_02.py` |
|---|---|---|
| วิธี | await ทีละดวง | gather หลายดวง |
| เริ่ม request | ทีละ request | ใกล้เคียงพร้อมกัน |
| เวลาคาด | ~4.5s | ~2.0s |
| เหมาะกับ | งานที่ต้องเรียงลำดับ | งานอิสระต่อกัน |
| Output | ไฟเปิดทีละดวง | ไฟเสร็จตาม delay |
| ความง่าย | เข้าใจง่าย | ต้องเข้าใจ Task/gather |

ภาพจำ:

```text
Sequential:
light_1 ----> light_2 ----> light_3 ----> light_4

Concurrent:
light_1 ---->
light_2 -------->
light_3 ------------>
light_4 ------>
```

### ผลตรวจจริงจาก Server ห้องเรียน

ไอริสรันทั้งสองไฟล์กับ `http://172.16.2.117:8088` เมื่อวันที่ 15 กรกฎาคม 2026 ได้ผลดังนี้:

| ไฟล์ | เวลาที่วัดได้จริง | ผล |
|---|---:|---|
| `light_01.py` | 4.55 วินาที | เปิดครบ 4 ดวงแบบ sequential |
| `light_02.py` | 2.02 วินาที | เปิดครบ 4 ดวงด้วย `asyncio.gather()` |

หลังจบทั้งสองโปรแกรม ตรวจ GET endpoint แล้วไฟ `light_1`–`light_4` กลับเป็น `OFF` ครบทุกดวง แสดงว่า `finally` cleanup ทำงานสำเร็จในรอบทดสอบจริงค่ะ

---

## 16. ทำไม `asyncio` เหมาะกับงานนี้

งาน HTTP เป็น I/O-bound:

```text
Python ส่ง request
แล้วเวลาส่วนใหญ่รอ network และ Server
```

ระหว่างรอ Python ไม่จำเป็นต้องใช้ CPU คำนวณหนัก ดังนั้น Event Loop สามารถสลับไปดู request อื่นได้

`asyncio` เหมาะกับ:

- HTTP API
- Database
- File I/O แบบ async
- WebSocket
- Network connection
- งานที่มีช่วงรอจำนวนมาก

ไม่ใช่ตัวเลือกหลักสำหรับงาน CPU หนัก เช่นคำนวณภาพหรือ matrix ขนาดใหญ่ เพราะงานแบบนั้นอาจต้องใช้ multiprocessing หรือ GPU

---

# Part D — Safety และ Error Handling

## 17. ทำไมต้องใช้ `try/finally`

ถ้าโปรแกรมเกิด error กลางทาง เราไม่อยากให้ไฟค้างเป็น ON

รูปแบบ:

```python
try:
    # ทดลองเปิดไฟ
finally:
    # reset กลับ OFF เสมอ
```

`finally` จะถูกพยายามเรียกไม่ว่า:

- โปรแกรมสำเร็จ
- เกิด HTTP error
- เกิด exception ระหว่าง loop

ข้อควรรู้: ถ้า network ขาดในช่วง `finally` การ reset ก็อาจล้มเหลวได้ จึงต้องรายงาน error ตามจริง ไม่ควรอ้างว่า reset สำเร็จโดยไม่ได้รับ response

---

## 18. ทำไมไม่ควรจับ `Exception` กว้าง ๆ ใน Helper

แบบที่ไม่ดี:

```python
try:
    ...
except Exception:
    return {}
```

ปัญหา:

- กลบสาเหตุจริง
- Caller แยกไม่ได้ว่า HTTP 404, timeout หรือ code bug
- Dictionary ว่างอาจถูกเข้าใจผิดว่า response สำเร็จ

แนวทางที่ชัดกว่า:

```python
response.raise_for_status()
return response.json()
```

แล้วให้ระดับ CLI จับ `httpx.HTTPError` เพื่อแสดงข้อความแก่ผู้ใช้

---

## 19. ระวัง Cancel และ Timeout กับคำสั่ง POST

ถ้า Client cancel การรอ HTTP request ไม่ได้แปลว่า Server จะ rollback

ตัวอย่าง:

```text
Client ส่ง POST เปิด light_3
Server รับคำสั่งแล้ว
Client timeout ก่อน 2 วินาที
Server อาจทำงานต่อและเปิดไฟสำเร็จ
```

ดังนั้น:

```text
Client timeout != ยืนยันว่า Server ไม่เปลี่ยนสถานะ
```

วิธีตรวจที่ถูก:

1. รับมือ timeout
2. รอสักระยะถ้าจำเป็น
3. GET สถานะจาก Server อีกครั้ง
4. ใช้สถานะจาก Server เป็นความจริงล่าสุด

ด้วยเหตุนี้ Lab หลักจึงเน้น Sequential กับ `gather()` และไม่ใช้ `FIRST_COMPLETED` แล้ว cancel POST ที่เหลือค่ะ

---

# Part E — Testing

## 20. ทำไม Unit Test ห้ามยิง Server จริง

ถ้า test ยิง Server จริง:

- เปลี่ยนสถานะไฟของใบทุกครั้งที่รัน
- ผลขึ้นกับ Wi-Fi และ Server
- Server ปิดแล้ว test fail ทั้งที่ logic ถูก
- Test ช้าเพราะรอ Hardware Delay
- นักศึกษาคนอื่นหรือ network load อาจทำให้ผลแกว่ง

จึงใช้ `httpx.MockTransport` จำลอง Server ใน memory

Unit test จะตรวจว่า:

- ใช้ Method ถูกหรือไม่
- URL path ถูกหรือไม่
- JSON body ถูกหรือไม่
- normalize `on/off` ถูกหรือไม่
- reject Light ID ที่ไม่มีหรือไม่
- HTTP error ถูกส่งต่ออย่างชัดเจนหรือไม่

---

## 21. Unit Test กับ Live Test ต่างกันอย่างไร

| Test | ใช้อะไร | เปลี่ยน Server จริงไหม | ตรวจอะไร |
|---|---|---|---|
| Unit Test | MockTransport | ไม่ | Logic และ request contract |
| Live Test | Server อาจารย์ | ใช่ | Integration และ Dashboard |

ต้องมีทั้งสองแบบ:

```text
Unit Test ผ่าน
    -> โค้ดสร้าง request ถูก

Live Test ผ่าน
    -> โค้ดคุยกับระบบอาจารย์ได้จริง
```

---

# Part F — วิธีติดตั้งและรัน

## 22. ติดตั้ง HTTPX

จาก root project:

```bash
python -m pip install -r Week4/light/requirements.txt
```

ตรวจว่า import ได้:

```bash
python -c "import httpx; print(httpx.__version__)"
```

---

## 23. รัน Unit Tests

```bash
python -m unittest discover -s Week4/light/tests -v
```

Unit tests ไม่ควรเปลี่ยนไฟบน Dashboard

---

## 24. รัน Sequential Lab

เปิด Dashboard ก่อน:

```text
http://172.16.2.117:8088/6710301033
```

จากนั้นรัน:

```bash
python Week4/light/light_01.py
```

ให้สังเกต:

- ไฟเริ่มจาก OFF
- ไฟเปิดทีละดวง
- เวลาส่วนควบคุมประมาณ 4.5 วินาทีบวก overhead
- หลังจบโปรแกรม reset กลับ OFF

---

## 25. รัน Concurrent Lab

```bash
python Week4/light/light_02.py
```

ให้สังเกต:

- request ทั้ง 4 เริ่มใกล้กัน
- Dashboard เปลี่ยนตาม delay ของแต่ละไฟ
- เวลารวมประมาณ 2.0 วินาทีบวก overhead
- หลังจบ reset กลับ OFF

---

## 26. ตรวจ Syntax

```bash
python -m py_compile Week4/light/*.py
```

ถ้าไม่มีข้อความ error แปลว่า compile ผ่าน

หมายเหตุ: `py_compile` ตรวจ syntax แต่ไม่ได้ยืนยันว่า Server เชื่อมต่อได้หรือ logic runtime ถูกทั้งหมด

---

# Part G — Debug Checklist

## 27. ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ModuleNotFoundError: httpx` | ยังไม่ได้ติดตั้ง | ติดตั้งจาก requirements |
| `ConnectError` | Server ปิดหรืออยู่คนละ network | ตรวจ `172.16.2.117:8088` |
| `TimeoutException` | Network/Server ใช้เวลานาน | ตรวจ Server และ timeout |
| HTTP 404 | Light ID ผิด | ใช้ `light_1`–`light_4` |
| HTTP 400 | Status ผิด | ใช้ `ON` หรือ `OFF` |
| HTTP 422 | JSON body ผิด | ต้องมี key `status` |
| Dashboard ไม่เปลี่ยน | WebSocket ขาดหรือเปิดผิด Student ID | Refresh และตรวจ URL |
| เวลามากกว่า 4.5/2.0 | Network overhead หรือ Server load | ดูเป็นแนวโน้ม ไม่ยึดเลขตายตัว |
| ไฟค้าง ON หลัง error | reset ใน finally ไม่สำเร็จ | ใช้ปุ่ม reset หรือ DELETE endpoint |

---

## 28. เช็กทีละชั้นเมื่อโปรแกรมไม่ทำงาน

### ชั้น 1 — Server เปิดไหม

เปิด:

```text
http://172.16.2.117:8088/6710301033
```

### ชั้น 2 — GET ได้ไหม

เปิด:

```text
http://172.16.2.117:8088/api/6710301033/lights
```

### ชั้น 3 — Dependency พร้อมไหม

```bash
python -c "import httpx; print('httpx ready')"
```

### ชั้น 4 — Unit test ผ่านไหม

```bash
python -m unittest discover -s Week4/light/tests -v
```

### ชั้น 5 — Syntax ผ่านไหม

```bash
python -m py_compile Week4/light/*.py
```

### ชั้น 6 — Live script ทำงานไหม

```bash
python Week4/light/light_01.py
```

---

# Part H — คำถามแนวสอบ

## 29. คำถามและคำตอบสั้น

### 29.1 Client คืออะไร

โปรแกรมที่ส่ง request ไปยัง Server ใน Lab นี้คือ Python ของใบ

### 29.2 Server คืออะไร

โปรแกรมที่รับคำสั่ง ควบคุมสถานะไฟจำลอง และตอบ JSON กลับมา

### 29.3 GET ใช้ทำอะไร

อ่านสถานะไฟทั้งหมดโดยไม่ตั้งใจเปลี่ยน state

### 29.4 POST ใช้ทำอะไร

ส่งคำสั่งเปลี่ยนไฟหนึ่งดวงเป็น `ON` หรือ `OFF`

### 29.5 DELETE ใช้ทำอะไร

รีเซ็ตสถานะไฟทุกดวงเป็น `OFF`

### 29.6 `async def` คืออะไร

ประกาศ coroutine function ที่สามารถใช้ `await` ได้

### 29.7 `await` ทำอะไร

รอ awaitable และคืน control ให้ Event Loop ไปจัดการงานอื่นระหว่างรอ I/O

### 29.8 `asyncio.run()` ทำอะไร

เปิด Event Loop และรัน main coroutine จนเสร็จ

### 29.9 `asyncio.gather()` ทำอะไร

จัดการ awaitable หลายตัวพร้อมกันและรอให้ครบทั้งหมด

### 29.10 ทำไม Sequential ใช้ประมาณ 4.5 วินาที

เพราะรอ delay ทีละดวง จึงรวม `0.5 + 1.2 + 2.0 + 0.8`

### 29.11 ทำไม Concurrent ใช้ประมาณ 2.0 วินาที

เพราะทุก request คืบหน้าพร้อมกัน เวลารวมจึงใกล้ไฟที่ช้าที่สุดคือ `light_3` 2.0 วินาที

### 29.12 `gather()` คืนผลตามลำดับใด

ตามลำดับ argument ที่ส่งเข้าไป ไม่ใช่ลำดับที่งานเสร็จ

### 29.13 ทำไมใช้ `perf_counter()`

เหมาะกับการวัด elapsed time เพราะเป็น monotonic clock และมีความละเอียดดี

### 29.14 WebSocket ทำอะไร

ให้ Server push สถานะใหม่มาที่ Dashboard ทันทีโดยไม่ต้อง refresh หรือ polling ซ้ำ

### 29.15 ใบต้องเขียน WebSocket Client เองไหม

ไม่จำเป็นใน Lab หลัก เพราะ README ระบุว่า WebSocket channel มีไว้ให้ Dashboard frontend และ Dashboard มีอยู่แล้ว

### 29.16 ทำไมต้อง reuse `AsyncClient`

ลด overhead ของการเปิด connection ใหม่ทุก request และทำให้ test/โค้ดอ่านง่ายขึ้น

### 29.17 `response.raise_for_status()` ทำอะไร

ทำให้ HTTP response ที่เป็น error เช่น 400 หรือ 404 กลายเป็น exception แทนการถูกเข้าใจว่า success

### 29.18 Timeout แปลว่า Server ไม่ทำงานต่อใช่ไหม

ไม่เสมอ Client อาจเลิกรอ แต่ Server อาจได้รับคำสั่งและทำต่อ จึงต้อง GET ตรวจสถานะจริง

### 29.19 Unit test ทำไมใช้ MockTransport

เพื่อทดสอบ request contract โดยไม่เปลี่ยนสถานะ Server จริงและไม่ขึ้นกับ network

### 29.20 Sequential เหมาะเมื่อไร

เมื่องานต้องทำตามลำดับ หรืองานถัดไปต้องใช้ผลจากงานก่อนหน้า

### 29.21 Concurrent เหมาะเมื่อไร

เมื่องานเป็นอิสระต่อกันและมีช่วงรอ I/O เช่น request ของไฟคนละดวง

---

# Part I — Mini Exercises

## 30. ทำนายเวลาก่อนรัน

ถ้า delay เปลี่ยนเป็น:

```text
light_1 = 1.0s
light_2 = 2.0s
light_3 = 3.0s
light_4 = 4.0s
```

Sequential:

```text
1 + 2 + 3 + 4 = 10 วินาที
```

Concurrent:

```text
max(1, 2, 3, 4) = 4 วินาที
```

---

## 31. ถ้าเอา `await` ออกจาก `set_light()`

อาจได้ coroutine object แทน response และ request ไม่ถูกดำเนินการในจุดที่คาด

จำว่า:

```text
เรียก async function -> ได้ coroutine
await coroutine      -> รันและรับผล
create_task(coro)    -> ส่ง coroutine เข้า Event Loop เป็น Task
```

---

## 32. ถ้าใช้ `time.sleep()` ใน async code

`time.sleep()` block thread และ Event Loop ทำให้ Task อื่นสลับมาทำงานไม่ได้

สำหรับการรอแบบ async ใช้:

```python
await asyncio.sleep(...)
```

แต่ใน Lab นี้ Hardware Delay อยู่ที่ Server Client จึงรอผ่าน `await client.post(...)` อยู่แล้ว

---

# Part J — Checklist ก่อนสอบ

## 33. Concept checklist

- [ ] อธิบาย Client กับ Server ได้
- [ ] รู้ว่า Student ID แยก state ของแต่ละคน
- [ ] รู้หน้าที่ GET, POST และ DELETE
- [ ] อธิบาย JSON request/response ได้
- [ ] อธิบาย `async def` และ `await` ได้
- [ ] อธิบาย Event Loop ได้
- [ ] อธิบาย `asyncio.gather()` ได้
- [ ] คำนวณ Sequential 4.5 วินาทีได้
- [ ] อธิบาย Concurrent ประมาณ 2.0 วินาทีได้
- [ ] รู้ว่า gather return ตาม input order
- [ ] รู้หน้าที่ WebSocket Dashboard
- [ ] รู้ว่า timeout ไม่รับประกัน rollback
- [ ] รู้ว่าทำไม test ไม่ยิง Server จริง

## 34. Practical checklist

- [ ] เปิด Dashboard ได้
- [ ] เปิด GET endpoint ได้
- [ ] ติดตั้ง HTTPX แล้ว
- [ ] รัน Unit Tests ผ่าน
- [ ] รัน `light_01.py` ได้
- [ ] รัน `light_02.py` ได้
- [ ] เห็น Dashboard อัปเดต
- [ ] หลังจบไฟกลับ OFF
- [ ] ตรวจ syntax ผ่าน

---

# Part K — Cheat Sheet

## 35. คำสั่งจำง่าย

```text
GET    = อ่านสถานะ
POST   = เปลี่ยนไฟหนึ่งดวง
DELETE = รีเซ็ตทุกดวง
```

```text
async def           = สร้าง coroutine function
await               = รอแบบให้ Event Loop สลับงานได้
asyncio.run(main()) = เปิด Event Loop
asyncio.gather(...) = รอหลายงานพร้อมกัน
```

```text
Sequential time = ผลรวมของ delay
Concurrent time = ใกล้ delay ที่มากที่สุด
```

```text
0.5 + 1.2 + 2.0 + 0.8 = 4.5s
max(0.5, 1.2, 2.0, 0.8) = 2.0s
```

## 36. URL จำง่าย

```text
Dashboard:
http://172.16.2.117:8088/6710301033

GET status:
http://172.16.2.117:8088/api/6710301033/lights

POST light:
http://172.16.2.117:8088/api/6710301033/lights/light_1

DELETE reset:
http://172.16.2.117:8088/api/6710301033/lights/reset

WebSocket:
ws://172.16.2.117:8088/ws/6710301033
```

## 37. คำสั่งรัน

```bash
python -m pip install -r Week4/light/requirements.txt
python -m unittest discover -s Week4/light/tests -v
python Week4/light/light_01.py
python Week4/light/light_02.py
python -m py_compile Week4/light/*.py
```

---

## 38. สรุปสุดท้าย

จำ 5 ข้อนี้ให้ได้:

1. Python ของใบเป็น Client ที่ส่ง HTTP request ไปยัง Server
2. `GET` อ่านสถานะ, `POST` เปิด/ปิดไฟ, `DELETE` รีเซ็ต
3. `light_01.py` รอทีละดวง จึงใช้เวลาประมาณ 4.5 วินาที
4. `light_02.py` ใช้ `asyncio.gather()` จึงใช้เวลาประมาณ 2.0 วินาที
5. Dashboard รับ WebSocket broadcast และเปลี่ยน real-time

ประโยคสรุปสำหรับตอบอาจารย์:

> งานนี้ใช้ `httpx.AsyncClient` ส่ง REST API requests ไปควบคุมไฟจำลอง 4 ดวง โดยเปรียบเทียบการ await ทีละ request กับการรันพร้อมกันผ่าน `asyncio.gather()` แบบ sequential ใช้เวลารวมของทุก delay ประมาณ 4.5 วินาที ส่วน concurrent ใช้เวลาใกล้กับงานที่ช้าที่สุดประมาณ 2.0 วินาที และ Dashboard รับสถานะใหม่แบบ real-time ผ่าน WebSocket ค่ะ
