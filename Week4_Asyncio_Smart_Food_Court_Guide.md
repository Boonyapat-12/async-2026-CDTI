# Week 4 Asyncio Smart Food Court Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงล่าสุด** ในโฟลเดอร์ `Week4` ของใบค่ะ เหมาะสำหรับอ่านตั้งแต่ยังไม่รู้พื้นฐาน และใช้ทบทวนก่อนสอบเรื่อง `asyncio`, HTTP API, timeout และการจัดการหลาย Task

ไฟล์ที่ใช้เรียนมี 7 ไฟล์:

- `Week4/foodcourt_api.py`
- `Week4/food_utils.py`
- `Week4/foodcourt_01_create_task.py`
- `Week4/foodcourt_02_gather.py`
- `Week4/foodcourt_03_wait_first.py`
- `Week4/foodcourt_04_wait_for.py`
- `Week4/foodcourt_05_mix_concepts.py`

> เป้าหมาย: อ่านจบแล้วอธิบายได้ว่า Client ส่งออเดอร์ไปยัง API อย่างไร, `create_task()`, `gather()`, `wait()` และ `wait_for()` ต่างกันอย่างไร รวมถึงเลือกใช้ให้เหมาะกับโจทย์ได้ค่ะ

---

## 1. Week 4 กำลังเรียนเรื่องอะไร

Week 2 สอนพื้นฐานการสร้างงาน async และ Week 3 สอนการควบคุม Task ส่วน Week 4 นำแนวคิดเหล่านั้นมาใช้กับ **HTTP API จริง**

ระบบจำลองศูนย์อาหารมีองค์ประกอบหลัก 2 ฝั่ง:

1. **Client** — โปรแกรมของนักศึกษาที่ส่งออเดอร์
2. **Server** — FastAPI ที่รับออเดอร์และจำลองเวลาทำอาหาร

ภาพรวมการทำงาน:

```text
foodcourt_01 ถึง foodcourt_05
            |
            | เรียก send_order_to_kitchen(...)
            v
       food_utils.py
            |
            | HTTP POST + JSON
            v
      foodcourt_api.py
            |
            | await asyncio.sleep(cooking_time)
            v
        ส่ง JSON กลับ
```

สิ่งใหม่ที่สำคัญใน Week 4:

- ส่ง HTTP request แบบ async ด้วย `httpx.AsyncClient`
- สร้าง API server ด้วย FastAPI
- ส่งข้อมูลในรูป JSON
- ส่งหลายออเดอร์พร้อมกัน
- รอทุกออเดอร์ หรือรอเฉพาะจานแรก
- กำหนด timeout ให้คำสั่งซื้อ
- ยกเลิก Task ที่ไม่ต้องการแล้ว

---

## 2. คำศัพท์พื้นฐาน

| คำ | ความหมายแบบง่าย | ตัวอย่างใน Week 4 |
|---|---|---|
| Client | ฝั่งที่ส่งคำขอ | `foodcourt_01`–`foodcourt_05` |
| Server | ฝั่งที่รับและประมวลผลคำขอ | `foodcourt_api.py` |
| API | ช่องทางที่โปรแกรมใช้คุยกัน | `POST /order/{shop_name}` |
| Endpoint | Method + path ที่เปิดให้เรียก | `POST /order/steak` |
| HTTP `POST` | request ที่ใช้ส่งข้อมูลไปให้ server | ส่งรหัสนักศึกษาและชื่อเมนู |
| Request | ข้อมูลที่ client ส่งไป | URL และ JSON payload |
| Response | ข้อมูลที่ server ตอบกลับ | JSON สถานะ `READY_FOR_PICKUP` |
| JSON | รูปแบบข้อมูล key-value | `{"student_id": "..."}` |
| Latency | เวลาหน่วงก่อนตอบกลับ | ร้าน steak ใช้ 4.0 วินาที |
| Coroutine | งานที่ประกาศด้วย `async def` | `send_order_to_kitchen()` |
| Task | Coroutine ที่ถูกส่งเข้า event loop แล้ว | ผลจาก `asyncio.create_task()` |
| Event loop | ตัวจัดคิวและสลับงาน async | เริ่มด้วย `asyncio.run(main())` |
| Timeout | เวลารอสูงสุด | `timeout=2.0` |
| Pending | Task ที่ยังไม่เสร็จ | ร้าน noodle/steak ตอนข้าวมันไก่เสร็จก่อน |
| Cancel | ส่งสัญญาณยกเลิก Task | `task.cancel()` |

---

## 3. ข้อมูลร้านและเวลาทำอาหาร

ค่าจริงมาจาก `KITCHEN_LATENCY` ใน `foodcourt_api.py`:

| `shop_name` | เมนูตัวอย่าง | เวลาจำลอง | ลำดับความเร็ว |
|---|---|---:|---|
| `hainanese_chicken` | ข้าวมันไก่ | 0.8 วินาที | เร็วที่สุด |
| `noodle` | ก๋วยเตี๋ยว | 1.5 วินาที | ปานกลาง |
| `steak` | สเต็ก | 4.0 วินาที | ช้าที่สุด |

เวลานี้สำคัญมาก เพราะใช้ทำนายผลของทุก Task ได้:

```text
0.8 วินาที < 1.5 วินาที < 4.0 วินาที
ข้าวมันไก่      ก๋วยเตี๋ยว       สเต็ก
```

---

## 4. สถาปัตยกรรม Client–Server

### 4.1 ฝั่ง Client

ไฟล์ `foodcourt_01`–`foodcourt_05` ไม่ได้ทำอาหารเอง แต่เรียก:

```python
send_order_to_kitchen(student_id, shop_name, menu_name)
```

ฟังก์ชันนี้อยู่ใน `food_utils.py` และเป็นผู้ส่ง HTTP request

### 4.2 ฝั่ง Server

`foodcourt_api.py` รับ request ที่ endpoint:

```text
POST /order/{shop_name}
```

ตัวอย่าง:

```text
POST /order/hainanese_chicken
POST /order/noodle
POST /order/steak
```

### 4.3 ข้อมูลที่ส่ง

Client ส่ง JSON body รูปแบบนี้:

```json
{
  "student_id": "6710301033",
  "menu_name": "Sizzling Steak"
}
```

### 4.4 ข้อมูลที่ได้รับกลับ

เมื่อทำอาหารเสร็จ Server ตอบ JSON ประมาณนี้:

```json
{
  "status": "READY_FOR_PICKUP",
  "student_id": "6710301033",
  "shop": "steak",
  "menu": "Sizzling Steak",
  "cooking_seconds": 4.0,
  "timestamp": "Wed Jul 15 10:00:04 2026"
}
```

Timestamp และเวลาจริงจะเปลี่ยนไปในแต่ละรอบค่ะ

---

# Part A — Infrastructure Files

## 5. `foodcourt_api.py` — FastAPI Kitchen Server

### 5.1 หน้าที่ของไฟล์

ไฟล์นี้สร้าง API server ที่จำลองครัวของศูนย์อาหาร

```python
app = FastAPI(title="🍳 Smart Food Court API")
```

`app` คือ FastAPI application ที่ Uvicorn จะนำไปรันเป็น web server

### 5.2 `OrderModel`

```python
class OrderModel(BaseModel):
    student_id: str
    menu_name: str
```

Pydantic `BaseModel` ใช้กำหนดรูปแบบ JSON ที่ server ยอมรับ

| Field | Type | หน้าที่ |
|---|---|---|
| `student_id` | `str` | รหัสผู้สั่ง |
| `menu_name` | `str` | ชื่ออาหาร |

ถ้าส่ง JSON ขาด field หรือ type ไม่ถูก FastAPI จะตอบ validation error โดยอัตโนมัติ

### 5.3 `KITCHEN_LATENCY`

```python
KITCHEN_LATENCY = {
    "hainanese_chicken": 0.8,
    "noodle": 1.5,
    "steak": 4.0
}
```

Dictionary นี้เก็บเวลาทำอาหารของแต่ละร้าน โดยใช้ชื่อร้านเป็น key

### 5.4 Endpoint `cook_food()`

```python
@app.post("/order/{shop_name}")
async def cook_food(shop_name: str, order: OrderModel):
```

ข้อมูลมาจาก 2 จุด:

| Parameter | มาจากไหน | ตัวอย่าง |
|---|---|---|
| `shop_name` | URL path | `steak` จาก `/order/steak` |
| `order` | JSON request body | `student_id` และ `menu_name` |

### 5.5 ตรวจชื่อร้าน

```python
if shop_name not in KITCHEN_LATENCY:
    raise HTTPException(status_code=404, detail="Shop not found")
```

ถ้าเรียกชื่อร้านที่ไม่มี เช่น `/order/pizza` จะได้ HTTP 404

### 5.6 จำลองการทำอาหาร

```python
cooking_time = KITCHEN_LATENCY[shop_name]
await asyncio.sleep(cooking_time)
```

ต้องใช้ `await asyncio.sleep()` เพราะ endpoint เป็น async ถ้าใช้ `time.sleep()` จะ block event loop และทำให้ request อื่นรอไปด้วย

### 5.7 Response

Server คืน Python dictionary และ FastAPI จะแปลงเป็น JSON ให้โดยอัตโนมัติ

```python
return {
    "status": "READY_FOR_PICKUP",
    "student_id": order.student_id,
    "shop": shop_name,
    "menu": order.menu_name,
    "cooking_seconds": cooking_time,
    "timestamp": ctime()
}
```

### 5.8 วิธีเปิด Server

เปิด Terminal ที่โฟลเดอร์ `Week4` แล้วรัน:

```bash
uvicorn foodcourt_api:app --port 8088
```

ความหมาย:

| ส่วน | ความหมาย |
|---|---|
| `foodcourt_api` | ชื่อไฟล์โดยไม่ใส่ `.py` |
| `app` | ตัวแปร FastAPI ในไฟล์ |
| `--port 8088` | เปิด server ที่ port 8088 |

API docs ของ FastAPI:

```text
http://127.0.0.1:8088/docs
```

> ต้องเปิด server ค้างไว้ใน Terminal หนึ่งหน้าต่าง แล้วจึงเปิดอีก Terminal เพื่อรัน client ค่ะ

---

## 6. `food_utils.py` — HTTP Client Helper

### 6.1 หน้าที่ของไฟล์

ไฟล์นี้รวม logic การส่งออเดอร์ไว้ใน function เดียว เพื่อไม่ให้ Task 1–5 ต้องเขียน HTTP code ซ้ำกัน

```python
async def send_order_to_kitchen(
    student_id: str,
    shop_name: str,
    menu_name: str
) -> dict:
```

### 6.2 Parameter

| Parameter | ตัวอย่าง | ความหมาย |
|---|---|---|
| `student_id` | `"6710301033"` | รหัสนักศึกษา |
| `shop_name` | `"steak"` | ชื่อร้านที่ใช้ใน URL |
| `menu_name` | `"Sizzling Steak"` | ชื่อเมนูที่ส่งใน JSON |

### 6.3 สร้าง URL

โค้ดปัจจุบันใช้:

```python
url = f"http://172.16.2.117:8088/order/{shop_name}"
```

ถ้า `shop_name` เป็น `steak` URL จะกลายเป็น:

```text
http://172.16.2.117:8088/order/steak
```

### 6.4 สร้าง JSON payload

```python
payload = {
    "student_id": student_id,
    "menu_name": menu_name
}
```

`shop_name` ไม่ได้อยู่ใน JSON เพราะถูกใส่อยู่ใน URL path แล้ว

### 6.5 ส่ง HTTP POST

```python
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=payload, timeout=10.0)
```

| ส่วน | ความหมาย |
|---|---|
| `AsyncClient()` | HTTP client ที่ทำงานแบบ async |
| `async with` | เปิด client และปิด connection ให้เมื่อจบ |
| `await client.post(...)` | ส่ง request แล้วรอ response โดยไม่ block event loop |
| `json=payload` | แปลง dictionary เป็น JSON body |
| `timeout=10.0` | HTTP request รอได้สูงสุด 10 วินาที |

### 6.6 ตรวจ HTTP status

ถ้า status เป็น `200`:

```python
return response.json()
```

ถ้าเป็น status อื่น:

```python
return {
    "status": "ERROR",
    "detail": f"HTTP Error {response.status_code}"
}
```

ถ้าเชื่อมต่อไม่ได้หรือเกิด exception:

```python
return {
    "status": "ERROR",
    "detail": f"Connection failed: {e}"
}
```

จุดสำคัญคือ function นี้ **จับ exception แล้ว return dictionary** แทนการโยน error ออกไป ดังนั้นบาง Task อาจยังทำงานต่อ แต่ผลลัพธ์จะไม่มี key `shop` หรือ `menu`

---

## 7. เรื่อง IP ที่ต้องเข้าใจก่อนรัน

ในไฟล์ปัจจุบันมี URL สองแบบ:

| ตำแหน่ง | URL | ความหมาย |
|---|---|---|
| `Week4/Readme.md` | `http://127.0.0.1:8088` | Server ในเครื่องตัวเอง |
| `food_utils.py` | `http://172.16.2.117:8088` | Server ในเครือข่ายห้องเรียน/เครื่องอื่น |

ดังนั้น แม้ใบเปิด `foodcourt_api.py` ในเครื่องตัวเอง แต่ Client ปัจจุบันก็ยังส่งไป `172.16.2.117` ไม่ใช่ local server

### ถ้าเรียนในเครือข่ายที่เข้าถึง Server อาจารย์ได้

ใช้ URL `172.16.2.117` ตามโค้ดปัจจุบัน

### ถ้าทดลองด้วย Server ในเครื่องตัวเอง

ต้องตั้ง URL ใน `food_utils.py` เป็น:

```python
url = f"http://127.0.0.1:8088/order/{shop_name}"
```

อย่าเปลี่ยน URL ก่อนส่งงานโดยไม่เช็ก requirement ของอาจารย์ เพราะ IP อาจเป็นส่วนหนึ่งของโจทย์ค่ะ

---

# Part B — Task Files

## 8. Task 1 — `foodcourt_01_create_task.py`

### 8.1 เป้าหมาย

ฝึกสร้าง Task ด้วย `asyncio.create_task()` ตรวจสถานะทันที และรอผลภายหลัง

### 8.2 Flow

```text
สร้าง coroutine ส่งออเดอร์ข้าวมันไก่
          |
          v
create_task() ส่งงานเข้า event loop
          |
          v
เช็ก .done() ทันที -> ปกติเป็น False
          |
          v
await food_task
          |
          v
รับ response จากครัว
```

### 8.3 สร้าง Task

```python
food_task = asyncio.create_task(
    send_order_to_kitchen(
        MY_STUDENT_ID,
        "hainanese_chicken",
        "Chicken Rice Mixed"
    )
)
```

ก่อนใช้ `create_task()` สิ่งที่ได้จาก `send_order_to_kitchen(...)` เป็น coroutine ส่วนหลังสร้างแล้ว `food_task` เป็น Task object

### 8.4 ตรวจ `.done()`

```python
food_task.done()
```

ค่าที่เป็นไปได้:

- `False` — งานยังทำไม่เสร็จ
- `True` — งานเสร็จ, error หรือถูก cancel แล้ว

เมื่อเช็กทันทีหลังสร้าง Task โดยทั่วไปจะได้ `False` เพราะ HTTP request ยังไม่เสร็จ

### 8.5 รอและรับผล

```python
result = await food_task
```

`await` ทำ 2 หน้าที่:

1. รอ Task ให้เสร็จ
2. รับค่าที่ coroutine `return` กลับมา

### 8.6 Expected behavior

ถ้า server เชื่อมต่อได้:

```text
--- [Task 1] Practice using create_task to queue an order ---
Checking task status immediately: Is it done? = False
System Response: {'status': 'READY_FOR_PICKUP', ...}
```

Timestamp และรายละเอียด dictionary จะเปลี่ยนตาม request จริง

### 8.7 Lab ย่อย

1. ลอง print `food_task.get_name()`
2. ลองตั้งชื่อ Task ด้วย `name="Chicken-Order"`
3. เปลี่ยนร้านจากข้าวมันไก่เป็น steak แล้วสังเกตเวลารอ

---

## 9. Task 2 — `foodcourt_02_gather.py`

### 9.1 เป้าหมาย

ส่งออเดอร์ 3 ร้านพร้อมกัน และรอให้ **ทุกออเดอร์** เสร็จด้วย `asyncio.gather()`

### 9.2 ออเดอร์ที่ส่ง

| ลำดับที่ส่งเข้า `gather()` | ร้าน | เวลา |
|---:|---|---:|
| 1 | `hainanese_chicken` | 0.8 วินาที |
| 2 | `noodle` | 1.5 วินาที |
| 3 | `steak` | 4.0 วินาที |

### 9.3 ใช้ `gather()`

```python
results = await asyncio.gather(
    send_order_to_kitchen(... "hainanese_chicken" ...),
    send_order_to_kitchen(... "noodle" ...),
    send_order_to_kitchen(... "steak" ...)
)
```

`gather()` จะ:

1. จัดให้ coroutine ทั้งสามคืบหน้าพร้อมกัน
2. รอจนทุกงานเสร็จ
3. คืน list ของผลลัพธ์

### 9.4 ทำไมใช้เวลาประมาณ 4 วินาที ไม่ใช่ 6.3 วินาที

ถ้าทำเรียงกัน:

```text
0.8 + 1.5 + 4.0 = 6.3 วินาที
```

แต่เมื่อทำ concurrent:

```text
เริ่มทั้งสามร้านใกล้กัน
ข้าวมันไก่เสร็จที่ 0.8 วิ
ก๋วยเตี๋ยวเสร็จที่ 1.5 วิ
สเต็กเสร็จที่ 4.0 วิ
gather จบเมื่อร้านสุดท้ายเสร็จ
```

จึงใช้เวลาประมาณร้านที่ช้าที่สุด คือ 4.0 วินาที บวก network overhead เล็กน้อย

### 9.5 ลำดับของ `results`

จุดที่มักออกสอบ:

> `gather()` คืนผลลัพธ์ตาม **ลำดับ argument ที่ส่งเข้าไป** ไม่ใช่ลำดับเวลาที่งานเสร็จ

ดังนั้น `results` จะเรียง:

1. hainanese chicken
2. noodle
3. steak

แม้ข้าวมันไก่จะเสร็จก่อนและสเต็กเสร็จทีหลัง

### 9.6 Expected behavior

```text
[Pickup] Shop: hainanese_chicken | Menu: Chicken Rice is ready!
[Pickup] Shop: noodle | Menu: Wonton Noodles is ready!
[Pickup] Shop: steak | Menu: Sizzling Steak is ready!
Total time: ประมาณ 4.xx seconds (Equals to the slowest dish).
```

### 9.7 Lab ย่อย

1. สลับลำดับ argument ใน `gather()` แล้วดู order ของ `results`
2. เอา steak ออก แล้วทำนายเวลารวม
3. เพิ่มร้านข้าวมันไก่อีกหนึ่งออเดอร์ แล้วดูว่าเวลารวมเปลี่ยนมากหรือไม่

---

## 10. Task 3 — `foodcourt_03_wait_first.py`

### 10.1 เป้าหมาย

ส่ง 3 ออเดอร์พร้อมกัน แต่ต้องการแค่ **จานแรกที่เสร็จ**

### 10.2 ทำไมต้องสร้าง Task ก่อน

`asyncio.wait()` ในโค้ดนี้รับ Task objects:

```python
task1 = asyncio.create_task(...)
task2 = asyncio.create_task(...)
task3 = asyncio.create_task(...)
```

Task object ทำให้ตรวจสถานะ อ่าน result และเรียก `.cancel()` ได้

### 10.3 รอแบบ `FIRST_COMPLETED`

```python
done, pending = await asyncio.wait(
    [task1, task2, task3],
    return_when=asyncio.FIRST_COMPLETED
)
```

ผลลัพธ์ถูกแบ่งเป็น 2 set:

| ตัวแปร | เก็บอะไร |
|---|---|
| `done` | Task ที่เสร็จแล้ว |
| `pending` | Task ที่ยังไม่เสร็จ |

`FIRST_COMPLETED` หมายถึงหยุดรอเมื่อมี Task แรกเสร็จ ไม่ได้รอทั้งหมด

### 10.4 ใครควรเป็นผู้ชนะ

จาก latency:

```text
hainanese_chicken = 0.8 วินาที
noodle             = 1.5 วินาที
steak              = 4.0 วินาที
```

ดังนั้นข้าวมันไก่ควรชนะเมื่อ server ทำงานปกติ

### 10.5 อ่านผลจากผู้ชนะ

```python
winner_task = done.pop()
result = winner_task.result()
```

- `.pop()` ดึง Task หนึ่งตัวออกจาก set
- `.result()` อ่านค่าที่ Task return
- ใช้ `.result()` ได้อย่างปลอดภัยเมื่อ Task อยู่ใน `done` และไม่ได้พัง/cancel

### 10.6 ยกเลิกงานที่เหลือ

```python
for task in pending:
    task.cancel()
```

หลังข้าวมันไก่เสร็จ ก๋วยเตี๋ยวและสเต็กไม่จำเป็นแล้ว จึงส่งสัญญาณยกเลิก

แนวปฏิบัติที่สมบูรณ์ในระบบทั่วไปคือ หลัง `cancel()` ควรรอเก็บ Task ที่ถูกยกเลิกด้วย:

```python
await asyncio.gather(*pending, return_exceptions=True)
```

โค้ดปัจจุบันยังไม่มีบรรทัดนี้ แต่ตัวอย่างนี้ช่วยให้เข้าใจว่าการ cancel เป็นคำสั่งร้องขอ และควรเปิดโอกาสให้ Task จบขั้นตอนยกเลิกอย่างเรียบร้อย

### 10.7 Expected behavior

```text
Winner served dish: Shop: hainanese_chicken | Menu: Chicken Rice Thigh
Cleaning up: Canceling 2 remaining pending orders...
Total waiting time for the first dish: ประมาณ 0.8x seconds.
```

### 10.8 `wait()` ไม่ได้ยกเลิก pending ให้อัตโนมัติ

นี่เป็นจุดสำคัญ:

- `asyncio.wait(... FIRST_COMPLETED)` แค่หยุดรอ
- งานที่อยู่ใน `pending` ยังคงทำงานต่อ
- ถ้าไม่ต้องการแล้ว โปรแกรมต้อง `.cancel()` เอง

### 10.9 Lab ย่อย

1. เปลี่ยน latency ให้ noodle เร็วที่สุด แล้วทำนาย winner
2. เอา loop `cancel()` ออก แล้วสังเกตว่าโปรแกรมรอหรือจบต่างกันอย่างไร
3. เพิ่ม `gather(*pending, return_exceptions=True)` หลัง cancel

---

## 11. Task 4 — `foodcourt_04_wait_for.py`

### 11.1 เป้าหมาย

สั่งสเต็กที่ใช้ 4.0 วินาที แต่กำหนด SLA ว่าจะรอไม่เกิน 2.0 วินาที

### 11.2 ใช้ `asyncio.wait_for()`

```python
result = await asyncio.wait_for(
    send_order_to_kitchen(
        STUDENT_ID,
        "steak",
        "Sizzling Steak"
    ),
    timeout=2.0
)
```

`wait_for()` รับ:

1. awaitable ที่ต้องการรอ
2. เวลาสูงสุดผ่าน `timeout`

### 11.3 ทำนายผล

```text
สเต็กต้องใช้ 4.0 วินาที
แต่โปรแกรมรอได้ 2.0 วินาที
4.0 > 2.0
ดังนั้นเกิด TimeoutError
```

### 11.4 จัดการ Timeout

```python
except asyncio.TimeoutError:
    print("Timeout occurred: Steak took too long! ...")
```

การมี `try/except` ทำให้โปรแกรมไม่ crash แต่เปลี่ยนไปทำ fallback behavior แทน

### 11.5 บรรทัดที่ปกติไม่ทำงาน

```python
print(f"{ctime()} | Order received: {result}")
```

ในค่าปัจจุบัน บรรทัดนี้ไม่ควรถูกเรียก เพราะ timeout เกิดก่อน server ตอบ

ถ้าเปลี่ยน timeout เป็น `5.0` สเต็กมีเวลาพอทำเสร็จ และบรรทัดนี้จะทำงาน

### 11.6 `wait_for()` กับ HTTP timeout คนละชั้น

ในระบบนี้มี timeout สองชั้น:

| ชั้น | อยู่ที่ | ค่า | หน้าที่ |
|---|---|---:|---|
| Application timeout | `asyncio.wait_for()` | 2.0 วินาที | กฎของ Task 4 ว่าจะรออาหารนานเท่าไร |
| HTTP client timeout | `client.post(... timeout=10.0)` | 10.0 วินาที | จำกัดเวลารวมของ HTTP request |

Application timeout 2 วินาทีสั้นกว่า จึงเกิดก่อน HTTP timeout 10 วินาที

### 11.7 Expected behavior

```text
[System] Order sent. Monitoring 2.0s timeout limit...
Timeout occurred: Steak took too long! Leaving the food court now.
```

เวลารวมควรใกล้ 2 วินาทีเมื่อเชื่อมต่อ server สำเร็จและ server จำลองสเต็ก 4 วินาที

### 11.8 Lab ย่อย

| ค่า timeout | ผลที่คาด |
|---:|---|
| `1.0` | timeout |
| `2.0` | timeout |
| `3.0` | timeout |
| `5.0` | ได้ response สำเร็จ |

ลองเปลี่ยนร้านเป็น `noodle` โดยคง timeout 2.0 วินาที ก๋วยเตี๋ยวควรเสร็จทันเพราะใช้ 1.5 วินาที

---

## 12. Task 5 — `foodcourt_05_mix_concepts.py`

### 12.1 เป้าหมาย

รวมสามแนวคิดในงานเดียว:

- `asyncio.create_task()`
- `asyncio.wait_for()`
- `asyncio.gather()`

### 12.2 Task ของก๋วยเตี๋ยว

```python
noodle_task = asyncio.create_task(
    send_order_to_kitchen(
        STUDENT_ID,
        "noodle",
        "Wonton Noodles"
    )
)
```

ก๋วยเตี๋ยวใช้ 1.5 วินาทีและไม่มี application timeout เพิ่ม

### 12.3 Task ของข้าวมันไก่

```python
chicken_task = asyncio.create_task(
    asyncio.wait_for(
        send_order_to_kitchen(
            STUDENT_ID,
            "hainanese_chicken",
            "Chicken Rice"
        ),
        timeout=1.0
    )
)
```

Task นี้มี `wait_for()` ครอบอยู่:

```text
ข้าวมันไก่ใช้ 0.8 วินาที
timeout ให้ 1.0 วินาที
0.8 < 1.0
จึงควรเสร็จทัน
```

### 12.4 รวมด้วย `gather()`

```python
results = await asyncio.gather(noodle_task, chicken_task)
```

แม้ข้าวมันไก่เสร็จที่ประมาณ 0.8 วินาที แต่ `gather()` ต้องรอก๋วยเตี๋ยวด้วย จึงจบที่ประมาณ 1.5 วินาที

### 12.5 Success path

ถ้าทั้งสองจานเสร็จตาม latency:

```text
Success: All food served on time! Received 2 dishes.
Total elapsed time: ประมาณ 1.5x seconds.
```

### 12.6 Failure path

ถ้าข้าวมันไก่ใช้เกิน 1.0 วินาที `wait_for()` จะโยน `TimeoutError` และเข้า:

```python
except asyncio.TimeoutError:
    print("Failed: One of the dishes took too long!")
```

ข้อควรรู้ระดับสอบ:

- เมื่อ coroutine หนึ่งใน `gather()` เกิด exception, `gather()` จะส่ง exception นั้นออกมาให้ `try/except`
- `gather()` ไม่ได้แปลว่าจะยกเลิก Task อื่นทั้งหมดให้เสมอไป
- ถ้าต้องการ cleanup ที่ควบคุมได้ ควรเก็บ Task references, cancel งานที่เหลือ และ await งานเหล่านั้นอย่างชัดเจน

### 12.7 จุดสังเกตเรื่องรหัสนักศึกษา

Task 1–4 ใช้:

```text
6710301033
```

แต่ Task 5 ปัจจุบันใช้:

```text
6710301017
```

คู่มือนี้บันทึกตามโค้ดจริง ใบควรตรวจ requirement หรือรหัสของตนเองก่อนส่งงาน แต่ไม่ควรเปลี่ยนโดยเดาเองค่ะ

### 12.8 Lab ย่อย

1. เปลี่ยน timeout ของข้าวมันไก่เป็น `0.5` แล้วทำนายผล
2. เปลี่ยนจากข้าวมันไก่เป็น steak แต่คง timeout `1.0`
3. ใช้ `return_exceptions=True` กับ `gather()` แล้วสังเกตว่า `results` เปลี่ยนอย่างไร
4. เพิ่ม Task สเต็กตัวที่สาม แล้วทำนายเวลารวม

---

## 13. ตารางเปรียบเทียบคำสั่งหลัก

| คำสั่ง | รออะไร | คืนอะไร | หยุดรอเมื่อ | ยกเลิกงานอื่นอัตโนมัติไหม | ใช้ในไฟล์ |
|---|---|---|---|---|---|
| `create_task(coro)` | ไม่ได้รอทันที | Task | ไม่เกี่ยว | ไม่ | Task 1, 3, 5 |
| `await task` | Task เดียว | ค่าที่ Task return | Task นั้นจบ | ไม่ | Task 1 |
| `gather(*aws)` | ทุกงาน | list ผลลัพธ์ตามลำดับ input | ทุกงานจบ หรือมี exception ตาม behavior | ไม่ควรสมมติว่ายกเลิกทุกงาน | Task 2, 5 |
| `wait(tasks, FIRST_COMPLETED)` | Task ชุดหนึ่ง | `(done, pending)` | มีตัวแรกเสร็จ | ไม่ | Task 3 |
| `wait_for(aw, timeout)` | awaitable เดียว | ผลของ awaitable | งานเสร็จหรือหมดเวลา | ยกเลิก awaitable เมื่อ timeout ตามกลไก asyncio | Task 4, 5 |
| `task.cancel()` | ไม่ได้รอ | `True/False` ว่าส่งคำขอยกเลิกได้ไหม | — | ยกเลิกเฉพาะ Task นั้น | Task 3 |

### วิธีเลือกใช้แบบจำง่าย

```text
อยากให้งานเริ่มก่อน แล้วค่อยกลับมารอ       -> create_task
อยากได้ผลครบทุกงาน                         -> gather
อยากได้จานแรก แล้วแยก done/pending          -> wait + FIRST_COMPLETED
อยากจำกัดเวลาของงานหนึ่ง                    -> wait_for
ไม่ต้องการงานที่เหลือแล้ว                    -> cancel + await cleanup
```

---

## 14. ตารางทำนายเวลาของ Task 1–5

ตารางนี้สมมติว่า server/network ทำงานปกติและไม่มี overhead มากผิดปกติ

| Task | งานที่รอ | เวลาประมาณ | เหตุผล |
|---|---|---:|---|
| Task 1 | ข้าวมันไก่ | 0.8+ วิ | รอ Task เดียว |
| Task 2 | ข้าวมันไก่ + ก๋วยเตี๋ยว + สเต็ก | 4.0+ วิ | `gather()` รอร้านช้าที่สุด |
| Task 3 | จานแรกจาก 3 ร้าน | 0.8+ วิ | `FIRST_COMPLETED` ได้ข้าวมันไก่ |
| Task 4 | สเต็ก แต่ timeout 2.0 | ~2.0 วิ | timeout ก่อนสเต็กเสร็จ |
| Task 5 | ก๋วยเตี๋ยว + ข้าวมันไก่ | 1.5+ วิ | ทั้งคู่สำเร็จและ `gather()` รอก๋วยเตี๋ยว |

เครื่องหมาย `+` หมายถึงอาจมี network และ runtime overhead เพิ่มเล็กน้อย

---

## 15. วิธีรันทั้งชุด

### 15.1 ติดตั้ง Library

ถ้ายังไม่มี package:

```bash
python -m pip install fastapi uvicorn httpx
```

### 15.2 เปิด Local API Server

Terminal 1:

```bash
cd Week4
python -m uvicorn foodcourt_api:app --port 8088
```

เปิดตรวจ API docs:

```text
http://127.0.0.1:8088/docs
```

> Local server จะถูกใช้จริงก็ต่อเมื่อ URL ใน `food_utils.py` ชี้มาที่ `127.0.0.1:8088` ค่ะ

### 15.3 รัน Client

จาก root project ใน Terminal 2:

```bash
python Week4/foodcourt_01_create_task.py
python Week4/foodcourt_02_gather.py
python Week4/foodcourt_03_wait_first.py
python Week4/foodcourt_04_wait_for.py
python Week4/foodcourt_05_mix_concepts.py
```

### 15.4 ตรวจ Syntax

```bash
python -m py_compile Week4/*.py
```

---

## 16. Debug Checklist

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ |
|---|---|---|
| `ModuleNotFoundError: httpx` | ยังไม่ได้ติดตั้ง HTTPX | `python -m pip install httpx` |
| `ModuleNotFoundError: fastapi` | ยังไม่ได้ติดตั้ง FastAPI | `python -m pip install fastapi uvicorn` |
| `Connection failed` | Server ไม่เปิด, IP/port ผิด หรืออยู่คนละ network | ตรวจ URL และเปิด server |
| เปิด local server แล้ว client ยังต่อไม่ได้ | Client ยังชี้ไป `172.16.2.117` | ตรวจบรรทัด URL ใน `food_utils.py` |
| HTTP 404 | `shop_name` ไม่มีใน `KITCHEN_LATENCY` | ใช้ชื่อร้านให้ตรงทุกตัวอักษร |
| ค่า `result.get('shop')` เป็น `None` | Helper คืน error dictionary ที่ไม่มี key `shop` | print `result` เต็ม ๆ และดู `detail` |
| Task 4 ไม่ timeout | Server ตอบ error เร็ว หรือ latency ไม่ใช่ 4 วินาที | ตรวจ response และ server ที่ Client เรียกจริง |
| Task 3 winner ไม่ใช่ข้าวมันไก่ | Server/network latency เปลี่ยน หรือ request บางตัว error เร็ว | ตรวจ result และ server log |
| `TimeoutError` | งานเกินเวลาที่ `wait_for()` กำหนด | เพิ่ม timeout หรือเลือกงานที่เร็วขึ้น |
| Server เปิดไม่ได้เพราะ port ถูกใช้ | มี process อื่นใช้ port 8088 | ปิด server เก่าหรือใช้ portใหม่ให้ตรงทั้งสองฝั่ง |

### ระวัง Error Response ที่เสร็จเร็ว

`send_order_to_kitchen()` จับ exception แล้ว return dictionary ทันที เช่น:

```python
{
    "status": "ERROR",
    "detail": "Connection failed: ..."
}
```

ผลคือ Task อาจถูกนับว่า “เสร็จแล้ว” อย่างรวดเร็ว แม้ไม่ได้อาหารจริง

ดังนั้นในระบบจริงไม่ควรดูแค่ว่า Task เสร็จก่อน แต่ต้องตรวจด้วยว่า:

```python
result.get("status") == "READY_FOR_PICKUP"
```

โค้ดปัจจุบันเป็นตัวอย่างเพื่อเรียน concurrency จึงยังไม่ได้เพิ่ม validation นี้ทุกไฟล์ค่ะ

---

## 17. คำถามแนวสอบพร้อมคำตอบสั้น

### 17.1 `async def` คืออะไร

ประกาศ coroutine function ที่สามารถใช้ `await` และทำงานร่วมกับ event loop ได้

### 17.2 `await` ทำอะไร

รอผลของ awaitable โดยเปิดโอกาสให้ event loop ไปทำ Task อื่นระหว่างที่งานนี้กำลังรอ

### 17.3 `create_task()` ต่างจากเรียก coroutine ตรง ๆ อย่างไร

การเรียก async function ได้ coroutine object ส่วน `create_task()` ส่ง coroutine เข้า event loop ให้เริ่มมีโอกาสทำงาน

### 17.4 ทำไม Task 2 ใช้ `gather()`

เพราะต้องการรอและรับผลลัพธ์ของออเดอร์ครบทุกจาน

### 17.5 ทำไม Task 2 ใช้เวลาประมาณ 4 วินาที

สามงานทำ concurrent และ `gather()` รอร้านช้าที่สุด คือ steak 4.0 วินาที

### 17.6 ทำไม Task 3 ใช้ `wait()` แทน `gather()`

เพราะต้องการหยุดรอเมื่อมีจานแรกเสร็จ และต้องการแยก `done` กับ `pending`

### 17.7 `FIRST_COMPLETED` ยกเลิกงานที่เหลือหรือไม่

ไม่ยกเลิก ต้องวน `.cancel()` pending tasks เอง

### 17.8 ทำไมต้อง cleanup pending Task

เพราะงานที่ไม่ใช้แล้วอาจยังใช้ connection, เวลา และ resource ต่อ

### 17.9 `wait_for()` ใช้ทำอะไร

กำหนดเวลารอสูงสุดให้ awaitable ถ้าเกินจะเกิด timeout

### 17.10 ทำไม Task 4 timeout

สเต็กใช้ 4.0 วินาที แต่ `wait_for()` อนุญาตเพียง 2.0 วินาที

### 17.11 `time.sleep()` กับ `asyncio.sleep()` ต่างกันอย่างไร

- `time.sleep()` block thread
- `await asyncio.sleep()` คืน control ให้ event loop ไปทำงานอื่น

### 17.12 HTTP 404 หมายถึงอะไรในระบบนี้

เรียก endpoint หรือชื่อร้านที่ server ไม่พบ เช่น `/order/pizza`

### 17.13 ทำไมต้องใช้ `async with httpx.AsyncClient()`

เพื่อเปิดและปิด HTTP client/connection อย่างถูกต้อง พร้อมรองรับ request แบบ async

### 17.14 `gather()` คืนผลตามลำดับใด

คืนตามลำดับ awaitables ที่ส่งเข้าไป ไม่ใช่ลำดับที่เสร็จ

### 17.15 `done()` เป็น `True` แปลว่าสำเร็จเสมอไหม

ไม่เสมอ Task อาจสำเร็จ, พังด้วย exception หรือถูก cancel ก็ถือว่า done ได้

---

## 18. แบบฝึกหัดรวม

### Exercise 1 — ทำนายผลโดยไม่รัน

ถ้าแก้ latency เป็น:

```python
KITCHEN_LATENCY = {
    "hainanese_chicken": 2.0,
    "noodle": 0.5,
    "steak": 1.0
}
```

ตอบว่า:

1. Task 2 ใช้เวลาประมาณเท่าไร
2. Task 3 ร้านใดชนะ
3. Task 4 ยัง timeout หรือไม่

เฉลยแนวคิด:

1. ประมาณ 2.0 วินาที เพราะ `gather()` รอร้านช้าที่สุด
2. noodle ชนะ เพราะใช้ 0.5 วินาที
3. steak ใช้ 1.0 วินาทีและ timeout 2.0 จึงควรสำเร็จ

### Exercise 2 — เปรียบเทียบ `gather` กับ `wait`

อธิบายด้วยคำของตัวเอง:

```text
gather = ______________________________________
wait + FIRST_COMPLETED = ______________________
```

คำตอบย่อ:

```text
gather = รอทุกงานและรับผลทั้งหมด
wait + FIRST_COMPLETED = หยุดรอเมื่อมีงานแรกเสร็จ และแยกงานที่เหลือเป็น pending
```

### Exercise 3 — ออกแบบ SLA

กำหนดว่า:

- ข้าวมันไก่ต้องไม่เกิน 1.0 วินาที
- ก๋วยเตี๋ยวต้องไม่เกิน 2.0 วินาที
- สเต็กต้องไม่เกิน 3.0 วินาที

จาก latency ปัจจุบัน:

| ร้าน | Latency | SLA | ผล |
|---|---:|---:|---|
| ข้าวมันไก่ | 0.8 | 1.0 | ผ่าน |
| ก๋วยเตี๋ยว | 1.5 | 2.0 | ผ่าน |
| สเต็ก | 4.0 | 3.0 | timeout |

---

## 19. สิ่งที่ควรพูดได้ก่อนเข้าสอบ

ลองอธิบายโดยไม่เปิดคู่มือ:

- [ ] Client และ Server ต่างกันอย่างไร
- [ ] `food_utils.py` มีหน้าที่อะไร
- [ ] FastAPI รับ `shop_name` และ JSON body จากไหน
- [ ] ทำไม endpoint ต้องใช้ `await asyncio.sleep()`
- [ ] `create_task()` ทำอะไร
- [ ] `.done()` บอกอะไรและไม่บอกอะไร
- [ ] `gather()` เหมาะกับโจทย์แบบไหน
- [ ] `wait(... FIRST_COMPLETED)` เหมาะกับโจทย์แบบไหน
- [ ] `done` และ `pending` ต่างกันอย่างไร
- [ ] ทำไม pending tasks ต้องถูก cleanup
- [ ] `wait_for()` ทำให้เกิด timeout อย่างไร
- [ ] ทำไม Task 2 ใช้ประมาณ 4 วินาที
- [ ] ทำไม Task 3 ได้ข้าวมันไก่เป็นผู้ชนะ
- [ ] ทำไม Task 4 timeout ที่ประมาณ 2 วินาที
- [ ] ทำไม Task 5 ปกติใช้ประมาณ 1.5 วินาที
- [ ] URL `127.0.0.1` ต่างจาก `172.16.2.117` อย่างไร

---

## 20. Cheat Sheet ก่อนสอบ

```text
async def
    สร้าง coroutine function

await
    รอ awaitable และคืน control ให้ event loop ระหว่างรอ

asyncio.run(main())
    เปิด event loop แล้วรัน main coroutine

asyncio.create_task(coro)
    ส่ง coroutine เข้า event loop และได้ Task object

task.done()
    เช็กว่า Task จบแล้วหรือยัง แต่ไม่ได้ยืนยันว่าสำเร็จ

await task
    รอ Task และรับค่าที่ return

asyncio.gather(a, b, c)
    รอทุกงาน คืนผลตามลำดับ input

asyncio.wait(tasks, return_when=FIRST_COMPLETED)
    รอจนมีตัวแรกเสร็จ คืน done และ pending

task.cancel()
    ส่งคำขอยกเลิก Task

asyncio.wait_for(aw, timeout=n)
    รอไม่เกิน n วินาที ถ้าเกินเกิด timeout

httpx.AsyncClient
    ส่ง HTTP request แบบ async

FastAPI
    สร้าง HTTP API server

POST /order/{shop_name}
    ส่งออเดอร์ไปยังร้านที่ระบุ
```

จำสถานการณ์ 4 แบบนี้ให้ได้:

```text
ต้องการผลครบทุกจาน       -> gather
ต้องการจานแรก             -> wait + FIRST_COMPLETED
ต้องการกำหนดเวลาสูงสุด    -> wait_for
ต้องการเริ่มงานไว้ก่อน     -> create_task
```

---

## 21. สรุปสุดท้าย

Week 4 ไม่ได้สอนแค่เขียน async function แต่สอนให้เอา `asyncio` ไปใช้กับงาน I/O จริงผ่าน HTTP

หัวใจของแต่ละไฟล์:

| ไฟล์ | จำสั้น ๆ |
|---|---|
| `foodcourt_api.py` | Server รับออเดอร์และจำลองเวลาทำอาหาร |
| `food_utils.py` | Client helper ส่ง HTTP POST และคืน JSON |
| `foodcourt_01_create_task.py` | สร้าง Task ตรวจสถานะ แล้ว await ผล |
| `foodcourt_02_gather.py` | รอทุกจาน เวลาขึ้นกับจานช้าที่สุด |
| `foodcourt_03_wait_first.py` | เอาจานแรก แล้ว cancel จานที่เหลือ |
| `foodcourt_04_wait_for.py` | จำกัดเวลารอสเต็กและรับมือ timeout |
| `foodcourt_05_mix_concepts.py` | ผสม Task, timeout และ gather |

ถ้าใบจำได้ว่า **“จะรอทุกงาน, รอจานแรก หรือรอแบบมีเส้นตาย”** ใบจะเลือกใช้ `gather()`, `wait()` และ `wait_for()` ได้ถูกต้องค่ะ
