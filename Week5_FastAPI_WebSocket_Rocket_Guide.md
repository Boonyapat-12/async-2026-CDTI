# Week 5 FastAPI, Async HTTP, WebSocket และ Rocket Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงใน Week 5 เท่านั้น** เหมาะสำหรับผู้เริ่มต้น ใช้ทำแล็บ และใช้ทบทวนก่อนสอบเรื่อง FastAPI, HTTP API, `async`/`await`, HTTPX, WebSocket, broadcast และระบบจรวดแบบ real-time

ไฟล์ต้นฉบับที่ใช้ทั้งหมด 10 ไฟล์:

- `Week5/fastapi_basic_lab.py`
- `Week5/fastapi_async_basic_lab.py`
- `Week5/fastapi_async_external_api_lab.py`
- `Week5/chat-hello/main.py`
- `Week5/chat-hello/client.py`
- `Week5/chat-hello/client2.py`
- `Week5/rocket/main.py`
- `Week5/rocket/dashboard.py`
- `Week5/rocket/student.py`
- `Week5/rocket/student2.py`

> **เป้าหมาย:** อ่านจบแล้วควรสร้างและอธิบาย HTTP endpoint ได้ แยก path/query/body ได้ เข้าใจ blocking กับ non-blocking เรียก API ภายนอกแบบ sequential/concurrent และอธิบายการสื่อสาร WebSocket ของห้องแชตกับเกมจรวดได้

---

## 1. ภาพรวม Week 5 กำลังเรียนอะไร

Week 5 เดินจากเว็บ API ธรรมดาไปสู่ระบบ real-time เป็นลำดับ:

```text
FastAPI พื้นฐาน
GET / POST / Path / Query / JSON / Pydantic
              |
              v
FastAPI + async/await
blocking เทียบ non-blocking และ asyncio.gather()
              |
              v
Async HTTP Client
ใช้ httpx เรียก API ภายนอก + timeout + fallback
              |
              v
WebSocket Chat
เชื่อมต่อค้างไว้ รับ-ส่งข้อความสองทางและ broadcast
              |
              v
Rocket Real-time System
ส่งคำสั่ง CONTROL และกระจายสถานะจรวดให้ Dashboard
```

### 🎯 ใช้ทำอะไรได้หลังเรียน

- สร้าง REST-like API สำหรับอ่านและรับข้อมูล
- ทำ endpoint ที่รองรับงานรอ I/O โดยไม่ block event loop
- ดึงข้อมูลหลายแหล่งพร้อมกัน
- สร้างห้องแชตที่ข้อความปรากฏทันทีทุกหน้าจอ
- สร้าง controller หลายเครื่องควบคุมวัตถุบน dashboard กลาง

---

## 2. คำศัพท์พื้นฐาน

| คำ | ความหมายแบบง่าย | ตัวอย่างในโค้ด |
|---|---|---|
| FastAPI | Framework สำหรับสร้างเว็บ API ด้วย Python | `app = FastAPI(...)` |
| Uvicorn | ASGI server ที่นำ FastAPI app ไปรัน | `uvicorn main:app ...` |
| Route / Endpoint | Method และ path ที่เปิดให้ client เรียก | `GET /users`, `WS /ws/{client_id}` |
| HTTP GET | ขออ่านข้อมูล | `@app.get("/")` |
| HTTP POST | ส่งข้อมูลไปให้ server ประมวลผล | `@app.post("/register/student")` |
| Path parameter | ค่าที่ฝังอยู่ใน path | `item_id` ใน `/items/{item_id}` |
| Query parameter | ค่าหลัง `?` ใน URL | `?username=Alice&age=21` |
| Request body | ข้อมูลหลักที่ส่งมากับ request | JSON ของนักศึกษา |
| JSON | ข้อมูลแบบ key-value | `{"type":"CONTROL"}` |
| Pydantic model | สัญญารูปแบบและชนิดข้อมูล | `SimpleStudent(BaseModel)` |
| Validation | ตรวจว่าข้อมูลตรง schema หรือไม่ | `gpa` ต้องแปลงเป็น `float` ได้ |
| Sync / Blocking | งานครอบครอง thread ขณะรอ | `time.sleep(3)` |
| Async / Non-blocking wait | ยอมคืน control ให้ event loop ระหว่างรอ | `await asyncio.sleep(3)` |
| Coroutine | งานจาก function ที่ประกาศ `async def` | `fetch_single_api()` |
| Event loop | ตัวสลับให้งาน async หลายงานคืบหน้า | ทำงานเมื่อ Uvicorn รัน app |
| Concurrency | หลายงานคืบหน้าสลับกันระหว่างรอ | `asyncio.gather(...)` |
| HTTPX | HTTP client ที่รองรับ async | `httpx.AsyncClient()` |
| Timeout | เวลารอสูงสุด | `timeout=3.0` |
| Fallback | ข้อมูลสำรองเมื่อบริการจริงล้มเหลว | `MOCK_CAT_FACT` |
| Graceful degradation | บริการยังตอบได้แม้บางส่วนเสีย | เปลี่ยนไปคืน mock data |
| WebSocket | connection สองทางที่เปิดค้างไว้ | `/ws/{student_id}` |
| Broadcast | ส่งข้อความเดียวให้ทุก connection | `manager.broadcast(...)` |
| Canvas | พื้นที่วาดกราฟิกใน browser | `<canvas width="800" height="600">` |
| SPAWN / UPDATE / DESPAWN | event เกิด/เปลี่ยน/หายของจรวด | JSON จาก Rocket server |

---

# Part A — FastAPI พื้นฐาน

## 3. `Week5/fastapi_basic_lab.py`

### 3.1 หน้าที่ของไฟล์

ไฟล์นี้สร้าง FastAPI app แรก และสอน 4 เรื่อง:

1. GET endpoint
2. Path parameter และการแปลง type
3. Query parameter และ default value
4. POST JSON body ผ่าน Pydantic model

App มี metadata:

```python
app = FastAPI(
    title="CS-302: Basic FastAPI Lab",
    description="...",
    version="1.0.0"
)
```

ข้อมูลนี้จะปรากฏในหน้า Swagger UI ที่ `/docs`

### 3.2 ตาราง Endpoint แบบครบถ้วน

| Method | Path | รับข้อมูล | ผลหลัก |
|---|---|---|---|
| GET | `/` | ไม่มี | ข้อความยืนยันว่า server ทำงาน |
| GET | `/items/{item_id}` | `item_id: int` จาก path | ID, type และค่า ID คูณ 2 |
| GET | `/users` | `username: str`, `age: int = 18` จาก query | เงื่อนไขค้นหาผู้ใช้ |
| POST | `/register/student` | JSON ตาม `SimpleStudent` | ข้อมูลนักศึกษาและ probation flag |

### 3.3 Endpoint `GET /`

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to CS-302! Your first FastAPI server is alive!"}
```

เมื่อเปิด `http://127.0.0.1:8000/` server จะ print log และคืน JSON หนึ่ง field

### 3.4 Path parameter: `GET /items/{item_id}`

```python
@app.get("/items/{item_id}")
def read_item_by_id(item_id: int):
    doubled_value = item_id * 2
```

ตัวอย่าง:

```text
GET /items/123
item_id ใน Python -> int 123
123 * 2 -> 246
```

Response สำคัญ:

```json
{
  "received_item_id": 123,
  "type_in_python": "<class 'int'>",
  "demonstration_math": "Your ID doubled is: 246"
}
```

ถ้าเรียก `/items/abc` FastAPI แปลง `abc` เป็น `int` ไม่ได้ จึงตอบ validation error แทนการเข้า function ตามปกติ

### 3.5 Query parameter: `GET /users`

```python
@app.get("/users")
def search_users(username: str, age: int = 18):
```

ตัวอย่าง URL:

```text
http://127.0.0.1:8000/users?username=Alice&age=21
```

- `username` ไม่มี default จึงเป็นค่าที่ต้องส่ง
- `age` มี default เป็น `18`
- `/users?username=Alice` จึงใช้ age 18
- `/users` ขาด `username` และจะเกิด validation error

### 3.6 Pydantic และ `POST /register/student`

Schema:

```python
class SimpleStudent(BaseModel):
    student_id: str
    nickname: str
    gpa: float
```

JSON ตัวอย่าง:

```json
{
  "student_id": "6710301033",
  "nickname": "Alice",
  "gpa": 1.75
}
```

Server คำนวณ:

```python
is_academic_probation = student.gpa < 2.00
```

ดังนั้น GPA 1.75 ได้ `academic_probation_alert: true` แต่ GPA 2.50 ได้ `false` การตรวจนี้เป็นเพียงเงื่อนไขในแล็บ ไม่ได้บันทึกข้อมูลลงฐานข้อมูล

### 3.7 Path, Query และ Body ต่างกันอย่างไร

| ชนิด | อยู่ที่ไหน | ตัวอย่าง |
|---|---|---|
| Path | เป็นส่วนหนึ่งของ URL path | `/items/123` |
| Query | หลัง `?` และคั่นด้วย `&` | `/users?username=Alice&age=21` |
| Body | payload ภายใน request | JSON ของ `SimpleStudent` |

---

# Part B — FastAPI กับ Async

## 4. `Week5/fastapi_async_basic_lab.py`

### 4.1 Endpoint ทั้งหมด

| Method | Path | วิธีรอ | เวลาที่คาด |
|---|---|---|---:|
| GET | `/sync-delay` | `time.sleep(3)` | ~3 วินาที |
| GET | `/async-delay` | `await asyncio.sleep(3)` | ~3 วินาทีสำหรับ request นั้น |
| GET | `/concurrent-tasks` | `asyncio.gather()` รอ 2, 3, 1 วินาทีพร้อมกัน | ~3 วินาที |

### 4.2 `/sync-delay` — synchronous blocking

```python
@app.get("/sync-delay")
def sync_delay():
    time.sleep(3)
```

`time.sleep(3)` block thread ที่กำลังรัน function นั้นอยู่เต็ม 3 วินาที โค้ดอธิบายไว้อย่างถูกต้องว่า FastAPI นำ endpoint แบบ `def` ไปทำใน thread pool จึงไม่ควรสรุปง่ายเกินไปว่า “ทำให้ทั้ง server หยุดทั้งหมด” แต่ request นี้ยังครอบครอง worker thread ระหว่างรอ

### 4.3 `/async-delay` — cooperative asynchronous wait

```python
@app.get("/async-delay")
async def async_delay():
    await asyncio.sleep(3)
```

Request นี้ยังใช้เวลาประมาณ 3 วินาทีเหมือนเดิม แต่ระหว่าง sleep coroutine คืน control ให้ event loop เพื่อดูแลงานอื่นได้

```text
เวลา request เดียว:
/sync-delay  ≈ 3 วินาที
/async-delay ≈ 3 วินาที

ความต่างสำคัญ:
time.sleep       -> block thread
await async sleep -> ยอมให้ event loop ไปทำงานอื่น
```

> `async def` ไม่ได้ทำให้ทุกอย่างเร็วเอง ถ้าใส่ blocking code ลงใน `async def` ก็ยังสร้างปัญหาได้

### 4.4 `/concurrent-tasks` — `asyncio.gather()`

Helper ภายใน endpoint จำลอง 3 API:

| งาน | เวลารอ | ผลที่ return |
|---|---:|---|
| `API_Alpha` | 2 วินาที | `Data from API_Alpha` |
| `API_Beta` | 3 วินาที | `Data from API_Beta` |
| `API_Gamma` | 1 วินาที | `Data from API_Gamma` |

```python
results = await asyncio.gather(
    fetch_data_from_api("API_Alpha", 2),
    fetch_data_from_api("API_Beta", 3),
    fetch_data_from_api("API_Gamma", 1)
)
```

ถ้ารอทีละงานจะเป็น `2 + 3 + 1 = 6` วินาที แต่ `gather()` ทำให้ทั้งสามคืบหน้าพร้อมกัน จึงรอประมาณงานช้าที่สุดคือ 3 วินาที

สิ่งที่มักออกสอบ:

- ลำดับ **เสร็จ**: Gamma, Alpha, Beta
- ลำดับใน `results`: Alpha, Beta, Gamma ตามลำดับ argument ของ `gather()`
- นี่คือ concurrency ของงานรอ I/O ไม่ควรเรียกว่าใช้ CPU คำนวณสามงานแบบ parallel โดยอัตโนมัติ

---

# Part C — เรียก External API ด้วย HTTPX

## 5. `Week5/fastapi_async_external_api_lab.py`

### 5.1 บริการภายนอกและข้อมูลสำรอง

| ชื่อ | URL ในโค้ด | Mock data เมื่อเรียกไม่ได้ |
|---|---|---|
| Cat Fact | `https://catfact.ninja/fact` | fact เรื่องแมวนอน 70% ของชีวิต |
| Bitcoin Price | `https://api.coindesk.com/v1/bpi/currentprice.json` | USD rate `95,430.00` |
| Joke | `https://official-joke-api.appspot.com/random_joke` | มุก dark mode / bugs |

ผลจากบริการจริงเปลี่ยนได้ และบริการอาจ timeout, rate-limit, เปลี่ยนรูปแบบ หรือเข้าไม่ได้ โค้ดจึงมี fallback เพื่อให้ endpoint ของเรายังตอบได้

### 5.2 Endpoint ทั้งหมด

| Method | Path | พฤติกรรม |
|---|---|---|
| GET | `/single-fetch` | เรียก Cat Fact หนึ่งแหล่ง |
| GET | `/sequential-fetch` | เรียก Cat → Bitcoin → Joke ทีละตัว |
| GET | `/concurrent-fetch` | เรียกทั้งสามพร้อมกันด้วย `gather()` |

### 5.3 รูปแบบ HTTPX ที่ต้องจำ

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url, timeout=3.0)
    response.raise_for_status()
    data = response.json()
```

| บรรทัด | หน้าที่ |
|---|---|
| `AsyncClient()` | client สำหรับ network I/O แบบ async |
| `async with` | ปิด client/connection resource เมื่อจบ block |
| `await client.get(...)` | ส่ง GET โดยไม่ block event loop ระหว่างรอ network |
| `timeout=3.0` | รอ request นั้นสูงสุด 3 วินาที |
| `raise_for_status()` | เปลี่ยน HTTP error status เป็น exception |
| `response.json()` | แปลง JSON response เป็น Python object |

### 5.4 `/single-fetch`

เมื่อ Cat Fact สำเร็จ:

```json
{
  "status": "Success",
  "elapsed_seconds": 0.42,
  "source": "CatFact Ninja",
  "fallback_activated": false,
  "fetched_payload": {"fact": "...", "length": 123}
}
```

เมื่อเกิด `httpx.HTTPError`:

- server print network warning
- ใช้ `MOCK_CAT_FACT`
- `fallback_activated` เป็น `true`
- endpoint ยังคืน `status: "Success"` ตามโค้ด เพราะ success ในที่นี้หมายถึง endpoint ของเรายังตอบได้ ไม่ได้แปลว่า upstream สำเร็จ

### 5.5 `/sequential-fetch`

ลำดับการรอจริง:

```text
Cat เสร็จ/ล้มเหลว
       |
       v
Bitcoin เสร็จ/ล้มเหลว
       |
       v
Joke เสร็จ/ล้มเหลว
       |
       v
return ผลรวม
```

แม้ใช้ `await` และไม่ block event loop แต่ภายใน request นี้ยัง **รอแบบเรียงลำดับ** เพราะ request ถัดไปเริ่มหลัง request ก่อนหน้าจบ

กรณีเลวร้ายที่ทั้งสามรอจน timeout 3 วินาที เวลารวมอาจเข้าใกล้ 9 วินาทีบวก overhead ไม่ใช่รับประกันว่าจะเป็น 3 วินาที

### 5.6 `/concurrent-fetch`

Helper `fetch_safely(...)` จัดการความล้มเหลวของแต่ละ API เอง และคืน tuple:

```python
(data, fallback_was_used)
```

จากนั้นสร้าง coroutine 3 ตัวและรอพร้อมกัน:

```python
cat_res, btc_res, joke_res = await asyncio.gather(
    cat_task, btc_task, joke_task
)
```

หากทั้งสาม timeout ใกล้ 3 วินาทีพร้อมกัน เวลารวมโดยแนวคิดจะใกล้ timeout ที่ช้าที่สุด ไม่ใช่ 9 วินาที

```text
Sequential: Cat ----> BTC ----> Joke ----> return
Concurrent: Cat  ----------------->
            BTC  -----------------> return เมื่อครบ
            Joke ----------------->
```

`fallback_active = cat_fallback or btc_fallback or joke_fallback` จึงเป็น `true` ถ้ามีอย่างน้อยหนึ่งบริการใช้ mock

### 5.7 จุดสังเกตจากโค้ดจริง

- `HTTPException` ถูก import แต่ไม่ได้ใช้
- API ภายนอกและค่าที่ตอบไม่แน่นอน จึงไม่ควรจำ expected output แบบตายตัว
- `elapsed_seconds` รวม network latency และ overhead จริง
- `asyncio.gather()` ช่วยเมื่อแต่ละงานเป็นอิสระต่อกัน
- การจับ error ภายใน `fetch_safely()` ป้องกัน API หนึ่งล้มแล้วทำให้ batch ทั้งหมดพัง

---

# Part D — WebSocket Chat

## 6. HTTP กับ WebSocket ต่างกันอย่างไร

| ประเด็น | HTTP endpoint | WebSocket |
|---|---|---|
| รูปแบบ | request → response | connection สองทางเปิดค้างไว้ |
| เหมาะกับ | อ่าน/ส่งข้อมูลเป็นครั้ง ๆ | chat, dashboard, game real-time |
| FastAPI decorator | `@app.get`, `@app.post` | `@app.websocket` |
| รับข้อมูล | parameter/body | `receive_text()` หรือ `receive_json()` |
| ส่งข้อมูล | `return` response | `send_text()` หรือ `send_json()` |
| URL scheme | `http://` | `ws://` |

## 7. สถาปัตยกรรม Chat

```text
Browser ของ client.py (HTTP :8001)
        | WebSocket ws://SERVER:8088/ws/{student_id}
        |
        v
chat-hello/main.py (:8088)
ConnectionManager.active_connections
        |
        +---- broadcast ----> Browser client.py
        |
        +---- broadcast ----> Browser client2.py
        |
        +---- broadcast ----> client อื่นทุกคน

Browser ของ client2.py มาจาก local HTTP :8002
```

ต้องแยกให้ชัดว่า client แต่ละไฟล์เป็น **ทั้ง**:

1. Local FastAPI HTTP server สำหรับส่งหน้า HTML ให้ browser
2. หน้า JavaScript ที่เปิด WebSocket ไปยัง central server port 8088

## 8. `Week5/chat-hello/main.py` — Central Chat Server

### 8.1 Port และ Endpoint

คำสั่งที่เขียนในไฟล์:

```bash
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
```

| Protocol | Path | หน้าที่ |
|---|---|---|
| HTTP GET | `/` | ดูสถานะ server และรายชื่อ ID ที่เชื่อมอยู่ |
| WebSocket | `/ws/{student_id}` | ช่อง chat ของ student ID นั้น |

### 8.2 `ConnectionManager`

```python
self.active_connections: Dict[str, WebSocket] = {}
```

เก็บ connection โดยใช้ `student_id` เป็น key:

```text
{
  "6710301001": WebSocket-A,
  "6710301002": WebSocket-B
}
```

- `connect()` เรียก `await websocket.accept()` แล้วเก็บ connection
- `disconnect()` ลบ key ออกจาก dictionary
- `broadcast()` วนทุก connection และ `await connection.send_text(message)`

### 8.3 Flow เมื่อเข้าแชต

```text
Browser connect /ws/6710301001
          |
          v
server accept connection
          |
          v
บันทึก active_connections["6710301001"]
          |
          v
broadcast "เชื่อมต่อเข้าสู่ระบบ" ให้ทุกคน
```

### 8.4 Flow เมื่อส่งข้อความ

```python
data = await websocket.receive_text()
await manager.broadcast(f"[{student_id}]: {data}")
```

ผู้ส่งจะได้รับข้อความ broadcast กลับด้วย เพราะ connection ของผู้ส่งก็อยู่ใน dictionary

### 8.5 Flow เมื่อตัดการเชื่อมต่อ

เมื่อ `receive_text()` เจอ `WebSocketDisconnect`:

1. ลบ student ID
2. broadcast ข้อความออกจากระบบให้คนที่ยังอยู่

### 8.6 ข้อจำกัดที่ควรรู้

- ถ้าสอง browser ใช้ `student_id` ซ้ำ connection ใหม่จะเขียนทับค่าเดิมใน dictionary แต่ connection เก่าอาจยังเปิดอยู่และไม่ได้อยู่ในชุด broadcast แล้ว
- `broadcast()` ไม่มี `try/except` ราย connection ถ้าการส่งไป connection หนึ่งล้ม อาจทำให้รอบ broadcast นั้นเกิด exception
- ข้อมูลอยู่ใน memory เท่านั้น restart server แล้วรายชื่อหาย
- ไม่มี authentication และไม่มีฐานข้อมูลประวัติข้อความ
- `asyncio` ถูก import แต่ไม่ได้เรียกใช้โดยตรงในไฟล์นี้

## 9. `chat-hello/client.py` และ `client2.py`

### 9.1 สิ่งที่ทำเหมือนกัน

ทั้งคู่:

- รับ `student_id` จาก Terminal
- รับ IP central server หรือใช้ `localhost`
- สร้างหน้า HTML/CSS/JavaScript
- JavaScript ต่อ `ws://{server_ip}:8088/ws/{student_id}`
- `ws.onmessage` เพิ่มข้อความใน `<div id="messages">`
- `sendMessage()` เรียก `ws.send(input.value)`
- เปิด browser อัตโนมัติ

### 9.2 สิ่งที่ต่างกัน

| ไฟล์ | Local HTTP port จริง | Browser URL จริง | WebSocket port จริง |
|---|---:|---|---:|
| `client.py` | 8001 | `http://127.0.0.1:8001` | 8088 |
| `client2.py` | 8002 | `http://127.0.0.1:8002` | 8088 |

### 9.3 ความไม่สอดคล้องของข้อความแสดง port

ใน `client2.py` มีจุดที่ต้องสังเกต:

```html
เชื่อมต่อไปยัง Server: ws://{server_ip}:8000/ws/{student_id}
```

แต่ JavaScript เชื่อมจริงด้วย:

```javascript
new WebSocket("ws://{server_ip}:8088/ws/{student_id}")
```

ดังนั้น **ข้อความบนหน้าจอแสดง port 8000 แต่ connection จริงใช้ port 8088** คู่มือนี้บันทึกตามโค้ดจริงและไม่ได้แก้ Python file

### 9.4 Expected behavior

เมื่อเปิด client แรก:

```text
[System]: รหัสนักศึกษา 6710301001 เชื่อมต่อเข้าสู่ระบบ
```

เมื่อ client สองเข้ามา ทุกหน้าจอที่เชื่อมอยู่ควรเห็น system message ของ client สอง จากนั้นถ้า client แรกส่ง `Hello` ทุกคนควรเห็น:

```text
[6710301001]: Hello
```

---

# Part E — Rocket Real-time System

## 10. สถาปัตยกรรม Rocket

```text
student.py (:8002)          student2.py (:8003)
Browser Controller A        Browser Controller B
       | CONTROL JSON              | CONTROL JSON
       +------------ WebSocket :8088 ------------+
                                                   v
                                         rocket/main.py
                                   RocketSpaceManager + state
                                                   |
                           INIT / SPAWN / UPDATE / DESPAWN
                                                   v
                                       dashboard.py (:8001)
                                      Browser Canvas 800x600
```

Port 8001/8002/8003 เป็น local HTTP servers ที่ส่งหน้าเว็บ ส่วน port 8088 เป็น WebSocket central server

## 11. `Week5/rocket/main.py` — Rocket Central Server

### 11.1 ขอบเขตสนามและ State

```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
```

Manager เก็บ dictionary สองชุด:

| ตัวแปร | เก็บอะไร |
|---|---|
| `connections` | WebSocket ของทุก client รวม dashboard |
| `rockets` | state ของจรวดจริง ไม่รวม dashboard |

State ของจรวดหนึ่งลำ:

```json
{
  "x": 400.0,
  "y": 300.0,
  "angle": 0,
  "color": "hsl(..., 80%, 60%)"
}
```

ตำแหน่งเริ่มต้นคือกึ่งกลางสนาม `(400, 300)` สีมาจาก `hash(rocket_id) % 360`

### 11.2 Endpoint

```text
WebSocket /ws/{client_id}
```

ถ้า `client_id == "DASHBOARD"` server มองว่าเป็น dashboard และไม่สร้างจรวดให้ ถ้าเป็น ID อื่นจะสร้าง state จรวด

### 11.3 Message protocol

| `type` | ทิศทาง | เกิดเมื่อ | field สำคัญ |
|---|---|---|---|
| `INIT` | server → client ที่เพิ่งต่อ | connect สำเร็จ | `rockets`, `bounds` |
| `SPAWN` | server → ทุก client | controller ใหม่เข้า | `id`, `rocket` |
| `CONTROL` | controller → server | กดปุ่ม/ลูกศร | `action` |
| `UPDATE` | server → ทุก client | server เปลี่ยน state | `id`, `rocket` |
| `DESPAWN` | server → ทุก client | client disconnect | `id` |

ตัวอย่าง CONTROL:

```json
{"type": "CONTROL", "action": "ROTATE_LEFT"}
```

ตัวอย่าง UPDATE:

```json
{
  "type": "UPDATE",
  "id": "Rocket_101",
  "rocket": {"x": 408.0, "y": 300.0, "angle": 0, "color": "hsl(...)"}
}
```

### 11.4 การหมุน

```python
ROTATE_LEFT  -> angle = (angle - 15) % 360
ROTATE_RIGHT -> angle = (angle + 15) % 360
```

แต่ละครั้งหมุน 15 องศา และ `% 360` ทำให้มุมอยู่ในรอบ 0–359

ตัวอย่าง:

```text
เริ่ม 0°
กดซ้าย -> 345°
กดขวา -> 0°
```

### 11.5 การเคลื่อนที่ด้วย THRUST

```python
rad = math.radians(rocket["angle"])
new_x = rocket["x"] + 8 * math.cos(rad)
new_y = rocket["y"] + 8 * math.sin(rad)
```

- speed ต่อการกดหนึ่งครั้ง = 8 pixel
- 0° เพิ่ม x จึงเคลื่อนไปทางขวา
- 90° เพิ่ม y บน Canvas ซึ่งโดยพิกัดหน้าจอคือเคลื่อนลง
- 180° ลด x คือไปซ้าย
- 270° ลด y คือขึ้น

### 11.6 ล็อกขอบสนาม

```python
x = max(20, min(780, new_x))
y = max(20, min(580, new_y))
```

Padding 20 pixel ป้องกันตัวจรวดหลุดจากสนาม 800×600

### 11.7 Broadcast และ disconnect

`broadcast()` ใช้ `list(self.connections.values())` เพื่อ snapshot ค่า และจับ exception ราย connection แล้ว `pass` จึงทนต่อ connection ที่ส่งไม่สำเร็จได้ดีกว่า chat version แต่ connection เสียไม่ได้ถูกลบใน method นี้

เมื่อ controller หลุด:

1. ลบจาก `connections`
2. ลบจาก `rockets`
3. broadcast `DESPAWN`

ถ้า dashboard หลุด จะไม่มี rocket state ชื่อ `DASHBOARD` ให้ลบ แต่ server ยัง broadcast `DESPAWN` ID `DASHBOARD`; dashboard อื่นที่รับ event นี้ก็เพียงพยายามลบ key ที่ปกติไม่มี

### 11.8 ข้อควรระวัง input

โค้ดอ่าน `data["type"]` และ `data["action"]` ตรง ๆ ถ้า client ส่ง JSON ที่ไม่มี key เหล่านี้ อาจเกิด `KeyError` ซึ่งไม่ได้ถูกจับโดย `except WebSocketDisconnect`

## 12. `Week5/rocket/dashboard.py`

### 12.1 หน้าที่

ไฟล์นี้เปิด local FastAPI ที่ port 8001 ส่งหน้า Canvas และ WebSocket ต่อ central server ด้วย ID พิเศษ:

```javascript
new WebSocket("ws://{server_ip}:8088/ws/DASHBOARD")
```

### 12.2 การจัดการ event

```javascript
INIT              -> Object.assign(rockets, data.rockets)
SPAWN หรือ UPDATE -> rockets[data.id] = data.rocket
DESPAWN           -> delete rockets[data.id]
```

Counter ใช้ `Object.keys(rockets).length` จึงนับจำนวน state จรวดบน browser

### 12.3 การวาด

- Canvas ขนาด 800×600
- `drawGrid(50)` วาด grid ทุก 50 pixel
- `drawRocket(...)` translate ไปตำแหน่งและ rotate ตามมุม
- เขียน ID ไว้เหนือจรวด
- `requestAnimationFrame(render)` วาดซ้ำตามรอบ render ของ browser

WebSocket event มีหน้าที่อัปเดต state ส่วน animation loop มีหน้าที่วาด state ล่าสุด ทั้งสองส่วนจึงแยกกัน

### 12.4 Port

```text
Local dashboard HTTP: http://127.0.0.1:8001
Central WebSocket:     ws://SERVER_IP:8088/ws/DASHBOARD
```

## 13. `rocket/student.py` และ `student2.py`

### 13.1 สิ่งที่เหมือนกัน

- รับ ID/ชื่อจรวด หรือ default `Rocket_101`
- รับ IP server หรือ default `localhost`
- สร้างหน้า controller
- ปุ่มซ้ายส่ง `ROTATE_LEFT`
- ปุ่มขวาส่ง `ROTATE_RIGHT`
- ปุ่ม THRUST ส่ง `THRUST`
- Keyboard ArrowLeft/ArrowRight/ArrowUp ทำงานเหมือนปุ่ม
- ส่งเฉพาะเมื่อ `ws.readyState === WebSocket.OPEN`

### 13.2 สิ่งที่ต่างกัน

| ไฟล์ | Local HTTP port จริง | URL ที่เปิดจริง | WebSocket server |
|---|---:|---|---|
| `student.py` | 8002 | `http://127.0.0.1:8002` | `SERVER:8088` |
| `student2.py` | 8003 | `http://127.0.0.1:8003` | `SERVER:8088` |

สองไฟล์เกือบเหมือนกัน จุดประสงค์คือเปิด controller สองหน้าบนเครื่องเดียวโดยไม่ชน local port

### 13.3 ความไม่สอดคล้องของ comment เรื่อง port

ใน `student.py` comment เขียนว่า “เปิดเบราว์เซอร์ไปที่ Port 8001” แต่ code เปิดและรันจริงที่ **8002**

ใน `student2.py` comment ก็เขียนว่า “เปิดเบราว์เซอร์ไปที่ Port 8001” แต่ code เปิดและรันจริงที่ **8003**

ให้เชื่อค่าที่ถูกส่งเข้า `webbrowser.open(...)` และ `uvicorn.run(..., port=...)` เป็นพฤติกรรมจริง คู่มือนี้ไม่แก้ source code

### 13.4 Expected behavior

1. เปิด dashboard: Active Rockets = 0
2. เปิด `student.py`: จรวดแรกเกิดกลางสนาม และ counter = 1
3. เปิด `student2.py` ด้วย ID ไม่ซ้ำ: จรวดที่สองเกิด และ counter = 2
4. กด Left/Right: จรวด ID นั้นหมุนครั้งละ 15°
5. กด THRUST: จรวดขยับครั้งละ 8 pixel ตามมุม
6. ปิด controller: จรวดนั้นหายจาก dashboard หลัง `DESPAWN`

---

## 14. ตาราง Port และ Endpoint ทั้ง Week 5

### 14.1 HTTP/FastAPI Labs

ทั้งสามไฟล์พื้นฐานต้องรัน **ทีละไฟล์** หากใช้ port 8000 เดียวกัน

| App | Port ตามคำสั่ง | Endpoints |
|---|---:|---|
| `fastapi_basic_lab.py` | 8000 (Uvicorn default) | `/`, `/items/{item_id}`, `/users`, `/register/student`, `/docs` |
| `fastapi_async_basic_lab.py` | 8000 | `/sync-delay`, `/async-delay`, `/concurrent-tasks`, `/docs` |
| `fastapi_async_external_api_lab.py` | 8000 | `/single-fetch`, `/sequential-fetch`, `/concurrent-fetch`, `/docs` |

### 14.2 Chat

| Process | HTTP port | WebSocket target |
|---|---:|---|
| `chat-hello/main.py` | 8088 และมี GET `/` | `/ws/{student_id}` บน 8088 |
| `chat-hello/client.py` | 8001 | central server 8088 |
| `chat-hello/client2.py` | 8002 | central server 8088 |

### 14.3 Rocket

| Process | HTTP port | WebSocket target |
|---|---:|---|
| `rocket/main.py` | ไม่มี HTTP route ในโค้ด; Uvicorn ฟัง 8088 เพื่อ WebSocket | `/ws/{client_id}` |
| `rocket/dashboard.py` | 8001 | `/ws/DASHBOARD` บน 8088 |
| `rocket/student.py` | 8002 | `/ws/{student_id}` บน 8088 |
| `rocket/student2.py` | 8003 | `/ws/{student_id}` บน 8088 |

> Chat และ Rocket central server ใช้ port 8088 เหมือนกัน จึงไม่สามารถเปิดทั้งสอง server บน IP/เครื่องเดียวกันพร้อมกันที่ port เดิมได้ ควรรันแยกแล็บ

---

## 15. วิธีติดตั้งและรัน

### 15.1 ติดตั้ง package

จาก repository root:

```bash
python -m pip install fastapi uvicorn httpx
```

`webbrowser`, `asyncio`, `time`, `typing` และ `math` มาจาก Python standard library ไม่ต้อง `pip install`

### 15.2 รัน FastAPI Basic Lab

Terminal:

```bash
cd Week5
python -m uvicorn fastapi_basic_lab:app --reload
```

เปิด:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

ทดสอบ URL ตัวอย่าง:

```text
http://127.0.0.1:8000/items/123
http://127.0.0.1:8000/users?username=Alice&age=21
```

POST ให้ใช้ `/docs` แล้วกด **Try it out** ที่ `/register/student`

### 15.3 รัน Async Basic Lab

หยุด server เดิมด้วย `Ctrl+C` ก่อน เพราะใช้ port 8000 เหมือนกัน:

```bash
cd Week5
python -m uvicorn fastapi_async_basic_lab:app --reload --port 8000
```

เปิด:

```text
http://127.0.0.1:8000/sync-delay
http://127.0.0.1:8000/async-delay
http://127.0.0.1:8000/concurrent-tasks
```

### 15.4 รัน External API Lab

```bash
cd Week5
python -m uvicorn fastapi_async_external_api_lab:app --reload --port 8000
```

เปิด `http://127.0.0.1:8000/docs` แล้วทดลองทั้ง 3 endpoint เปรียบเทียบ `elapsed_seconds` และ `fallback_activated`

### 15.5 รัน Chat Lab

ใช้ 3 Terminal

Terminal 1 — central server:

```bash
cd Week5/chat-hello
python -m uvicorn main:app --host 0.0.0.0 --port 8088 --reload
```

Terminal 2 — client แรก:

```bash
cd Week5/chat-hello
python client.py
```

Terminal 3 — client ที่สอง:

```bash
cd Week5/chat-hello
python client2.py
```

ตอน prompt:

- กรอก student ID ไม่ซ้ำกัน
- ถ้าทุก process อยู่เครื่องเดียวกัน กด Enter เพื่อใช้ `localhost`
- ถ้า central server อยู่เครื่องอื่น ให้กรอก IP เครื่อง server และตรวจ firewall/network

ตรวจสถานะ central server:

```text
http://127.0.0.1:8088/
```

### 15.6 รัน Rocket Lab

หยุด Chat central server ก่อน เพราะชน port 8088 จากนั้นใช้ 4 Terminal

Terminal 1 — Rocket central server:

```bash
cd Week5/rocket
python -m uvicorn main:app --host 0.0.0.0 --port 8088 --reload
```

Terminal 2 — Dashboard:

```bash
cd Week5/rocket
python dashboard.py
```

Terminal 3 — Controller 1:

```bash
cd Week5/rocket
python student.py
```

Terminal 4 — Controller 2:

```bash
cd Week5/rocket
python student2.py
```

กรอก ID ของ controller ให้ไม่ซ้ำกัน เช่น `Rocket_A` และ `Rocket_B`

### 15.7 ตรวจ syntax โดยไม่แก้ไฟล์

จาก repository root:

```bash
python -m py_compile Week5/fastapi_basic_lab.py Week5/fastapi_async_basic_lab.py Week5/fastapi_async_external_api_lab.py Week5/chat-hello/main.py Week5/chat-hello/client.py Week5/chat-hello/client2.py Week5/rocket/main.py Week5/rocket/dashboard.py Week5/rocket/student.py Week5/rocket/student2.py
```

---

## 16. Pitfalls และ Debug Checklist

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ/แนวทาง |
|---|---|---|
| `ModuleNotFoundError: fastapi` | ยังไม่ได้ติดตั้ง | `python -m pip install fastapi uvicorn` |
| `ModuleNotFoundError: httpx` | ขาด HTTPX | `python -m pip install httpx` |
| `Address already in use` | port 8000/8001/8002/8088 ถูกใช้อยู่ | หยุด process แล็บเดิมก่อน |
| `/items/abc` ได้ error | `item_id` ต้องเป็น int | ใช้ `/items/123` |
| `/users` ได้ validation error | ขาด `username` | เพิ่ม `?username=Alice` |
| POST register ไม่ผ่าน | JSON ขาด field หรือ type ผิด | ตรวจ `student_id`, `nickname`, `gpa` |
| External API ได้ mock | upstream ล้ม/timeout/rate-limit | ดู log และ `fallback_activated` |
| Sequential บางครั้งเร็วกว่า/ช้ากว่าที่เดา | network latency จริงไม่คงที่ | ทดลองหลายรอบและดู elapsed |
| Browser chat เปิดแต่ไม่มีข้อความ | central server ไม่เปิด/IP ผิด/port ถูก block | ตรวจ server 8088 และ URL WebSocket |
| `client2.py` แสดง `:8000` | ข้อความ HTML ไม่ตรง JavaScript | connection จริงใน JS ใช้ 8088 |
| เปิด client สองตัวด้วย ID เดียว | dictionary key ถูกเขียนทับ | ใช้ ID ไม่ซ้ำ |
| Dashboard ไม่มีจรวด | Rocket server/controller ไม่เชื่อม | เปิด server → dashboard → controller |
| กดปุ่มแล้วไม่ขยับ | WebSocket ยังไม่ `OPEN` หรือ server ไม่ตอบ | ตรวจ browser console และ central server |
| จรวดเดิน “ลง” ที่ 90° | Canvas เพิ่มค่า y ลงด้านล่าง | เป็นระบบพิกัดหน้าจอปกติ |
| จรวดหยุดที่ขอบ | server clamp padding 20 | เป็น behavior ที่ตั้งใจไว้ |
| Dashboard เปิด port 8001 ไม่ได้ | chat `client.py` หรือ app อื่นยังใช้ 8001 | ปิดแล็บเดิมก่อน |
| Student เปิด port 8002 ไม่ได้ | chat `client2.py` หรือ app อื่นยังใช้ 8002 | ปิดแล็บเดิมก่อน |

### Port display inconsistencies ที่ต้องจำ

1. `chat-hello/client2.py`: ข้อความหน้าเว็บบอก WS port 8000 แต่ JavaScript ใช้ 8088 จริง
2. `rocket/student.py`: comment บอก browser port 8001 แต่ code ใช้ 8002 จริง
3. `rocket/student2.py`: comment บอก browser port 8001 แต่ code ใช้ 8003 จริง

อย่าแก้โค้ดเพียงเพราะคู่มือชี้จุดนี้ หากเป็นงานส่งควรตรวจ requirement ของอาจารย์ก่อน

---

## 17. ตารางเปรียบเทียบแนวคิดสำคัญ

### 17.1 `def` กับ `async def`

| ประเด็น | `def` | `async def` |
|---|---|---|
| object/function | function ปกติ | coroutine function |
| ใช้ `await` ได้ไหม | ไม่ได้ | ได้ |
| FastAPI execution | ปกติรันใน thread pool | รันบน event loop |
| เหมาะกับ | sync library/งานสั้น หรือจัดการ blocking อย่างเหมาะสม | งาน I/O ที่ library รองรับ async |
| ตัวอย่าง | `sync_delay()` | `async_delay()` |

### 17.2 `time.sleep()` กับ `asyncio.sleep()`

| คำสั่ง | ผลระหว่างรอ |
|---|---|
| `time.sleep(3)` | block thread |
| `await asyncio.sleep(3)` | suspend coroutine และคืน control ให้ event loop |

### 17.3 Sequential กับ Concurrent

| แบบ | เริ่มงานถัดไปเมื่อไร | เวลาคร่าว ๆ | ตัวอย่าง |
|---|---|---|---|
| Sequential | งานก่อนหน้าจบ | ผลรวมเวลารอ | `/sequential-fetch` |
| Concurrent | เริ่มหลายงานก่อนรอครบ | ใกล้งานช้าที่สุด | `/concurrent-tasks`, `/concurrent-fetch` |

### 17.4 Text กับ JSON บน WebSocket

| ระบบ | รับ | ส่ง | รูปแบบ |
|---|---|---|---|
| Chat | `receive_text()` | `send_text()` | string |
| Rocket | `receive_json()` | `send_json()` | dictionary/JSON protocol |

### 17.5 Chat Manager กับ Rocket Manager

| ประเด็น | Chat | Rocket |
|---|---|---|
| connection key | student ID | rocket/client ID |
| state เพิ่มเติม | ไม่มี | x, y, angle, color |
| broadcast | text | JSON event |
| Dashboard พิเศษ | ไม่มี | ID `DASHBOARD` |
| send error handling | ไม่มี try/except ราย connection | catch exception แล้ว pass |

---

## 18. Practical Labs

> ทุก Lab ให้ทำนายผลก่อนรัน แล้วจึงทดลองจริง การแก้ source เพื่อทดลองควรทำบนสำเนาหรือ revert ก่อนส่งงาน

### Lab 1 — Path, Query และ Validation

**วัตถุประสงค์:** แยกแหล่งข้อมูลของ parameter ได้

1. รัน `fastapi_basic_lab.py`
2. เรียก `/items/10`, `/items/-5`, `/items/abc`
3. เรียก `/users?username=Bai`
4. เรียก `/users?username=Bai&age=abc`
5. จดว่า request ใดเข้า function และ request ใดถูก validation ปฏิเสธ

**เกณฑ์ผ่าน:** อธิบายได้ว่า path/query field ไหนถูกแปลงเป็น `int`

### Lab 2 — GPA Boundary

POST นักศึกษาด้วย GPA:

```text
1.99, 2.00, 2.01
```

ทำนาย `academic_probation_alert` ของแต่ละค่า

**เฉลยแนวคิด:** เงื่อนไขคือ `< 2.00` ดังนั้น true เฉพาะ 1.99

### Lab 3 — Blocking เทียบ Non-blocking

1. เปิด `/sync-delay` และ `/async-delay`
2. ดูเวลาของ request เดี่ยว
3. ทดลองเปิดหลาย request ใกล้กัน
4. อธิบายว่าทำไม “แต่ละ request ใช้ ~3 วินาที” ไม่ได้แปลว่าพฤติกรรม resource เหมือนกัน

### Lab 4 — ทำนาย `gather()`

จาก wait time 2, 3, 1 วินาที ตอบก่อนรัน:

1. งานใด print Finished ก่อน
2. `results_received` เรียงแบบใด
3. เวลารวมใกล้เท่าไร

**เฉลย:** Gamma → Alpha → Beta; results Alpha/Beta/Gamma; รวม ~3 วินาที

### Lab 5 — Resilience ของ External API

1. เรียกทั้ง 3 endpoint อย่างละหลายรอบ
2. บันทึก `elapsed_seconds`
3. บันทึก `fallback_activated`
4. เปรียบเทียบ sequential กับ concurrent
5. อธิบายว่าทำไมผลแต่ละรอบอาจไม่เหมือนกัน

### Lab 6 — Chat Broadcast

1. เปิด client สอง ID
2. ให้แต่ละฝั่งส่งข้อความ
3. เปิด `GET /` ของ central server และดู `connected_students`
4. ปิด client หนึ่งตัว
5. ตรวจ system message และรายชื่ออีกครั้ง

**เกณฑ์ผ่าน:** ทุก client เห็นข้อความเดียวกันและอธิบาย flow ผ่าน manager ได้

### Lab 7 — ตรวจ Port ด้วยการอ่านโค้ด

โดยไม่แก้ไฟล์ ให้กรอกตาราง:

| ไฟล์ | Port ในข้อความ/comment | Port ที่ code ใช้จริง |
|---|---:|---:|
| `chat-hello/client2.py` WebSocket | ? | ? |
| `rocket/student.py` local HTTP | ? | ? |
| `rocket/student2.py` local HTTP | ? | ? |

**เฉลย:** 8000→8088, 8001→8002, 8001→8003

### Lab 8 — Rocket Geometry

เริ่มที่ `(400, 300, 0°)` ทำนายหลัง:

1. THRUST หนึ่งครั้ง
2. ROTATE_RIGHT หกครั้ง
3. THRUST หนึ่งครั้ง

แนวคิด:

- ครั้งแรกได้ประมาณ `(408, 300)`
- หมุนขวา 6 ครั้งได้ 90°
- thrust ที่ 90° เพิ่ม y ประมาณ 8 จึงได้ `(408, 308)`

### Lab 9 — Multi-Rocket

1. เปิด dashboard
2. เปิด controller สอง ID
3. หมุนและขยับคนละทิศ
4. ตรวจว่า UPDATE ของ ID หนึ่งไม่แก้ state อีก ID
5. ปิดหนึ่ง controller และตรวจ DESPAWN

### Lab 10 — ออกแบบ Message ใหม่บนกระดาษ

ไม่ต้องแก้โค้ด ออกแบบ event `RESET` เพื่อย้ายจรวดกลับ `(400,300,0)` ตอบว่า:

- JSON จาก controller ควรหน้าตาอย่างไร
- server ต้องตรวจที่ส่วนไหน
- server ควร broadcast event ใดหลัง reset
- dashboard ต้องแก้หรือไม่ หากได้รับ UPDATE รูปแบบเดิม

คำตอบที่สมเหตุผลคือส่ง `{"type":"CONTROL","action":"RESET"}` ให้ server เพิ่ม branch แล้ว broadcast `UPDATE`; dashboard ไม่ต้องเพิ่ม protocol ใหม่

---

## 19. คำถามแนวสอบพร้อมคำตอบสั้น

### 19.1 FastAPI รู้ได้อย่างไรว่า `item_id` ต้องเป็นเลข

จาก type hint `item_id: int` และ FastAPI ทำ parsing/validation ก่อนเรียก function

### 19.2 `username` กับ `age` เป็น query parameter เพราะอะไร

เพราะไม่ได้อยู่ใน path และเป็น parameter ธรรมดาของ GET function โดย `username` required ส่วน `age` default 18

### 19.3 Pydantic model มีหน้าที่อะไร

กำหนด schema ของ request body ช่วย parse, แปลงชนิด และ validation ข้อมูล

### 19.4 ทำไม `/async-delay` ยังใช้ 3 วินาที

Async ไม่ได้ลบเวลารอ แต่ทำให้ coroutine ยอมคืน control ระหว่างรอ

### 19.5 `gather()` ใน Async Basic ใช้เวลาประมาณเท่าไร

ประมาณ 3 วินาที เพราะรอ task ช้าที่สุด ไม่ใช่ผลรวม 6 วินาที

### 19.6 Concurrent เหมือน parallel เสมอหรือไม่

ไม่เสมอ ในแล็บนี้เป็น cooperative concurrency ของงานรอ I/O บน event loop

### 19.7 `raise_for_status()` ทำอะไร

ทำให้ HTTP response ที่เป็น error status ก่อ exception เพื่อเข้า error handling

### 19.8 Fallback ช่วยอะไร

ทำให้ endpoint ยังคืนข้อมูลที่มีรูปแบบใช้ต่อได้เมื่อ upstream unavailable

### 19.9 ถ้า external API หนึ่งล้ม `/concurrent-fetch` พังทั้งหมดไหม

ตามโค้ดไม่พังจาก `httpx.HTTPError` นั้น เพราะ `fetch_safely()` จับ error ของแต่ละงานและคืน mock

### 19.10 WebSocket ต่างจาก HTTP request อย่างไร

WebSocket เปิด connection สองทางค้างไว้ ส่งข้อมูลได้หลายครั้งโดยไม่ต้องสร้าง request-response ใหม่ทุกข้อความ

### 19.11 ทำไมต้อง `await websocket.accept()`

เพื่อยอมรับ WebSocket handshake ก่อนเริ่มรับส่งข้อมูล

### 19.12 Broadcast คืออะไร

การวนส่งข้อความ/event เดียวไปยังทุก active connection

### 19.13 ผู้ส่ง chat เห็นข้อความตัวเองหรือไม่

เห็น เพราะ broadcast รวม connection ของผู้ส่งด้วย

### 19.14 Rocket dashboard มีจรวดของตัวเองไหม

ไม่มี เพราะ ID `DASHBOARD` ทำให้ `is_dashboard=True` และ server ไม่สร้าง rocket state

### 19.15 INIT กับ SPAWN ต่างกันอย่างไร

INIT ส่ง snapshot จรวดทั้งหมดให้ client ที่เพิ่งต่อ ส่วน SPAWN แจ้งทุก client ว่ามีจรวดใหม่หนึ่งลำ

### 19.16 ทำไมต้องใช้ `% 360`

เพื่อ wrap มุมให้อยู่ในวงรอบ เช่น -15° กลายเป็น 345°

### 19.17 ทำไมจรวดไม่ออกนอกจอ

Server clamp x ให้อยู่ 20–780 และ y ให้อยู่ 20–580

### 19.18 Dashboard วาดภาพต่อเนื่องได้อย่างไร

ใช้ `requestAnimationFrame(render)` ส่วน WebSocket อัปเดต object `rockets`

### 19.19 ถ้าใช้ ID ซ้ำมีปัญหาอะไร

Dictionary key เดิมถูกเขียนทับ ทำให้ state/connection ไม่ได้แยกผู้ใช้ตามที่คาด

### 19.20 Chat และ Rocket เปิดพร้อมกันได้ไหม

ถ้าอยู่ IP/เครื่องเดียวกันและต่างต้อง bind port 8088 จะชนกัน ต้องหยุดอีกระบบหรือเปลี่ยน port ให้สอดคล้องทั้ง server/client

---

## 20. Cheat Sheet ก่อนสอบ

```text
FastAPI()
    สร้าง ASGI application

@app.get("/path")
    สร้าง HTTP GET endpoint

@app.post("/path")
    สร้าง HTTP POST endpoint

@app.websocket("/ws/{id}")
    สร้าง WebSocket endpoint

BaseModel
    schema ของ JSON request body

def + time.sleep()
    งาน sync ที่ block thread ระหว่าง sleep

async def + await asyncio.sleep()
    coroutine ยอมคืน control ให้ event loop ระหว่างรอ

await asyncio.gather(a, b, c)
    รอหลาย awaitable แบบ concurrent
    ผลเรียงตาม input

async with httpx.AsyncClient()
    ใช้ HTTP client แบบ async และ cleanup เมื่อจบ

response.raise_for_status()
    เปลี่ยน HTTP error status เป็น exception

fallback
    ใช้ข้อมูลสำรองเมื่อ upstream ล้ม

await websocket.accept()
    รับ WebSocket connection

await websocket.receive_text()
    รอรับ string

await websocket.receive_json()
    รอรับ JSON

await websocket.send_text(...)
    ส่ง string

await websocket.send_json(...)
    ส่ง JSON

WebSocketDisconnect
    exception เมื่อ peer ตัด connection

Chat protocol
    ข้อความ text -> server เติม [student_id] -> broadcast

Rocket protocol
    CONTROL -> server คำนวณ state -> UPDATE -> dashboard วาด

Rocket events
    INIT / SPAWN / CONTROL / UPDATE / DESPAWN

Ports
    basic labs 8000
    central WebSocket 8088
    chat clients 8001, 8002
    rocket dashboard/controller 8001, 8002, 8003
```

---

## 21. Checklist ก่อนเข้าสอบ

- [ ] อธิบาย Method, path และ endpoint ได้
- [ ] แยก path parameter, query parameter และ request body ได้
- [ ] อธิบาย Pydantic validation ได้
- [ ] อธิบาย `def` กับ `async def` ใน FastAPI ได้
- [ ] แยก `time.sleep()` กับ `await asyncio.sleep()` ได้
- [ ] ทำนายเวลาและลำดับผลของ `gather()` ได้
- [ ] อธิบาย sequential กับ concurrent network requests ได้
- [ ] อธิบาย timeout, HTTP error และ fallback ได้
- [ ] อธิบาย HTTP กับ WebSocket ต่างกันอย่างไรได้
- [ ] วาด flow connect → receive → broadcast → disconnect ของ chat ได้
- [ ] อธิบาย dictionary ของ ConnectionManager ได้
- [ ] บอก message types ของ Rocket ได้ครบ
- [ ] คำนวณการหมุนและ THRUST เบื้องต้นได้
- [ ] อธิบาย clamp ขอบสนามได้
- [ ] บอก port จริงของทุก process ได้
- [ ] ระบุ port-display inconsistency ทั้ง 3 จุดได้
- [ ] อธิบายปัญหา ID ซ้ำและ port ชนได้

---

## 22. สรุปสุดท้าย

| ไฟล์ | จำสั้น ๆ |
|---|---|
| `fastapi_basic_lab.py` | GET/POST, path/query/body และ Pydantic |
| `fastapi_async_basic_lab.py` | blocking, non-blocking และ gather |
| `fastapi_async_external_api_lab.py` | HTTPX, timeout, sequential/concurrent และ fallback |
| `chat-hello/main.py` | central text WebSocket และ broadcast |
| `chat-hello/client.py` | หน้า chat local port 8001 |
| `chat-hello/client2.py` | หน้า chat local port 8002; ข้อความ port WS แสดงไม่ตรง |
| `rocket/main.py` | central JSON WebSocket, state และฟิสิกส์จรวด |
| `rocket/dashboard.py` | Canvas แสดงทุกจรวดที่ local port 8001 |
| `rocket/student.py` | controller แรก local port 8002 |
| `rocket/student2.py` | controller ที่สอง local port 8003 |

แก่นของ Week 5 คือการเลือกวิธีสื่อสารและวิธีรอให้ตรงกับงาน:

```text
ข้อมูลเป็นครั้ง ๆ                     -> HTTP GET/POST
รอ I/O โดยไม่อยาก block event loop   -> async/await
รอหลายแหล่งอิสระพร้อมกัน             -> asyncio.gather()
บริการภายนอกอาจล้ม                    -> timeout + error handling + fallback
ต้องรับส่งข้อมูลต่อเนื่องทันที         -> WebSocket
หลาย client ต้องเห็น state เดียวกัน    -> central manager + broadcast
```

ถ้าอธิบายเส้นทาง **Browser/Client → Endpoint → Manager/Logic → Broadcast/Response → Browser** ได้ ใบจะเห็นภาพรวมทั้ง FastAPI, WebSocket และ Rocket เป็นระบบเดียวกัน ไม่ใช่ชุดคำสั่งแยกกันค่ะ
