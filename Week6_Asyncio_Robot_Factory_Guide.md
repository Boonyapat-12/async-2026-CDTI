# Week 6 Asyncio Robot Factory Study Guide

คู่มือนี้เป็นภาษาไทยเป็นหลัก และอธิบายจาก **โค้ดจริงใน `Week6/robots.py` เท่านั้น** เพื่อให้เริ่มอ่านได้แม้ยังไม่คล่องเรื่อง `asyncio`, HTTP API หรือ `httpx`

> **เป้าหมายหลังอ่านจบ:** อธิบายได้ว่าโปรแกรมรีเซ็ตโรงงานอย่างไร หุ่นยนต์แต่ละตัวหยิบ `A -> B -> C` แบบเรียงลำดับอย่างไร เหตุใดหุ่นยนต์ทั้ง 4 ตัวจึงทำงานคืบหน้าพร้อมกันได้ และ `asyncio.gather()` กับ `httpx.AsyncClient` มีบทบาทอะไร

ไฟล์ต้นฉบับที่ใช้อ้างอิง:

```text
Week6/robots.py
```

ค่าจริงที่ต้องจำจากโค้ดปัจจุบัน:

```python
STUDENT_ID = "6710301033"
BASE_URL = "http://172.16.2.117:8088"
```

> คู่มือนี้ไม่สมมติรายละเอียดที่ไม่มีในไฟล์ เช่น เวลาหน่วงของแต่ละชิ้นส่วน รูปแบบ JSON response จาก Server หรือ URL ของ Dashboard หาก Server มีเอกสารแยกต่างหาก ให้ยึดเอกสารนั้นเพิ่มเติมค่ะ

---

## สารบัญ

1. ภาพรวมโจทย์
2. Use case และสิ่งที่ได้ฝึก
3. คำศัพท์สำคัญ
4. สถาปัตยกรรมและ Flow
5. Constants ทั้งหมด
6. API contract ที่มองเห็นจากโค้ด
7. `reset_factory()`
8. `grab_part()`
9. `run_robot_task()`
10. `main()`
11. จุดเริ่มโปรแกรมและ Error Handling
12. Sequential ภายในหุ่นยนต์แต่ละตัว
13. Concurrent ระหว่างหุ่นยนต์ 4 ตัว
14. เจาะลึก `asyncio.gather()`
15. เจาะลึก `httpx.AsyncClient`
16. Timing และ Expected Behavior
17. วิธีติดตั้ง ตรวจ และรัน
18. Network Caveats
19. Pitfalls และ Debug Checklist
20. แบบฝึกหัด
21. คำถามแนวสอบ
22. Checklist และ Cheat Sheet

---

# Part A — ปูพื้นฐาน

## 1. ภาพรวม Week 6 กำลังทำอะไร

โปรแกรม `robots.py` เป็น **HTTP client แบบ asynchronous** สำหรับสั่ง Robot Factory จำลองบน Server

งานหลักมี 2 ช่วง:

1. รีเซ็ตสถานะหุ่นยนต์ทั้งหมดของรหัสนักศึกษา `6710301033`
2. สั่งหุ่นยนต์ 4 ตัวให้หยิบชิ้นส่วน `A`, `B`, `C`

กฎสำคัญของโจทย์มีสองระดับ:

```text
ภายในหุ่นยนต์ตัวเดียว:
A ต้องเสร็จก่อน -> B ต้องเสร็จก่อน -> C
(Sequential)

ระหว่างหุ่นยนต์คนละตัว:
robot_1, robot_2, robot_3, robot_4 เริ่มคืบหน้าในช่วงเดียวกัน
(Concurrent)
```

นี่ไม่ใช่การให้ทั้ง 12 request ทำพร้อมกันแบบไร้ลำดับ เพราะถ้าทำอย่างนั้น `robot_1` อาจหยิบ `B` ก่อน `A` เสร็จ ซึ่งผิดเงื่อนไขของโค้ดปัจจุบัน

---

## 2. 🎯 Use case — เรียนแล้วใช้ทำอะไรได้

หลังอ่านบทนี้ ใบจะสามารถ:

- เขียน async client ที่ส่ง HTTP request หลายสายพร้อมกัน
- รักษาลำดับขั้นตอนภายใน workflow หนึ่งสาย
- ใช้ client เดียวซ้ำหลาย request เพื่อประหยัด overhead
- สร้าง URL path ด้วย Student ID และ Robot ID
- ส่ง JSON payload ด้วย `httpx`
- ตรวจ HTTP error ด้วย `raise_for_status()`
- อธิบายความแตกต่างระหว่าง sequential และ concurrent ได้

แนวคิดเดียวกันนำไปใช้กับงานจริงได้ เช่น:

- Robot แต่ละตัวต้องทำขั้นตอน `pick -> inspect -> pack` ตามลำดับ แต่ Robot หลายตัวทำงานพร้อมกัน
- ลูกค้าแต่ละคนต้องผ่าน `validate -> charge -> issue receipt` ตามลำดับ แต่รับลูกค้าหลายคนพร้อมกัน
- ดาวน์โหลดไฟล์แต่ละชุดตามลำดับภายในชุด แต่ดาวน์โหลดหลายชุดพร้อมกัน

---

## 3. คำศัพท์สำคัญ

| คำศัพท์ | ความหมายแบบง่าย | ตัวอย่างใน `robots.py` |
|---|---|---|
| Client | โปรแกรมที่ส่งคำขอ | `robots.py` |
| Server | ระบบที่รับคำสั่งและตอบกลับ | `172.16.2.117:8088` |
| HTTP request | คำขอที่ Client ส่งไป | `client.post(...)` |
| HTTP response | คำตอบที่ Server ส่งกลับ | ตัวแปร `response` |
| Endpoint | HTTP method + URL path ของงานหนึ่งอย่าง | `POST /student/.../reset` |
| Payload | ข้อมูลที่แนบไปกับ request | `{"part": "A"}` |
| JSON | รูปแบบข้อมูล key-value | `{"part": part}` |
| Coroutine function | ฟังก์ชันที่ประกาศด้วย `async def` | `grab_part()` |
| Coroutine object | สิ่งที่ได้เมื่อเรียก async function แต่ยังไม่ await | `run_robot_task(client, robot_id)` |
| Awaitable | สิ่งที่ใช้กับ `await` ได้ | coroutine และ Task |
| `await` | รอผลโดยคืน control ให้ Event Loop ระหว่างรอ I/O | `await client.post(...)` |
| Event Loop | ตัวจัดคิวและสลับงาน async | เริ่มโดย `asyncio.run(main())` |
| Sequential | ทำตามลำดับทีละขั้น | `A -> B -> C` ของ Robot เดียว |
| Concurrent | หลายงานคืบหน้าเหลื่อมกันในเวลาเดียวกัน | Robot 4 ตัวผ่าน `gather()` |
| Parallel | ทำงานจริงในเวลาเดียวกันบนหลายหน่วยประมวลผล | ไม่ใช่ประเด็นที่โค้ดนี้รับประกัน |
| I/O-bound | งานที่ใช้เวลาส่วนใหญ่รอภายนอก | รอ Network/Server ตอบ |
| Timeout | เวลารอสูงสุด | `timeout=10.0` |
| Exception | ข้อผิดพลาดที่ขัดจังหวะ flow ปกติ | `httpx.HTTPError` |

### Concurrent ไม่เท่ากับ Parallel

ในโปรแกรมนี้ concurrency เกิดเพราะเมื่อ Robot หนึ่งกำลังรอ HTTP response Event Loop สามารถสลับไปส่งหรือรอ request ของ Robot อื่นได้

```text
Concurrency = หลายงานคืบหน้าในช่วงเวลาเดียวกัน
Parallelism = หลายงานประมวลผลพร้อมกันจริงบนหลาย core/thread/process
```

`asyncio` หนึ่ง Event Loop ก็สร้าง concurrency สำหรับงาน I/O ได้ โดยไม่จำเป็นต้องสร้าง 4 threads หรือ 4 processes

---

# Part B — Architecture และข้อมูลคงที่

## 4. สถาปัตยกรรม Client–Server

```text
ผู้ใช้รัน Week6/robots.py
            |
            v
     asyncio.run(main())
            |
            v
  เปิด httpx.AsyncClient 1 ตัว
  base_url = http://172.16.2.117:8088
            |
            v
  POST /student/6710301033/reset
            |
            v
     รอ Reset สำเร็จ
            |
            v
      asyncio.gather(...)
       /       |       |       \
      v        v       v        v
  robot_1  robot_2  robot_3  robot_4
    A->B->C   A->B->C  A->B->C   A->B->C
       \       |       |       /
            v
  gather รอจน Robot ครบทุกตัว
            |
            v
  พิมพ์ elapsed time
            |
            v
  ออกจาก async with และปิด Client
```

### Flow ของ HTTP request

```text
robots.py
   |
   | POST + URL path + JSON (เฉพาะ grab)
   v
Robot Factory Server
   |
   | HTTP status + response body
   v
response.raise_for_status()
   |
   +-- status สำเร็จ --> ทำงานต่อ
   |
   +-- status ผิดพลาด --> โยน httpx.HTTPStatusError
```

---

## 5. Constants ทั้งหมด

โค้ดกำหนดค่าคงที่ 4 ตัว:

```python
STUDENT_ID = "6710301033"
BASE_URL = "http://172.16.2.117:8088"
PARTS = ["A", "B", "C"]
ROBOTS = ["robot_1", "robot_2", "robot_3", "robot_4"]
```

| Constant | Type | ค่าปัจจุบัน | หน้าที่ |
|---|---|---|---|
| `STUDENT_ID` | `str` | `"6710301033"` | แยกสถานะ/คำสั่งของนักศึกษาคนนี้ |
| `BASE_URL` | `str` | `"http://172.16.2.117:8088"` | Host และ port ของ Server |
| `PARTS` | `list[str]` | `A, B, C` | ลำดับชิ้นส่วนที่ Robot ต้องหยิบ |
| `ROBOTS` | `list[str]` | `robot_1` ถึง `robot_4` | Robot ที่ต้องสั่งงานพร้อมกัน |

### ทำไมลำดับใน `PARTS` สำคัญ

`for part in PARTS` อ่านสมาชิกจากซ้ายไปขวา จึงกำหนด workflow เป็น:

```text
index 0 = A
index 1 = B
index 2 = C
```

ถ้าเปลี่ยนเป็น `PARTS = ["C", "A", "B"]` Robot ทุกตัวก็จะพยายามหยิบ `C -> A -> B` ตามลำดับใหม่

### ทำไมลำดับใน `ROBOTS` สำคัญบ้าง

ลำดับนี้ใช้สร้าง awaitable ที่ส่งให้ `gather()` แม้งานจริงอาจเสร็จคนละลำดับ แต่ถ้าแต่ละ task มี return value `gather()` จะคืนผลตามลำดับ input คือ `robot_1`, `robot_2`, `robot_3`, `robot_4`

ในโค้ดปัจจุบัน `run_robot_task()` ไม่ได้ `return` ค่า ผลจากแต่ละงานจึงเป็น `None` และ `main()` ไม่ได้เก็บผลของ `gather()`

---

## 6. API Contract ที่เห็นได้จาก `robots.py`

> “Contract” ในส่วนนี้หมายถึงสิ่งที่ Client สร้างและคาดหวังจากโค้ดจริง ไม่ได้เดารูปแบบ response ที่ไฟล์ไม่ได้ระบุ

### 6.1 Reset Factory

Template:

```text
POST /student/{STUDENT_ID}/reset
```

ค่าจริง:

```text
POST http://172.16.2.117:8088/student/6710301033/reset
```

JSON payload:

```text
ไม่มี payload ที่ส่งจากโค้ดปัจจุบัน
```

Client behavior:

1. ส่ง POST
2. เรียก `raise_for_status()`
3. แปลง response body ด้วย `response.json()`
4. return JSON ที่ Server ตอบ

> รูปแบบ field ภายใน Reset response **ไม่ปรากฏใน `robots.py`** จึงไม่ควรท่อง JSON ที่เดาขึ้นเอง

### 6.2 Grab Part

Template:

```text
POST /student/{STUDENT_ID}/robot/{robot_id}/grab
```

ตัวอย่างค่าจริงสำหรับ `robot_1` หยิบ `A`:

```text
POST http://172.16.2.117:8088/student/6710301033/robot/robot_1/grab
```

JSON payload ที่ส่งจริง:

```json
{
  "part": "A"
}
```

ตัวอย่างครบทุก URL path:

```text
/student/6710301033/robot/robot_1/grab
/student/6710301033/robot/robot_2/grab
/student/6710301033/robot/robot_3/grab
/student/6710301033/robot/robot_4/grab
```

แต่ละ path ถูกเรียก 3 ครั้ง โดย payload เปลี่ยนตามลำดับ:

```json
{"part": "A"}
{"part": "B"}
{"part": "C"}
```

Client behavior หลัง Server ตอบสำเร็จ:

```python
return {"robot": robot_id, "part": part, "status": "success"}
```

ตัวอย่าง local return value:

```json
{
  "robot": "robot_1",
  "part": "A",
  "status": "success"
}
```

สำคัญมาก: dictionary นี้สร้างโดย Client เองหลัง `raise_for_status()` ไม่ใช่ JSON response body ที่อ่านจาก Server เพราะ `grab_part()` ไม่ได้เรียก `response.json()`

### 6.3 สรุป Endpoint และ Payload

| งาน | Method | Path | JSON body | Return ของ Python function |
|---|---|---|---|---|
| Reset | `POST` | `/student/6710301033/reset` | ไม่มีในโค้ด | `response.json()` จาก Server |
| Grab | `POST` | `/student/6710301033/robot/{robot_id}/grab` | `{"part": part}` | local dict `robot/part/status` |

ไม่มี `/api` นำหน้า path ในโค้ดนี้ อย่าเติมเองจากความเคยชินของ Lab อื่น

---

# Part C — อธิบายทุกฟังก์ชัน

## 7. `reset_factory(client)`

โค้ด:

```python
async def reset_factory(client: httpx.AsyncClient):
    response = await client.post(f"/student/{STUDENT_ID}/reset")
    response.raise_for_status()
    return response.json()
```

### 7.1 Parameter

| Parameter | Type hint | หน้าที่ |
|---|---|---|
| `client` | `httpx.AsyncClient` | ส่ง HTTP request โดยใช้ base URL และ connection pool ที่เปิดไว้ |

### 7.2 อธิบายทีละบรรทัด

```python
response = await client.post(f"/student/{STUDENT_ID}/reset")
```

- f-string แทน `{STUDENT_ID}` ด้วย `6710301033`
- path เริ่มด้วย `/` และถูกนำไปต่อกับ `base_url`
- `await` รอ HTTP response แบบไม่ block Event Loop ทั้งหมด

```python
response.raise_for_status()
```

- ถ้า status สำเร็จ โปรแกรมทำงานต่อ
- ถ้าเป็น HTTP error เช่น 4xx หรือ 5xx จะเกิด `httpx.HTTPStatusError`
- error นี้เป็น subclass ในกลุ่ม `httpx.HTTPError` จึงถูกจับที่ท้ายไฟล์ได้

```python
return response.json()
```

- แปลง JSON response เป็น Python object เช่น dictionary/list ตาม body จริง
- ถ้า body ไม่ใช่ JSON ที่ถูกต้อง อาจเกิด `ValueError`
- `ValueError` ถูกจับใน `if __name__ == "__main__"`

### 7.3 ทำไมต้อง Reset ก่อนจับเวลา

ใน `main()` reset เกิดก่อน `start_time = time.time()` ดังนั้นเวลา reset ไม่ถูกรวมใน elapsed time ของงาน Robot

Reset ก่อนเริ่มช่วยให้:

- ทุกการทดลองเริ่มจากสถานะที่ Server กำหนดหลัง reset
- ลดผลค้างจากการรันรอบก่อน
- เปรียบเทียบพฤติกรรมแต่ละรอบง่ายขึ้น

อย่างไรก็ตาม โค้ดปัจจุบัน reset เฉพาะก่อนเริ่ม ไม่ได้ reset ซ้ำหลังจบหรือใน `finally`

---

## 8. `grab_part(client, robot_id, part)`

โค้ด:

```python
async def grab_part(client: httpx.AsyncClient, robot_id: str, part: str):
    payload = {"part": part}
    url_path = f"/student/{STUDENT_ID}/robot/{robot_id}/grab"

    response = await client.post(url_path, json=payload)
    response.raise_for_status()
    return {"robot": robot_id, "part": part, "status": "success"}
```

### 8.1 Parameters

| Parameter | Type hint | ตัวอย่าง | หน้าที่ |
|---|---|---|---|
| `client` | `httpx.AsyncClient` | client จาก `main()` | ส่ง request |
| `robot_id` | `str` | `"robot_2"` | ระบุ Robot ใน URL path |
| `part` | `str` | `"B"` | ระบุชิ้นส่วนใน JSON payload |

### 8.2 สร้าง payload

```python
payload = {"part": part}
```

ถ้า `part == "B"` จะได้:

```python
{"part": "B"}
```

เมื่อส่งด้วย `json=payload` HTTPX จะ serialize dictionary เป็น JSON body และตั้ง header ที่เหมาะกับ JSON ให้

### 8.3 สร้าง URL path

```python
url_path = f"/student/{STUDENT_ID}/robot/{robot_id}/grab"
```

ถ้า `robot_id == "robot_2"` จะได้:

```text
/student/6710301033/robot/robot_2/grab
```

เมื่อรวมกับ `BASE_URL` จะเป็น:

```text
http://172.16.2.117:8088/student/6710301033/robot/robot_2/grab
```

### 8.4 ส่ง request

```python
response = await client.post(url_path, json=payload)
```

ระหว่างรอ Network/Server Event Loop สามารถให้ coroutine ของ Robot อื่นคืบหน้าได้ จุดนี้คือ async I/O ที่ทำให้ concurrency มีประโยชน์

### 8.5 ตรวจ status

```python
response.raise_for_status()
```

ทำให้ response error ไม่ถูกตีความว่า `success` ถ้าไม่เรียกบรรทัดนี้ โค้ดอาจสร้าง local dictionary ว่า success แม้ Server ตอบ 400 หรือ 500

### 8.6 Return value

```python
{"robot": robot_id, "part": part, "status": "success"}
```

Return นี้ยืนยันเพียงว่า request ผ่าน `raise_for_status()` ตามที่ Client เห็น ไม่ได้เก็บ response body ของ Server

ใน flow ปัจจุบัน `run_robot_task()` await ฟังก์ชันนี้ แต่ไม่ได้เก็บค่าที่ return จึงใช้เพื่อรอให้แต่ละขั้นสำเร็จเป็นหลัก

---

## 9. `run_robot_task(client, robot_id)`

โค้ด:

```python
async def run_robot_task(client: httpx.AsyncClient, robot_id: str):
    for part in PARTS:
        await grab_part(client, robot_id, part)
```

> ในไฟล์จริง บรรทัด `await grab_part(...)` เยื้องมากกว่าระดับมาตรฐานเล็กน้อย แต่ยังอยู่ใน block ของ `for` และ Python ยอมรับได้ ตราบใดที่ indentation ภายใน block สอดคล้องกัน

### 9.1 หน้าที่

ดูแล workflow ของ Robot **หนึ่งตัว** ตั้งแต่ `A` ถึง `C`

ตัวอย่าง `robot_3`:

```text
run_robot_task(client, "robot_3")
       |
       v
POST grab A -> await จนสำเร็จ
       |
       v
POST grab B -> await จนสำเร็จ
       |
       v
POST grab C -> await จนสำเร็จ
       |
       v
return None โดยปริยาย
```

### 9.2 ทำไม loop นี้เป็น Sequential

เพราะมี `await` อยู่ในแต่ละรอบ:

```python
for part in PARTS:
    await grab_part(...)
```

Python จะไม่เลื่อนไป part ถัดไปของ Robot ตัวเดิมจน `grab_part()` รอบปัจจุบันจบ

จึงรับประกันลำดับในฝั่ง Client ว่า:

```text
A response สำเร็จ -> จึงส่ง B
B response สำเร็จ -> จึงส่ง C
```

### 9.3 ถ้า `A` fail จะเกิดอะไร

หาก `grab_part(..., "A")` โยน exception:

- loop ของ Robot ตัวนั้นหยุดทันที
- `B` และ `C` ของ Robot ตัวนั้นไม่ถูกส่งจาก coroutine นี้
- exception ไหลออกจาก `run_robot_task()` ไปยัง `gather()`
- `main()` ไม่ได้จับภายใน จึงไหลไปยัง error handler ระดับบน

พฤติกรรมของ Robot งานอื่นเมื่อ `gather()` เจอ exception ต้องคิดอย่างระวัง: ไม่ควรสรุปง่าย ๆ ว่าทุกงานจะถูก rollback หรือ cancel บน Server เพราะ HTTP request ที่ส่งออกไปแล้วอาจทำงานต่อ

### 9.4 Return value ปัจจุบัน

ฟังก์ชันไม่มี `return` ชัดเจน จึงเท่ากับ:

```python
return None
```

ถ้าเก็บผลจาก gather จะได้แนวคิดเป็น:

```python
[None, None, None, None]
```

เมื่อทุก Robot สำเร็จ แต่โค้ดปัจจุบันไม่ได้เก็บ list นี้

---

## 10. `main()`

โค้ดสำคัญ:

```python
async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("Resetting Factory...")
        await reset_factory(client)

        start_time = time.time()
        print("Starting Async Robot Operation...")

        robot_tasks = [run_robot_task(client, robot_id) for robot_id in ROBOTS]
        await asyncio.gather(*robot_tasks)

        elapsed_time = time.time() - start_time
        print(f"Finished all tasks in {elapsed_time:.2f} seconds.")
```

### 10.1 เปิด Async Client

```python
async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
```

ค่าที่กำหนด:

| Option | ค่า | ความหมาย |
|---|---:|---|
| `base_url` | `http://172.16.2.117:8088` | ใช้ต่อกับ relative URL path |
| `timeout` | `10.0` | ค่า timeout เริ่มต้นของ request ที่ client นี้ส่ง |

`async with` ทำให้ปิด client/connection pool เมื่อออกจาก block ทั้งกรณีสำเร็จและเกิด exception

### 10.2 Reset ก่อนเริ่ม

```python
print("Resetting Factory...")
await reset_factory(client)
```

จุดนี้เป็น sequential gate: ต้อง reset สำเร็จก่อนจึงเริ่ม Robot ทั้ง 4 ตัว

### 10.3 เริ่มจับเวลา

```python
start_time = time.time()
```

เวลาที่วัดครอบคลุมตั้งแต่ก่อนสร้าง/รัน Robot coroutines จน `gather()` รอครบ แต่ไม่รวม reset และไม่รวมเวลาสร้าง/ปิด client ทั้งหมด

### 10.4 สร้าง coroutine 4 ตัว

```python
robot_tasks = [run_robot_task(client, robot_id) for robot_id in ROBOTS]
```

ค่าทางแนวคิดใน list:

```text
run_robot_task(client, "robot_1")
run_robot_task(client, "robot_2")
run_robot_task(client, "robot_3")
run_robot_task(client, "robot_4")
```

ชื่อตัวแปร `robot_tasks` อาจทำให้เข้าใจว่าเป็น `asyncio.Task` objects แล้ว แต่จริง ๆ list comprehension นี้ได้ **coroutine objects** เพราะไม่ได้เรียก `asyncio.create_task()` โดยตรง

`asyncio.gather()` รับ coroutine เหล่านี้ได้ และจัด schedule ให้ทำงาน concurrent

### 10.5 แตก list ด้วย `*`

```python
await asyncio.gather(*robot_tasks)
```

ถ้าไม่ใส่ `*` จะเหมือนส่ง list เป็น argument เดียว ซึ่งไม่ใช่ awaitable ที่ `gather()` ต้องการในรูปแบบนี้

เครื่องหมาย `*` แปลงจาก:

```python
[coro1, coro2, coro3, coro4]
```

เป็นการส่ง argument:

```python
asyncio.gather(coro1, coro2, coro3, coro4)
```

### 10.6 รอครบทุก Robot

`await asyncio.gather(...)` ไม่จบใน success path จน coroutine ของ Robot ทั้ง 4 ตัวเสร็จ ดังนั้นเมื่อถึงบรรทัดคำนวณเวลา ตาม flow ปกติ request grab ทั้ง 12 ครั้งสำเร็จครบแล้ว

### 10.7 คำนวณและแสดงเวลา

```python
elapsed_time = time.time() - start_time
print(f"Finished all tasks in {elapsed_time:.2f} seconds.")
```

`.2f` แสดงทศนิยม 2 ตำแหน่ง เช่น:

```text
Finished all tasks in 3.27 seconds.
```

ตัวเลขข้างบนเป็นเพียงตัวอย่างรูปแบบ ไม่ใช่ผลที่ยืนยันจาก Server เพราะเวลาหน่วงจริงไม่ได้ระบุในไฟล์

> สำหรับการวัด elapsed time ในงานที่ต้องการความแม่นยำเชิงเทคนิค มักนิยม `time.perf_counter()` มากกว่า แต่คู่มือนี้อธิบายตามโค้ดปัจจุบันซึ่งใช้ `time.time()` และไม่ได้แก้ Python file

---

## 11. จุดเริ่มโปรแกรมและ Error Handling

โค้ด:

```python
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (httpx.HTTPError, ValueError) as error:
        print(f"Error: {error}")
```

### 11.1 `if __name__ == "__main__"`

ทำให้ block นี้รันเมื่อสั่ง:

```bash
python Week6/robots.py
```

แต่ไม่รันอัตโนมัติเมื่อ import ไฟล์เป็น module

### 11.2 `asyncio.run(main())`

ทำหน้าที่:

1. สร้าง Event Loop
2. รัน `main()` จนเสร็จ
3. จัดการปิด Event Loop

อย่าเขียนแค่ `main()` เพราะจะได้ coroutine object และเกิด warning ว่า coroutine was never awaited

### 11.3 Error ที่จับ

| Exception | ตัวอย่างสาเหตุ |
|---|---|
| `httpx.HTTPError` | ต่อ Server ไม่ได้, timeout, protocol error, HTTP status error หลัง `raise_for_status()` |
| `ValueError` | Reset response แปลง JSON ไม่ได้ |

เมื่อ error ที่จับได้เกิดขึ้น โปรแกรมพิมพ์:

```text
Error: <รายละเอียดจริง>
```

### 11.4 Error ที่ไม่ได้จับ

exception ชนิดอื่น เช่น bug จากโค้ดหรือ type ที่ไม่คาดคิดอาจแสดง traceback ตามปกติ การไม่จับ `Exception` กว้างเกินไปช่วยไม่ให้ bug ถูกซ่อน แต่ผู้เขียนต้องเข้าใจขอบเขตนี้

---

# Part D — หัวใจของ Concurrency

## 12. Sequential ภายใน Robot แต่ละตัว

แต่ละ Robot มี dependency chain:

```text
robot_1: A --------> B --------> C
robot_2: A --------> B --------> C
robot_3: A --------> B --------> C
robot_4: A --------> B --------> C
```

ในแต่ละแถว ลูกศรหมายถึง “ต้องรอ response สำเร็จก่อน”

เหตุผลที่ต้อง sequential อาจเป็นกฎของ Server/โรงงาน เช่น Robot ต้องประกอบชิ้นส่วนตามขั้นตอน แม้ `robots.py` ไม่ได้อธิบายเหตุผลทางธุรกิจเพิ่มเติม แต่โค้ดยืนยันลำดับชัดเจน

### รูปแบบที่ถูก

```python
for part in PARTS:
    await grab_part(client, robot_id, part)
```

### รูปแบบที่เปลี่ยน semantics

```python
await asyncio.gather(
    *(grab_part(client, robot_id, part) for part in PARTS)
)
```

รูปแบบหลังจะพยายามให้ A, B, C ของ Robot เดียวกัน concurrent ซึ่งไม่ตรงกับ “Sequential inside single robot” ของไฟล์ปัจจุบัน

---

## 13. Concurrent ระหว่าง Robot 4 ตัว

Robot คนละตัวเป็น workflow แยกกัน จึงส่งเข้า `gather()` พร้อมกันได้:

```text
เวลา --->

robot_1: [grab A] [grab B] [grab C]
robot_2: [grab A]----[grab B]--[grab C]
robot_3: [grab A]--[grab B]----[grab C]
robot_4: [grab A] [grab B]-----[grab C]
```

ความยาวกล่องเป็นภาพแนวคิดเท่านั้น เพราะไฟล์ไม่ได้บอก delay จริง

Event Loop ทำงานโดยประมาณ:

```text
1. เริ่ม coroutine robot_1 -> ส่ง A -> รอ network
2. สลับไป robot_2       -> ส่ง A -> รอ network
3. สลับไป robot_3       -> ส่ง A -> รอ network
4. สลับไป robot_4       -> ส่ง A -> รอ network
5. response ของตัวใดมาก่อน ตัวนั้นไปส่ง B ของตัวเอง
6. ทำต่อจนแต่ละตัวครบ C
7. gather จบเมื่อครบทั้ง 4 ตัว
```

คำว่า “พร้อมกัน” ในบทเรียนนี้ควรอธิบายอย่างแม่นยำว่า request มีโอกาส **คืบหน้าเหลื่อมกัน** ไม่ได้แปลว่าทุกบรรทัด Python ทำใน nanosecond เดียวกัน

---

## 14. เจาะลึก `asyncio.gather()`

บรรทัดหลัก:

```python
await asyncio.gather(*robot_tasks)
```

### 14.1 `gather()` ทำอะไรใน success path

- รับ awaitable หลายตัว
- schedule coroutine ให้ทำงาน concurrent
- รอจนทุกตัวสำเร็จ
- คืนผลตามลำดับ input

### 14.2 ลำดับเสร็จ vs ลำดับผล

สมมติ Robot เสร็จจริงตามลำดับ:

```text
robot_3 -> robot_1 -> robot_4 -> robot_2
```

ถ้าเก็บผล:

```python
results = await asyncio.gather(*robot_tasks)
```

`results` ยังเรียงตาม input `ROBOTS`:

```text
result ของ robot_1
result ของ robot_2
result ของ robot_3
result ของ robot_4
```

แต่ในโค้ดปัจจุบันแต่ละ coroutine return `None`

### 14.3 ถ้า Robot หนึ่งเกิด exception

ค่า default ของ `gather()` คือไม่ใช้ `return_exceptions=True` ดังนั้น exception จะถูกส่งออกมายังผู้ await

สิ่งที่ต้องระวัง:

- โปรแกรมจะไม่ถึงข้อความ `Finished all tasks...` ใน flow error นั้น
- error จะถูกส่งขึ้นไปยัง `try/except` ถ้าเป็นชนิดที่จับไว้
- อย่าสมมติว่า HTTP POST ที่ Server รับไปแล้วถูก rollback
- อย่าสมมติว่าการหยุดรอของ Client ทำให้สถานะ Server ย้อนกลับ

### 14.4 ทำไมไม่จำเป็นต้อง `create_task()` ก่อน

`gather()` รับ coroutine objects ได้โดยตรงและจัด schedule ให้ จึงใช้รูปแบบนี้ได้:

```python
coroutines = [run_robot_task(...) for ...]
await asyncio.gather(*coroutines)
```

ถ้าต้องการตั้งชื่อ Task ตรวจ `.done()` หรือ cancel เป็นรายตัว จึงค่อยพิจารณา `asyncio.create_task()`

---

## 15. เจาะลึก `httpx.AsyncClient`

### 15.1 ทำไมไม่ใช้ `httpx.Client`

`httpx.AsyncClient` มี method แบบ awaitable:

```python
response = await client.post(...)
```

จึงเปิดโอกาสให้ Event Loop ไปดู Robot อื่นระหว่างรอ I/O

ถ้าใช้ synchronous client ใน Event Loop การรอ network อาจ block thread และลดประโยชน์ของ concurrency

### 15.2 ทำไมใช้ Client เดียวร่วมกัน

`main()` สร้าง client ครั้งเดียวแล้วส่ง reference เดิมให้ทุกฟังก์ชัน

ข้อดี:

- reuse connection pool
- ลด overhead จากการสร้าง client ใหม่ 13 ครั้ง
- รวม `base_url` และ timeout ไว้จุดเดียว
- ปิด resource อย่างเป็นระบบด้วย `async with`
- รูปแบบ function แยกหน้าที่ชัดเจนและทดสอบด้วย transport จำลองได้ง่ายขึ้น

### 15.3 `base_url` ต่อกับ relative path

```python
base_url = "http://172.16.2.117:8088"
path = "/student/6710301033/reset"
```

ผล URL ที่ต้องการ:

```text
http://172.16.2.117:8088/student/6710301033/reset
```

### 15.4 `json=payload`

```python
await client.post(url_path, json={"part": "A"})
```

`json=` ต่างจาก `data=` เพราะบอก HTTPX ว่าต้องส่งข้อมูลแบบ JSON และ serialize Python dictionary ให้

### 15.5 Timeout 10 วินาที

```python
timeout=10.0
```

เป็นค่า timeout config ของ HTTPX สำหรับ request ผ่าน client นี้ ไม่ได้แปลว่าโปรแกรมทั้งชุดมีเวลารวมสูงสุด 10 วินาที

เหตุผล:

- Robot หนึ่งตัวมี 3 request sequential
- แต่ละ request อาจใช้เวลาของตนเอง
- reset ก็เป็นอีก request

ดังนั้น “10 วินาที” ไม่ควรถูกตีความว่า elapsed ทั้งโรงงานต้องต่ำกว่า 10 วินาทีเสมอ

### 15.6 `raise_for_status()`

HTTP request “ได้รับ response” ไม่ได้แปลว่า “สำเร็จ” เพราะ Server อาจตอบ 4xx/5xx

```python
response.raise_for_status()
```

ทำหน้าที่เปลี่ยน HTTP error status เป็น exception เพื่อหยุด success flow

---

# Part E — เวลาและผลที่คาด

## 16. Timing Model

ใน `robots.py` ไม่มีตาราง delay ของ A, B, C หรือ Robot แต่ละตัว จึงคำนวณตัวเลขตายตัวไม่ได้

ให้กำหนดเชิงสัญลักษณ์:

```text
T(r, A) = เวลาที่ Robot r ใช้ request A
T(r, B) = เวลาที่ Robot r ใช้ request B
T(r, C) = เวลาที่ Robot r ใช้ request C
```

เพราะภายใน Robot เป็น sequential:

```text
เวลาของ robot_r ≈ T(r,A) + T(r,B) + T(r,C)
```

เพราะ Robot 4 ตัว concurrent:

```text
เวลาช่วง Robot ทั้งหมด
≈ max(
    เวลาของ robot_1,
    เวลาของ robot_2,
    เวลาของ robot_3,
    เวลาของ robot_4
  )
+ scheduling/network overhead
```

ไม่ใช่โดยทั่วไป:

```text
ผลรวมเวลาของ request ทั้ง 12 ครั้ง
```

### กรณีสมมติเพื่อฝึกคิด

ถ้าทุก grab ใช้ 1 วินาทีเท่ากัน:

```text
Robot หนึ่งตัว = 1 + 1 + 1 = 3 วินาที
Robot สี่ตัว concurrent = ประมาณ 3 วินาที + overhead
Robot สี่ตัว sequential = ประมาณ 12 วินาที + overhead
```

ตัวเลขนี้เป็น **โจทย์สมมติ** ไม่ใช่ delay จริงจาก Server

### ช่วงที่ถูกจับเวลา

```text
สร้าง Client
Reset Factory            <- ไม่รวมใน elapsed_time
ตั้ง start_time          <- เริ่มจับตรงนี้
Robot 1-4 ทำงาน
กather รอครบ
คำนวณ elapsed_time       <- หยุดเชิงตรรกะตรงนี้
ปิด Client               <- ไม่รวมหลังคำนวณ
```

---

## 17. Expected Behavior

ถ้า dependency พร้อม Server เข้าถึงได้ และ request ทุกตัวสำเร็จ Terminal ควรเห็นรูปแบบ:

```text
Resetting Factory...
Starting Async Robot Operation...
Finished all tasks in X.XX seconds.
```

สิ่งที่โค้ดปัจจุบัน **ไม่พิมพ์**:

- ชื่อ Robot ขณะเริ่มหรือจบ
- part แต่ละชิ้นขณะหยิบ
- JSON response จาก reset
- response body จาก grab
- ผลลัพธ์ราย Robot

ดังนั้นการเห็นเพียง 3 บรรทัดไม่แปลว่า loop ไม่ทำงาน โค้ดส่ง request อยู่ภายในแต่ไม่ได้ print รายละเอียด

### จำนวน request ใน success path

```text
Reset request = 1
Grab requests = 4 Robots x 3 Parts = 12
รวม = 13 HTTP POST requests
```

### ลำดับที่รับประกัน

รับประกันภายใน Robot แต่ละตัว:

```text
A ก่อน B ก่อน C
```

ไม่รับประกันลำดับข้าม Robot เช่น:

```text
robot_1 A ต้องจบก่อน robot_2 A
```

เพราะ Robot ทำ concurrent และขึ้นกับ Network/Server scheduling

### เมื่อ error

ถ้าเป็น `httpx.HTTPError` หรือ `ValueError` ควรเห็น:

```text
Error: <รายละเอียดข้อผิดพลาด>
```

และอาจไม่เห็นบรรทัด `Finished all tasks...`

---

# Part F — วิธีใช้งานจริง

## 18. ติดตั้งและตรวจ Dependency

จาก repo root:

```bash
python -m pip install httpx
```

ตรวจว่า import ได้:

```bash
python -c "import httpx; print(httpx.__version__)"
```

ถ้า project มี virtual environment อยู่แล้ว ควร activate environment นั้นก่อนติดตั้ง เพื่อไม่ปะปน package กับ Python ตัวอื่น

---

## 19. ตรวจ Syntax โดยไม่ยิง Server

```bash
python -m py_compile Week6/robots.py
```

ถ้าไม่มีข้อความ error แปลว่า syntax compile ผ่าน

ข้อจำกัด:

```text
py_compile ผ่าน
!= Server เชื่อมต่อได้
!= endpoint ถูกตาม Server จริง
!= request ทั้ง 13 ครั้งสำเร็จ
```

`py_compile` อาจสร้าง `Week6/__pycache__/` ถ้าไม่ต้องการเก็บไฟล์ cache ใน repository ให้ลบ cache ที่เพิ่งสร้างหลังตรวจ

---

## 20. รันโปรแกรม

จาก repo root:

```bash
python Week6/robots.py
```

หรือเข้าโฟลเดอร์ก่อน:

```bash
cd Week6
python robots.py
```

ก่อนรัน live ควรตรวจว่า:

- เชื่อมต่อเครือข่ายที่เข้าถึง `172.16.2.117` ได้
- Server เปิดที่ port `8088`
- ได้รับอนุญาตให้ reset และเปลี่ยนสถานะ Robot ของ Student ID นี้
- ไม่มีการทดสอบของตนเองอีก process ที่กำลังใช้ state เดียวกัน

> การรันไม่ใช่ read-only test เพราะส่ง POST 13 ครั้งและเปลี่ยน state บน Server จริง

---

## 21. Network Caveats — ข้อควรระวังเรื่องเครือข่าย

`172.16.2.117` เป็น private IPv4 address โดยทั่วไปเข้าถึงได้เฉพาะเครือข่ายภายในที่ route ถึงเครื่องนั้น เช่น Wi-Fi/LAN ห้องเรียนหรือ VPN ที่กำหนด

### `172.16.2.117` ไม่ใช่ `127.0.0.1`

```text
127.0.0.1     = เครื่องที่กำลังรัน Python เอง
172.16.2.117  = เครื่องอื่น/Server ใน private network ตามโค้ด
```

การเปิด local server ที่ `127.0.0.1:8088` จะไม่ทำให้ client ปัจจุบันส่งไป local เพราะ `BASE_URL` ยังชี้ `172.16.2.117:8088`

### Port `8088`

URL ต้องมี port ตรงกับ Server:

```text
http://172.16.2.117:8088
```

ถ้าตัด `:8088` browser/client จะใช้ default port ของ HTTP ซึ่งเป็นคนละปลายทาง

### Timeout ไม่เท่ากับ Server rollback

ถ้า Client timeout ขณะ POST:

```text
Client อาจหยุดรอ
แต่ Server อาจรับคำสั่งแล้วและทำงานต่อ
```

ดังนั้น:

```text
Timeout != ยืนยันว่า Robot state ไม่เปลี่ยน
```

หากต้องรู้สถานะจริง ต้องใช้ endpoint ตรวจสถานะหรือกลไก reset ตาม API ที่ Server รองรับ แต่ `robots.py` ไม่มี status endpoint จึงไม่ควรเดา URL

### ห้ามเปลี่ยน `BASE_URL` หรือ Student ID โดยเดา

โค้ดปัจจุบันกำหนดชัดเจน:

```python
BASE_URL = "http://172.16.2.117:8088"
STUDENT_ID = "6710301033"
```

ก่อนส่งงานให้รักษาค่าตาม requirement อาจารย์ ถ้าจะทดลอง Server อื่นควรทำอย่างมีขอบเขตและคืนค่าก่อนส่ง

---

# Part G — Pitfalls และ Debugging

## 22. Pitfalls ที่พบบ่อย

### 22.1 ลืม `await`

ผิด:

```python
client.post(url_path, json=payload)
```

จะได้ coroutine/awaitable ของ HTTPX แต่ request อาจไม่ถูกดำเนินการตามที่คาด และอาจมี warning

ถูก:

```python
await client.post(url_path, json=payload)
```

### 22.2 ทำ A, B, C concurrent ภายใน Robot

ถ้าใช้ gather กับ parts ของ Robot เดียว จะทำลายลำดับ sequential ของโจทย์

### 22.3 ทำ Robot ทั้ง 4 sequential

รูปแบบนี้ช้ากว่าและไม่ตรงจุดประสงค์:

```python
for robot_id in ROBOTS:
    await run_robot_task(client, robot_id)
```

เพราะ Robot ถัดไปเริ่มหลังตัวก่อนครบ A, B, C แล้ว

### 22.4 ส่ง list เข้า `gather()` โดยไม่แตก `*`

ผิด:

```python
await asyncio.gather(robot_tasks)
```

ถูก:

```python
await asyncio.gather(*robot_tasks)
```

### 22.5 ใช้ `time.sleep()` ใน coroutine

`time.sleep()` block Event Loop thread ถ้าต้องรอใน client logic ให้ใช้ `await asyncio.sleep()` แต่ในโปรแกรมนี้การรอหลักเกิดใน `await client.post()` อยู่แล้ว

### 22.6 ลืม `raise_for_status()`

การได้ response 404/500 ก็ยังเป็น response object หากไม่ตรวจ status อาจประกาศ success ผิด

### 22.7 เข้าใจ local return เป็น Server response

`grab_part()` คืน:

```python
{"robot": ..., "part": ..., "status": "success"}
```

แต่ dictionary นี้สร้างใน Client ไม่ได้อ่านจาก `response.json()`

### 22.8 คิดว่า timeout 10 วินาทีครอบทั้งโปรแกรม

ค่าของ HTTPX ใช้กับ request operations ตาม config ไม่ใช่ global deadline ของ Robot workflow ทั้งหมด

### 22.9 คิดว่า `robot_tasks` เป็น Task object แล้ว

ค่าปัจจุบันเป็น coroutine objects จน `gather()` schedule ให้ ถ้าต้องการ method เช่น `.done()` ต้องสร้าง Task จริงก่อน

### 22.10 คิดว่า `gather()` ทำให้ลำดับ A/B/C หาย

`gather()` อยู่ระดับ Robot ส่วน loop ที่ await ทีละ part ยังรักษาลำดับของแต่ละ Robot

### 22.11 ใช้ synchronous HTTP client ใน async flow

อาจ block Event Loop ทำให้ Robot อื่นไม่คืบหน้าระหว่างรอ network

### 22.12 ทดสอบ live ซ้ำโดยไม่รู้ผลข้างเคียง

โปรแกรม reset state แล้วส่ง POST จำนวนมาก การรันซ้ำอาจชนกับการดูผลหรือการทดลอง process อื่นของ Student ID เดียวกัน

---

## 23. Debug Checklist

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ |
|---|---|---|
| `ModuleNotFoundError: httpx` | ยังไม่ติดตั้ง package ใน Python environment นี้ | `python -m pip install httpx` |
| `ConnectError` | Server ปิด, IP ผิด, อยู่คนละ network | ตรวจ network และ `BASE_URL` |
| `ConnectTimeout` | ต่อปลายทางไม่ทัน | ตรวจ Wi-Fi/VPN/firewall/Server |
| `ReadTimeout` | ต่อได้แต่ Server ตอบช้าเกิน config | ตรวจ Server load และ timeout |
| HTTP 404 | path, Student ID หรือ Robot ID ไม่ตรง API | เปรียบเทียบ endpoint ทีละตัวอักษร |
| HTTP 4xx | payload หรือ state ไม่ถูกต้อง | ตรวจ `{"part": "A/B/C"}` และ error body |
| HTTP 5xx | Server เกิดปัญหา | ดู Server log/แจ้งผู้ดูแล |
| `ValueError` หลัง reset | reset response ไม่ใช่ JSON ที่ parse ได้ | ตรวจ response จริงด้วยเครื่องมือที่ได้รับอนุญาต |
| เห็นแค่ 3 บรรทัด | โค้ดไม่ได้ print ราย part | เป็น behavior ปัจจุบัน ไม่จำเป็นต้องเป็น bug |
| เวลาไม่คงที่ | Network และ Server scheduling เปลี่ยน | ดูแนวโน้มหลายรอบ ไม่ยึดเลขเดียว |
| บาง Robot หยุดก่อน C | request ก่อนหน้าเกิด exception | อ่าน `Error:` และ Server log |
| Local server เปิดแต่ยังต่อไม่ได้ | code ชี้ private IP | ตรวจ `BASE_URL` |

### วิธีไล่ตรวจทีละชั้น

1. ตรวจ syntax:

   ```bash
   python -m py_compile Week6/robots.py
   ```

2. ตรวจ dependency:

   ```bash
   python -c "import httpx; print('httpx ready')"
   ```

3. ตรวจค่าจากไฟล์:

   ```text
   STUDENT_ID = 6710301033
   BASE_URL   = http://172.16.2.117:8088
   ```

4. ตรวจว่าเครื่องอยู่ใน network ที่เข้าถึง Server ได้
5. รัน live เฉพาะเมื่อยอมรับผลข้างเคียงของ reset/grab
6. อ่านข้อความ error เต็ม ๆ ไม่แก้ timeout หรือ URL แบบสุ่ม

---

# Part H — แบบฝึกหัด

## 24. Exercise 1 — วาด Timeline

ให้สมมติ delay ต่อ request ดังนี้:

| Robot | A | B | C |
|---|---:|---:|---:|
| robot_1 | 1s | 1s | 1s |
| robot_2 | 2s | 1s | 1s |
| robot_3 | 1s | 3s | 1s |
| robot_4 | 1s | 1s | 2s |

ตอบ:

1. Robot แต่ละตัวใช้เวลารวมเท่าไร
2. Robot ใดเสร็จช้าที่สุด
3. `gather()` จบประมาณกี่วินาที ถ้าไม่คิด overhead

เฉลยแนวคิด:

```text
robot_1 = 3s
robot_2 = 4s
robot_3 = 5s
robot_4 = 4s
gather จบประมาณ max(3, 4, 5, 4) = 5s
```

---

## 25. Exercise 2 — นับ Request

ถ้าเพิ่ม:

```python
PARTS = ["A", "B", "C", "D"]
ROBOTS = ["robot_1", "robot_2", "robot_3", "robot_4", "robot_5"]
```

จำนวน request ใน success path เป็นเท่าไร

เฉลย:

```text
Reset = 1
Grab  = 5 x 4 = 20
รวม   = 21 POST requests
```

---

## 26. Exercise 3 — เปรียบเทียบ Flow

อธิบายความต่างระหว่าง:

```python
for robot_id in ROBOTS:
    await run_robot_task(client, robot_id)
```

กับ:

```python
robot_tasks = [run_robot_task(client, robot_id) for robot_id in ROBOTS]
await asyncio.gather(*robot_tasks)
```

คำตอบย่อ:

- แบบแรก: Robot ทั้งตัวทำ sequential ทีละตัว
- แบบสอง: Robot 4 workflow ทำ concurrent แต่ A/B/C ภายในแต่ละ workflow ยัง sequential

---

## 27. Exercise 4 — อ่าน API Request

เมื่อเรียก:

```python
await grab_part(client, "robot_4", "C")
```

ให้เขียน Method, URL และ JSON body

เฉลย:

```text
Method: POST
URL: http://172.16.2.117:8088/student/6710301033/robot/robot_4/grab
```

```json
{
  "part": "C"
}
```

---

## 28. Exercise 5 — ทำนาย Failure

ถ้า `robot_2` หยิบ `B` แล้ว Server ตอบ HTTP 500:

1. `raise_for_status()` ทำอะไร
2. `robot_2` จะส่ง `C` หรือไม่
3. จะเห็นข้อความ Finished หรือไม่ใน flow นี้
4. error ไปจบที่ไหน

เฉลยแนวคิด:

1. โยน `httpx.HTTPStatusError`
2. ไม่ส่ง `C` จาก loop นี้ เพราะ coroutine หยุดที่ exception
3. โดยปกติไม่ถึงบรรทัด Finished
4. ไหลผ่าน `gather()` และ `main()` ไปถูกจับใน `except httpx.HTTPError` แล้วพิมพ์ `Error: ...`

อย่าสรุปว่า request ของ Robot อื่นหรือ state บน Server ถูก rollback เพราะโค้ดไม่ได้รับประกันเรื่องนั้น

---

## 29. Exercise 6 — ออกแบบผลลัพธ์โดยไม่แก้ไฟล์จริง

ลองเขียนบนกระดาษว่าจะปรับ `run_robot_task()` อย่างไรให้เก็บผลของ A, B, C แล้ว return list โดยยัง sequential

แนวคำตอบ:

```python
async def run_robot_task(client, robot_id):
    results = []
    for part in PARTS:
        result = await grab_part(client, robot_id, part)
        results.append(result)
    return results
```

จากนั้น `results = await asyncio.gather(...)` จะเป็น list ซ้อนตาม Robot และ Part

> นี่เป็นแบบฝึกหัดแนวคิดเท่านั้น ไฟล์ `robots.py` ปัจจุบันไม่ได้ถูกแก้

---

## 30. Exercise 7 — ออกแบบ Mock Test

โจทย์: ถ้าไม่ต้องการยิง Server จริง ควรทดสอบอะไรบ้างด้วย `httpx.MockTransport`

Checklist:

- [ ] Reset ใช้ method `POST`
- [ ] Reset path เป็น `/student/6710301033/reset`
- [ ] Grab path มี Student ID และ Robot ID ถูกต้อง
- [ ] Grab body เป็น `{"part": ...}`
- [ ] Robot เดียวส่ง A, B, C ตามลำดับ
- [ ] มี Robot ครบ 4 ตัว
- [ ] HTTP 500 ทำให้เกิด exception
- [ ] Reset response ที่ไม่ใช่ JSON ทำให้เกิด `ValueError`

Mock test เหมาะกว่า live test สำหรับตรวจ request contract เพราะไม่เปลี่ยน state บน Server และผลไม่ขึ้นกับเครือข่าย

---

# Part I — คำถามแนวสอบ

## 31. คำถามพร้อมคำตอบสั้น

### 31.1 `async def` คืออะไร

ใช้ประกาศ coroutine function ซึ่งสามารถใช้ `await` ภายในและทำงานกับ Event Loop ได้

### 31.2 `await` ทำอะไร

รอ awaitable ให้เสร็จ พร้อมเปิดโอกาสให้ Event Loop ไปจัดการงาน async อื่นระหว่างรอ I/O

### 31.3 ทำไม `grab_part()` เหมาะกับ async

เพราะส่ง HTTP request ซึ่งเป็นงาน I/O-bound เวลาส่วนใหญ่คือการรอ Network/Server

### 31.4 ทำไม A, B, C ต้อง sequential

เพราะ `for part in PARTS` มี `await grab_part(...)` ในแต่ละรอบ จึงไม่เริ่ม part ถัดไปจนรอบปัจจุบันสำเร็จ

### 31.5 ทำไม Robot 4 ตัว concurrent

เพราะสร้าง coroutine 4 ตัวและส่งทั้งหมดให้ `asyncio.gather()`

### 31.6 `gather()` รออะไร

ใน success path รอ awaitable ทั้งหมดให้เสร็จ และคืนผลตามลำดับ input

### 31.7 `robot_tasks` เป็น Task object หรือไม่

ในโค้ดปัจจุบันเป็น list ของ coroutine objects ก่อนส่งให้ `gather()` ไม่ได้สร้างด้วย `asyncio.create_task()` โดยตรง

### 31.8 `*robot_tasks` ทำอะไร

แตกสมาชิกใน list ให้เป็น positional arguments หลายตัวของ `gather()`

### 31.9 ทำไม reuse `AsyncClient`

ใช้ connection pool ร่วมกัน ลด overhead รวม config ไว้จุดเดียว และปิด resource ด้วย `async with`

### 31.10 `base_url` ทำอะไร

เป็นส่วน host/port ที่ HTTPX นำไปต่อกับ relative path ใน `client.post()`

### 31.11 `json=payload` ทำอะไร

serialize Python dictionary เป็น JSON request body และตั้ง content type ที่เหมาะสม

### 31.12 `raise_for_status()` ทำอะไร

โยน exception เมื่อ HTTP status เป็น error เพื่อไม่ให้ flow ทำเหมือน request สำเร็จ

### 31.13 Reset endpoint คืออะไร

```text
POST http://172.16.2.117:8088/student/6710301033/reset
```

### 31.14 Grab endpoint คืออะไร

```text
POST http://172.16.2.117:8088/student/6710301033/robot/{robot_id}/grab
```

พร้อม JSON:

```json
{"part": "A"}
```

โดยค่า part เปลี่ยนเป็น A, B, C ตามรอบ

### 31.15 Success path มี request กี่ครั้ง

13 ครั้ง: reset 1 + grab 12

### 31.16 Timeout 10 วินาทีหมายถึงทั้งโปรแกรมต้องจบใน 10 วินาทีหรือไม่

ไม่ใช่ เป็น timeout config ของ HTTP request operations ผ่าน Client ไม่ใช่ global deadline ของทั้ง workflow

### 31.17 ทำไม elapsed time ไม่รวม reset

เพราะ `start_time` ถูกกำหนดหลัง `await reset_factory(client)`

### 31.18 Concurrent เร็วเท่าผลรวม หรือเท่างานช้าที่สุด

สำหรับ 4 Robot workflow ที่เริ่ม concurrent เวลารวมมีแนวโน้มใกล้ workflow Robot ที่ช้าที่สุด บวก overhead ไม่ใช่ผลรวมทั้ง 4 workflow

### 31.19 ถ้า request timeout แปลว่า Server ไม่เปลี่ยน state ใช่ไหม

ไม่เสมอ Server อาจได้รับ POST แล้วและทำต่อ แม้ Client หยุดรอ

### 31.20 `grab_part()` ใช้ JSON response จาก Server หรือไม่

ไม่ใช้ body หลังตรวจ status แต่สร้าง local success dictionary แล้ว return

### 31.21 `reset_factory()` ใช้ JSON response หรือไม่

ใช้ โดยเรียก `response.json()` และ return ผล

### 31.22 ถ้า Reset response ไม่ใช่ JSON เกิดอะไร

`response.json()` อาจโยน `ValueError` ซึ่ง error handler ระดับบนจับและพิมพ์ได้

### 31.23 ทำไมไม่ควรใช้ `time.sleep()` ใน async function

เพราะ block Event Loop thread ทำให้งาน Robot อื่นคืบหน้าไม่ได้ในช่วงนั้น

### 31.24 โปรแกรมนี้สร้าง Thread/Process เพิ่มหรือไม่

โค้ดไม่ได้สร้าง Thread หรือ Process เอง ใช้ Event Loop และ async I/O

### 31.25 มีการ reset หลังจบหรือไม่

ไม่มีในโค้ดปัจจุบัน มีเฉพาะ reset ก่อนเริ่ม Robot operation

---

# Part J — Checklist ก่อนสอบ

## 32. Concept Checklist

- [ ] อธิบาย Client, Server, Request, Response ได้
- [ ] อธิบาย coroutine, Task และ Event Loop ได้
- [ ] แยก concurrency ออกจาก parallelism ได้
- [ ] รู้ว่า `STUDENT_ID` คือ `6710301033`
- [ ] รู้ว่า `BASE_URL` คือ `http://172.16.2.117:8088`
- [ ] จำ `PARTS = ["A", "B", "C"]` ได้
- [ ] จำ Robot 4 ตัวได้
- [ ] เขียน Reset endpoint ได้ตรง
- [ ] เขียน Grab endpoint และ payload ได้ตรง
- [ ] อธิบาย `raise_for_status()` ได้
- [ ] อธิบาย `response.json()` ได้
- [ ] รู้ว่า Grab return เป็น local dict
- [ ] อธิบาย sequential ภายใน Robot ได้
- [ ] อธิบาย concurrent ระหว่าง Robot ได้
- [ ] อธิบาย `asyncio.gather(*robot_tasks)` ได้
- [ ] รู้ว่า gather คืนผลตาม input order
- [ ] รู้ว่า success path มี 13 POST requests
- [ ] รู้ว่า reset ไม่ถูกรวมใน elapsed time
- [ ] รู้ว่า timeout ไม่รับประกัน rollback

## 33. Practical Checklist

- [ ] อยู่ที่ repo root ถูกต้อง
- [ ] Python environment มี `httpx`
- [ ] `python -m py_compile Week6/robots.py` ผ่าน
- [ ] เชื่อม network ที่เข้าถึง `172.16.2.117` ได้
- [ ] Server port `8088` เปิด
- [ ] เข้าใจว่าการรัน live จะเปลี่ยน Server state
- [ ] รัน `python Week6/robots.py` ได้เมื่อได้รับอนุญาต
- [ ] อ่านข้อความ `Error:` เต็ม ๆ เมื่อมีปัญหา
- [ ] ไม่เปลี่ยน Student ID หรือ URL โดยเดา

---

# Part K — Cheat Sheet

## 34. ค่าที่ต้องจำ

```python
STUDENT_ID = "6710301033"
BASE_URL = "http://172.16.2.117:8088"
PARTS = ["A", "B", "C"]
ROBOTS = ["robot_1", "robot_2", "robot_3", "robot_4"]
```

## 35. API ที่ต้องจำ

```text
Reset:
POST http://172.16.2.117:8088/student/6710301033/reset
Body: ไม่มีในโค้ด

Grab:
POST http://172.16.2.117:8088/student/6710301033/robot/{robot_id}/grab
Body: {"part": "A"}  # เปลี่ยนเป็น A, B, C
```

## 36. Async ที่ต้องจำ

```text
async def
    ประกาศ coroutine function

await
    รอ awaitable และคืน control ให้ Event Loop ระหว่างรอ I/O

asyncio.run(main())
    เปิด Event Loop แล้วรัน main

asyncio.gather(a, b, c)
    ให้หลาย awaitable คืบหน้า concurrent และรอครบใน success path

*robot_tasks
    แตก list เป็น arguments หลายตัว

httpx.AsyncClient
    HTTP client แบบ async

async with
    จัดการเปิด/ปิด Client อย่างถูกต้อง

raise_for_status()
    เปลี่ยน HTTP error status เป็น exception
```

## 37. ภาพจำสำคัญที่สุด

```text
ผิดความเข้าใจ:
12 grabs ทำ sequential ทั้งหมด
A/B/C ของ Robot เดียวทำพร้อมกันหมด

โค้ดจริง:
robot_1: A -> B -> C
robot_2: A -> B -> C
robot_3: A -> B -> C
robot_4: A -> B -> C
           ^
ทั้ง 4 แถวคืบหน้า concurrent ผ่าน gather
แต่ในแต่ละแถวต้องเรียง A ก่อน B ก่อน C
```

## 38. คำสั่ง

```bash
python -m pip install httpx
python -c "import httpx; print(httpx.__version__)"
python -m py_compile Week6/robots.py
python Week6/robots.py
```

---

## 39. สรุปสุดท้าย

จำ 8 ข้อนี้ให้ได้:

1. `robots.py` เป็น async HTTP client ที่คุยกับ `http://172.16.2.117:8088`
2. Student ID ปัจจุบันคือ `6710301033`
3. โปรแกรม reset ก่อนเริ่ม และเวลา reset ไม่รวมใน elapsed time
4. Robot แต่ละตัวหยิบ `A -> B -> C` แบบ sequential
5. Robot 4 ตัวทำงาน concurrent ด้วย `asyncio.gather()`
6. `httpx.AsyncClient` ทำให้รอ HTTP แบบไม่ block Event Loop และ reuse connection ได้
7. Success path ส่ง 13 POST requests: reset 1 และ grab 12
8. Timeout หรือ Client error ไม่ได้ยืนยันว่า Server rollback state แล้ว

ประโยคสรุปสำหรับตอบอาจารย์:

> โปรแกรมนี้ใช้ `httpx.AsyncClient` ส่ง HTTP POST ไปยัง Robot Factory API โดย reset สถานะของรหัสนักศึกษา `6710301033` ก่อน จากนั้นสร้าง coroutine สำหรับ Robot 4 ตัวและรัน concurrent ด้วย `asyncio.gather()` ขณะที่แต่ละ Robot ยังใช้ `await` ใน loop เพื่อหยิบชิ้นส่วน A, B และ C แบบ sequential ดังนั้น concurrency เกิดข้าม Robot แต่ไม่ทำลายลำดับงานภายใน Robot แต่ละตัวค่ะ

---

## ✅ สิ่งที่ได้เรียนรู้จากคู่มือนี้

- [ ] อ่าน architecture ของ async HTTP client ได้
- [ ] แปลง source code เป็น API contract ได้โดยไม่เดาข้อมูลที่ไม่มี
- [ ] เห็นรูปแบบ “sequential inside, concurrent outside” ชัดเจน
- [ ] อธิบาย `gather()`, `await` และ `AsyncClient` ได้
- [ ] รันและ debug โปรแกรมอย่างระวังผลข้างเคียงของ Network API ได้
