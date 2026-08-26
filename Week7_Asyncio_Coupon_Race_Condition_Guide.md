# Week 7 Asyncio Coupon Race Condition Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงในโฟลเดอร์ `Week7`** เพื่อใช้ทำความเข้าใจและทบทวนก่อนสอบเรื่อง `asyncio`, FastAPI, HTTPX, shared state, race condition, critical section และ `asyncio.Lock`

ไฟล์ที่ใช้เป็นแหล่งอ้างอิงมี 6 ไฟล์:

- `Week7/server_vulnerable.py`
- `Week7/server.py`
- `Week7/server_example.py`
- `Week7/client.py`
- `Week7/client_example.py`
- `Week7/test_server_example.py`

> **เป้าหมาย:** อ่านจบแล้วอธิบายได้ว่า race condition เกิดขึ้นอย่างไร, ทำไม `await` ทำให้ request อื่นแทรกได้, critical section อยู่ตรงไหน, `asyncio.Lock` ป้องกันปัญหาอย่างไร, API แต่ละ endpoint รับและคืนอะไร และควรรันไฟล์คู่ใดร่วมกัน

---

## 1. Week 7 กำลังเรียนเรื่องอะไร

Week 7 จำลองระบบแจกคูปองให้กลุ่มนักศึกษา 6 คน โดยมีข้อกำหนดสำคัญดังนี้:

- มีนักศึกษา `6` คน
- นักศึกษาแต่ละคนรับคูปองได้สูงสุด `2` ใบ
- ระบบมีคูปองทั้งหมด `11` ใบ
- หลาย client สามารถส่ง request เข้ามาในเวลาใกล้กัน
- server ต้องไม่แจกคูปองใบเดียวกันซ้ำ
- server ต้องไม่ให้นักศึกษาคนใดเกิน 2 ใบ

ภาพรวมระบบ:

```text
client.py / client_example.py
            |
            | HTTP request แบบ async
            v
server_vulnerable.py / server.py / server_example.py
            |
            | อ่านและแก้ shared state ในหน่วยความจำ
            v
coupons_db + current_coupon_index + student_claims
```

หัวใจของบทเรียนไม่ใช่เพียง “เรียก API ได้” แต่คือ:

> เมื่อ coroutine หลายตัวใช้ข้อมูลร่วมกัน การสลับงานตรงจุด `await` อาจทำให้แต่ละงานตัดสินใจจากข้อมูลเก่าและแก้ข้อมูลชนกันได้

---

## 2. 🎯 Use case — เรียนเรื่องนี้แล้วใช้ทำอะไรได้

หลังอ่านบทนี้ เราจะสามารถ:

1. ตรวจหา race condition ใน endpoint แบบ async
2. ระบุ critical section ที่ต้องทำแบบ indivisible หรือ atomic
3. ใช้ `asyncio.Lock` ปกป้องข้อมูลร่วมใน process เดียว
4. ออกแบบ API contract ให้ client และ server ตรงกัน
5. แยก application status เช่น `LIMIT_REACHED` ออกจาก HTTP status เช่น `404`
6. เขียนและอ่าน test ที่เรียก FastAPI โดยไม่ต้องเปิด port จริง
7. อธิบายได้ว่าทำไม test แบบ sequential อาจผ่าน แม้ระบบยังมี race condition

ตัวอย่างระบบจริงที่ใช้แนวคิดเดียวกัน:

- ตัดสต็อกสินค้า
- จองที่นั่ง
- ใช้คูปองส่วนลดครั้งเดียว
- ถอนเงินหรือโอนเงิน
- เพิ่มเลขลำดับเอกสาร
- จำกัดจำนวนสิทธิ์ลงทะเบียน

---

## 3. คำศัพท์สำคัญ

| คำ | ความหมายแบบง่าย | ตัวอย่างใน Week 7 |
|---|---|---|
| Client | โปรแกรมที่ส่งคำขอ | `client.py`, `client_example.py` |
| Server | โปรแกรมที่รับและประมวลผลคำขอ | ไฟล์ `server*.py` |
| Endpoint | HTTP method + path | `POST /claim` |
| Request body | JSON ที่ client ส่ง | `{"student_id": "6710301033"}` |
| Response | ข้อมูลที่ server ตอบกลับ | `{"status": "SUCCESS", ...}` |
| Shared state | ข้อมูลที่หลาย coroutine ใช้ร่วมกัน | `current_coupon_index`, `student_claims` |
| Race condition | ผลลัพธ์ผิดเพราะลำดับการสลับงานไม่แน่นอน | สอง request ได้คูปองเลขเดียวกัน |
| Critical section | ช่วงที่อ่าน/ตรวจ/แก้ shared state และต้องไม่ถูกแทรก | ตรวจ limit ถึงอัปเดต index |
| Lock / Mutex | กลไกให้เข้า critical section ทีละงาน | `coupon_lock = asyncio.Lock()` |
| Coroutine | งานที่ประกาศด้วย `async def` | `claim_coupon()` |
| Event loop | ตัวจัดตารางและสลับ coroutine | เริ่มผ่าน Uvicorn หรือ `asyncio.run()` |
| `await` | จุดที่ coroutine ยอมให้งานอื่นคืบหน้าได้ | `await asyncio.sleep(0.1)` |
| Interleaving | คำสั่งจากหลายงานสลับกัน | A อ่าน index แล้ว B มาอ่านก่อน A อัปเดต |
| Atomic | มองจากภายนอกเหมือนเกิดครบทั้งชุดในครั้งเดียว | claim หนึ่งครั้งภายใน lock |
| Application status | สถานะธุรกิจใน JSON | `SUCCESS`, `LIMIT_REACHED` |
| HTTP status | สถานะระดับ HTTP | `200`, `404`, `422` |

---

## 4. ข้อมูลตั้งต้นของระบบ

### 4.1 นักศึกษา 6 คน

ทั้งสาม server ใช้นักศึกษาชุดเดียวกัน:

```text
6710301017
6710301019
6710301020
6710301033
6710301034
6710301043
```

ลำดับใน `server_vulnerable.py` ต่างจากอีกสองไฟล์ แต่สมาชิกทั้ง 6 คนเหมือนกัน

### 4.2 ทำไมมี 11 คูปอง

โค้ดคำนวณว่า:

```python
GROUP_SIZE = len(STUDENTS)
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1
```

เมื่อ `GROUP_SIZE = 6`:

```text
TOTAL_COUPONS = (6 × 2) - 1
              = 12 - 1
              = 11
```

ถ้าทุกคนต้องการคนละ 2 ใบ จะต้องใช้ 12 ใบ แต่มีเพียง 11 ใบ ดังนั้นในระบบที่ถูกต้อง:

- แจกได้รวมไม่เกิน 11 ครั้ง
- ไม่มีคูปองซ้ำ
- ไม่มีใครเกิน 2 ใบ
- ถ้าแจกตามลำดับจนหมด อาจมี 5 คนได้คนละ 2 ใบ และอีก 1 คนได้ 1 ใบ

คนที่ได้เพียง 1 ใบไม่จำเป็นต้องเป็นคนเดิมเสมอ เพราะขึ้นกับลำดับ request

### 4.3 รูปแบบชื่อคูปอง

| ไฟล์ | รูปแบบ | ตัวอย่าง |
|---|---|---|
| `server_vulnerable.py` | ขีดกลาง | `COUPON-01` |
| `server.py` | ขีดล่าง | `COUPON_01` |
| `server_example.py` | ขีดล่าง | `COUPON_01` |

จุดนี้สำคัญต่อ expected output และ test เพราะ string ต้องตรงกันทุกตัวอักษร

---

## 5. Shared state ของ server

ทั้งสาม server เก็บข้อมูลไว้ในหน่วยความจำของ Python process

### 5.1 `coupons_db`

```python
coupons_db = ["COUPON_01", "COUPON_02", ..., "COUPON_11"]
```

เป็นรายการคูปองทั้งหมด ไม่ได้ลบคูปองออกจาก list เมื่อแจก แต่ใช้ index ชี้แทน

### 5.2 `current_coupon_index`

```python
current_coupon_index = 0
```

เป็น pointer ชี้คูปองใบถัดไป:

```text
index 0 -> COUPON_01
index 1 -> COUPON_02
index 2 -> COUPON_03
...
index 10 -> COUPON_11
index 11 -> หมดสต็อก
```

### 5.3 `student_claims`

```python
student_claims = {
    student_id: [] for student_id in STUDENTS
}
```

เก็บรายการคูปองของแต่ละคน เช่น:

```python
{
    "6710301033": ["COUPON_01", "COUPON_02"],
    "6710301034": ["COUPON_03"],
    ...
}
```

### 5.4 ทำไมข้อมูลเหล่านี้เสี่ยง

`current_coupon_index` และ `student_claims` ต้องสอดคล้องกันเสมอ:

```text
จำนวน claim ที่สำเร็จทั้งหมด
ควรเท่ากับ
current_coupon_index
```

ถ้า request สองตัวอ่าน index เดียวกันแล้วต่างคนต่าง append คูปองเดียวกัน จะเกิดข้อมูลไม่สอดคล้อง เช่น:

```text
student_claims มี claim สำเร็จ 2 รายการ
แต่ current_coupon_index เพิ่มจาก 0 เป็น 1 เท่านั้น
```

---

# Part A — Race Condition

## 6. `server_vulnerable.py` — Server ที่ตั้งใจให้มีช่องโหว่

ไฟล์นี้ไม่มี lock และตั้งใจใส่ delay เพื่อทำให้ race condition เกิดง่ายขึ้น

ส่วนสำคัญ:

```python
if current_coupon_index < len(coupons_db):
    index_to_claim = current_coupon_index
    await asyncio.sleep(0.1)
    coupon = coupons_db[index_to_claim]
    student_claims[student_id].append(coupon)
    current_coupon_index = index_to_claim + 1
```

มองแบบ request เดียวจะดูถูกต้อง:

```text
อ่าน index -> รอ -> หยิบคูปอง -> บันทึกให้คนรับ -> ขยับ index
```

แต่เมื่อมีหลาย request พร้อมกัน ปัญหาเกิดตรงช่วงระหว่าง “อ่าน” กับ “อัปเดต”

---

## 7. Race condition timeline แบบละเอียด

สมมติเริ่มต้น:

```text
current_coupon_index = 0
COUPON-01 ยังไม่มีใครได้รับ
```

Request A มาจากนักศึกษา `6710301033` และ Request B มาจาก `6710301034`

| เวลา | Request A | Request B | Shared state |
|---:|---|---|---|
| T0 | เริ่ม `claim_coupon()` | เริ่ม `claim_coupon()` | index = 0 |
| T1 | ตรวจนักศึกษาผ่าน | ยังไม่ทำ | index = 0 |
| T2 | ตรวจ limit ผ่าน | ตรวจนักศึกษาผ่าน | index = 0 |
| T3 | อ่าน `index_to_claim = 0` | ตรวจ limit ผ่าน | index = 0 |
| T4 | เข้า `await sleep(0.1)` และยอมคืน control | อ่าน `index_to_claim = 0` | index = 0 |
| T5 | ยัง sleep | เข้า `await sleep(0.1)` | index = 0 |
| T6 | ตื่นและแจก `COUPON-01` ให้ A | ยัง sleep | index = 0 |
| T7 | ตั้ง index เป็น `0 + 1` | ตื่นและแจก `COUPON-01` ให้ B | index = 1 |
| T8 | return `SUCCESS` | ตั้ง index เป็น `0 + 1` | index = 1 |
| T9 | จบ | return `SUCCESS` | index = 1 |

ผลลัพธ์ผิด:

```python
student_claims["6710301033"] == ["COUPON-01"]
student_claims["6710301034"] == ["COUPON-01"]
current_coupon_index == 1
```

ปัญหาที่เห็นได้:

1. คูปองใบเดียวกันถูกแจกสองครั้ง
2. ทั้งสอง request ได้ `SUCCESS`
3. server คิดว่าใช้สต็อกไปเพียง 1 ใบ
4. จำนวนรายการ claim ไม่ตรงกับ pointer
5. ต่อให้ไม่มี exception ผลทางธุรกิจก็ผิด

นี่คือ **lost update** ด้วย เพราะ A และ B ต่างเขียนค่า index เป็น `1`; การอัปเดตหนึ่งครั้งถูกกลบไป

---

## 8. `await` เกี่ยวข้องอย่างไร

`asyncio` ปกติรัน coroutine บน thread เดียว แต่ thread เดียวไม่ได้แปลว่าไม่มี race condition

เมื่อ coroutine A พบ:

```python
await asyncio.sleep(0.1)
```

A จะพักและเปิดโอกาสให้ event loop รัน coroutine B ต่อ ดังนั้นคำสั่งก่อนและหลัง `await` ไม่ได้เกิดติดกันแบบ atomic

```text
A: อ่าน index
A: await --------------------+
                              |
B: อ่าน index เดียวกัน <-----+
B: await
A: เขียนผล
B: เขียนผลทับ
```

`asyncio.sleep(0.1)` ในไฟล์ vulnerable ไม่ใช่สาเหตุพื้นฐานเพียงอย่างเดียว แต่เป็นตัว **ขยาย race window** ให้สังเกตง่าย ในระบบจริง จุด `await` อาจเป็นการรอ database, network หรือ file I/O

---

## 9. Race ที่ทำให้เกิน limit 2 ใบ

ปัญหาไม่ได้มีเพียงคูปองซ้ำ สมมตินักศึกษาคนเดียวมีคูปองอยู่แล้ว 1 ใบ และส่งสอง request พร้อมกัน:

```text
จำนวนเดิม = 1
Request A ตรวจ 1 < 2 -> ผ่าน
Request B ตรวจ 1 < 2 -> ผ่าน
A append -> จำนวนเป็น 2
B append -> จำนวนเป็น 3
```

จึงอาจละเมิดกฎ “สูงสุด 2 ใบ” ได้เช่นกัน

ข้อสรุปสำคัญ:

> การ lock เฉพาะบรรทัดเพิ่ม index ยังไม่พอ เพราะการตรวจ limit และการ append ต้องอาศัย snapshot เดียวกัน

---

## 10. Critical section อยู่ตรงไหน

Critical section คือช่วงที่ต้องให้ request หนึ่งทำครบก่อน request อื่นเข้ามาใช้ shared state เดียวกัน

สำหรับโจทย์นี้ควรรวม:

1. ตรวจว่า student อยู่ในระบบ
2. ตรวจว่า student ยังไม่ครบ 2 ใบ
3. ตรวจว่ายังมีคูปอง
4. อ่าน `current_coupon_index`
5. เลือกคูปอง
6. append คูปองเข้า `student_claims`
7. อัปเดต `current_coupon_index`
8. สร้างผลลัพธ์จาก state หลังอัปเดต

ถ้าแยก “check” ออกจาก “act” อาจเกิดปัญหาแบบ time-of-check to time-of-use:

```text
ตอนตรวจยังว่าง
แต่ตอนใช้ข้อมูล สถานะถูก request อื่นเปลี่ยนไปแล้ว
```

---

# Part B — ป้องกันด้วย `asyncio.Lock`

## 11. `server.py` — Protected server

ไฟล์ `server.py` สร้าง lock หนึ่งตัว:

```python
coupon_lock = asyncio.Lock()
```

และครอบ critical section:

```python
async with coupon_lock:
    # validate
    # check limit
    # check stock
    # read index
    # await sleep
    # append claim
    # update index
    # return response
```

ความหมายของ `async with coupon_lock`:

```text
Request A ขอ lock -> ได้ lock -> เข้า critical section
Request B ขอ lock -> lock ไม่ว่าง -> await รอ
Request A ทำเสร็จและออกจาก block -> ปล่อย lock
Request B จึงได้ lock -> อ่าน state ล่าสุด
```

---

## 12. Timeline เมื่อมี Lock

เริ่มจาก index = 0 เช่นเดิม:

| เวลา | Request A | Request B | Shared state |
|---:|---|---|---|
| T0 | ขอ lock และได้ lock | เริ่ม request | index = 0 |
| T1 | อ่าน index 0 | ขอ lock แต่ต้องรอ | index = 0 |
| T2 | sleep โดยยังถือ lock | ยังรอ lock | index = 0 |
| T3 | แจก `COUPON_01` | ยังรอ lock | index = 0 |
| T4 | เปลี่ยน index เป็น 1 | ยังรอ lock | index = 1 |
| T5 | ออกจาก block และปล่อย lock | ได้ lock | index = 1 |
| T6 | จบ | อ่าน index 1 | index = 1 |
| T7 | — | แจก `COUPON_02` และตั้ง index 2 | index = 2 |

ผลลัพธ์ถูกต้อง:

```text
A ได้ COUPON_01
B ได้ COUPON_02
current_coupon_index = 2
```

แม้ A จะ `await asyncio.sleep(0.1)` อยู่ใน critical section แต่ B เข้า critical section ไม่ได้ เพราะ A ยังถือ lock

---

## 13. Lock แก้อะไร และไม่ได้แก้อะไร

### Lock ช่วยป้องกัน

- แจก index เดียวกันซ้ำจาก request ที่ overlap
- lost update ของ `current_coupon_index`
- check-limit แล้ว append ชนกัน
- check-stock แล้วแจกเกินจาก snapshot เดียวกัน

### Lock ไม่ได้ทำให้ทุกอย่างเร็วขึ้น

ในโค้ดนี้แต่ละ claim ถือ lock ระหว่าง sleep 0.1 วินาที ดังนั้น claim จะถูก serialize:

```text
Request 1 ประมาณ 0.1s
Request 2 รอต่อ ประมาณ 0.2s จากจุดเริ่ม
Request 3 รอต่อ ประมาณ 0.3s จากจุดเริ่ม
```

นี่เป็น trade-off ระหว่าง correctness กับ concurrency

### Lock นี้มีขอบเขตแค่ process เดียว

`asyncio.Lock` ป้องกัน coroutine ภายใน event loop/process ที่ใช้ lock object เดียวกัน ถ้ารัน Uvicorn หลาย worker แต่ละ worker จะมี:

- lock คนละตัว
- `current_coupon_index` คนละตัว
- `student_claims` คนละชุด

จึงไม่ใช่วิธีแก้ระบบหลาย process หรือหลายเครื่อง ระบบจริงควรใช้ transaction/locking ของฐานข้อมูลหรือ shared datastore

### อย่าใช้ `threading.Lock` แบบ blocking แทนโดยไม่เข้าใจ

ใน coroutine ควรใช้ `asyncio.Lock` เพื่อให้การรอ lock เป็น async และไม่ block event loop

---

# Part C — เปรียบเทียบ Server ทั้งสามไฟล์

## 14. ตารางเปรียบเทียบ

| ประเด็น | `server_vulnerable.py` | `server.py` | `server_example.py` |
|---|---|---|---|
| จุดประสงค์ | สาธิต race | คำตอบแบบมี lock | ตัวอย่าง local ที่ใช้งานครบกับ example client/test |
| Lock | ไม่มี | มี | มี |
| Host เมื่อรันตรง | `0.0.0.0` | `0.0.0.0` | `127.0.0.1` |
| Port | `8088` | `8088` | `8088` |
| Coupon format | `COUPON-01` | `COUPON_01` | `COUPON_01` |
| `POST /claim` | มี | มี | มี |
| `GET /summary` | มี | มี | มี |
| `GET /my-coupons/{id}` | ไม่มี | **ไม่มี** | มี |
| Reset helper | ไม่มี | ไม่มี | `reset_coupon_state()` |
| Unknown student ใน `/claim` | JSON status, HTTP 200 | JSON status, HTTP 200 | JSON status, HTTP 200 |
| Unknown student ใน `/my-coupons` | ไม่มี route | ไม่มี route | HTTP 404 |
| Direct-run message | ไม่มี | ไม่มี | พิมพ์ URL และ Swagger ก่อนรัน |

---

## 15. `server_example.py` เพิ่มอะไรจาก `server.py`

### 15.1 Endpoint สรุปส่วนตัว

```text
GET /my-coupons/{student_id}
```

ถ้าพบนักศึกษา จะคืน:

```json
{
  "student_id": "6710301033",
  "total_claimed": 2,
  "claimed_coupons": ["COUPON_01", "COUPON_02"]
}
```

ถ้าไม่พบ จะใช้:

```python
raise HTTPException(status_code=404, detail="ไม่พบรายชื่อในระบบ")
```

จึงต่างจาก `POST /claim` ที่ unknown student ยังตอบ HTTP 200 แต่ใส่ application status `INVALID_STUDENT`

### 15.2 Reset state สำหรับ test

```python
reset_coupon_state()
```

ฟังก์ชันนี้:

- ตั้ง `current_coupon_index` กลับเป็น 0
- clear list ของนักศึกษาทุกคน
- ไม่สร้าง dictionary ใหม่ จึงยังรักษา object เดิมที่ endpoint อ้างถึง

### 15.3 รันตรงได้ชัดเจน

```bash
python Week7/server_example.py
```

ไฟล์จะพิมพ์ URL และเปิด Uvicorn ที่ `127.0.0.1:8088`

---

# Part D — API Contract

## 16. `POST /claim`

### Request

```http
POST /claim
Content-Type: application/json
```

```json
{
  "student_id": "6710301033"
}
```

Pydantic model:

```python
class ClaimRequest(BaseModel):
    student_id: str
```

### Response เมื่อสำเร็จ

```json
{
  "status": "SUCCESS",
  "claimed_coupon": "COUPON_01",
  "total_owned": 1
}
```

### Response เมื่อไม่ใช่นักศึกษาในกลุ่ม

```json
{
  "status": "INVALID_STUDENT",
  "message": "ไม่พบรายชื่อในระบบ"
}
```

### Response เมื่อครบ 2 ใบ

```json
{
  "status": "LIMIT_REACHED",
  "message": "คุณรับคูปองครบ 2 ใบแล้ว"
}
```

### Response เมื่อคูปองหมด

```json
{
  "status": "OUT_OF_STOCK",
  "message": "คูปองหมดแล้ว"
}
```

### HTTP status ที่ควรเข้าใจ

ในโค้ดทั้งสาม server สถานะธุรกิจข้างต้นถูก `return` เป็น dictionary ปกติ จึงได้ HTTP `200` แม้ application status จะเป็น `INVALID_STUDENT`, `LIMIT_REACHED` หรือ `OUT_OF_STOCK`

ถ้าขาด `student_id` หรือ JSON type ไม่ตรง Pydantic/FastAPI จะตอบ HTTP `422` โดยอัตโนมัติ

---

## 17. `GET /summary`

มีใน server ทั้งสามไฟล์

### Request

```http
GET /summary
```

### Response

```json
{
  "remaining_stock": 9,
  "student_claims": {
    "6710301017": [],
    "6710301019": [],
    "6710301020": [],
    "6710301033": ["COUPON_01", "COUPON_02"],
    "6710301034": [],
    "6710301043": []
  }
}
```

`remaining_stock` คำนวณจาก:

```python
len(coupons_db) - current_coupon_index
```

ใน protected server ค่านี้ตรงกับ pointer แต่ใน vulnerable server อาจดูเหมือนเหลือมากกว่าคูปอง unique ที่ควรเหลือ เพราะ lost update

---

## 18. `GET /my-coupons/{student_id}`

มีเฉพาะ `server_example.py`

### Request

```http
GET /my-coupons/6710301033
```

### Response เมื่อพบ

- HTTP `200`
- JSON มี `student_id`, `total_claimed`, `claimed_coupons`

### Response เมื่อไม่พบ

- HTTP `404`

```json
{
  "detail": "ไม่พบรายชื่อในระบบ"
}
```

### Endpoint mismatch ที่ต้องจำ

`client.py` เรียก:

```text
GET /my-coupons/{MY_STUDENT_ID}
```

แต่ `server.py` ไม่มี endpoint นี้ ดังนั้นถ้ารัน `client.py` คู่กับ `server.py`:

- `POST /claim` ทำงานได้
- `GET /summary` ทำงานได้
- `GET /my-coupons/...` ได้ HTTP `404 Not Found`
- client พิมพ์ `ดึงข้อมูลส่วนตัวไม่สำเร็จ Status Code: 404`

นี่ไม่ใช่ปัญหา network และไม่ใช่ race condition แต่เป็น **client/server API contract ไม่ตรงกัน**

คู่ที่ contract ตรงครบคือ:

```text
client_example.py <-> server_example.py
```

`client.py` จะใช้ `/my-coupons` ได้ก็ต่อเมื่อ server ปลายทางมี route นี้ เช่น `server_example.py` หรือ classroom server ที่ประกาศ contract เดียวกัน

---

# Part E — Client Files

## 19. `client.py` — Classroom URL

ค่าจริงในไฟล์:

```python
SERVER_IP = "172.20.58.26"
PORT = "8088"
SERVER_URL = "http://172.20.58.26:8088"
MY_STUDENT_ID = "6710301033"
```

URL นี้หมายถึง server ในเครือข่ายห้องเรียน/เครื่องอื่น ไม่ใช่ local server ของเรา

Flow:

```text
เปิด AsyncClient
    |
    v
POST /claim สูงสุด 5 รอบแบบ sequential
    |
    | หยุดเมื่อ LIMIT_REACHED หรือ OUT_OF_STOCK
    v
GET /my-coupons/{student_id}
    |
    v
GET /summary
```

client นี้จับ exception แยกแต่ละช่วง จึงอาจทำส่วนถัดไปต่อได้ แม้ request ก่อนหน้ามีปัญหา

ข้อสังเกต:

- request claim เป็น sequential เพราะใช้ `await` ใน `for`
- client หนึ่งตัวเพียงลำพังไม่ได้สร้าง claim หลายครั้งพร้อมกัน
- หากต้องการเห็น race ต้องมีหลาย client/process หรือสร้าง concurrent requests
- POST ไม่ตรวจ `res.status_code` ก่อน `res.json()`
- GET ส่วนตัวและ summary ตรวจ HTTP status ก่อนใช้ข้อมูล

---

## 20. `client_example.py` — Local URL

ค่าจริง:

```python
SERVER_URL = "http://127.0.0.1:8088"
MY_STUDENT_ID = "6710301033"
```

จึงออกแบบมาคู่กับ `server_example.py` ในเครื่องเดียวกัน

จุดต่างจาก `client.py`:

- ตั้ง timeout ตอนสร้าง `AsyncClient`
- เรียก `response.raise_for_status()` ทุก request
- ถ้า HTTP 4xx/5xx จะเกิด `httpx.HTTPError`
- จับ HTTP error รอบ `asyncio.run()` หนึ่งชั้น
- ใช้ set ในเงื่อนไขหยุด: `{"LIMIT_REACHED", "OUT_OF_STOCK"}`
- sleep ระหว่าง attempt `0.02` วินาที แทน `0.01`
- contract ตรงกับ `server_example.py` ครบทั้งสาม endpoint

### Expected flow บน server ที่เพิ่งเริ่มใหม่

```text
attempt 1 -> SUCCESS -> COUPON_01
attempt 2 -> SUCCESS -> COUPON_02
attempt 3 -> LIMIT_REACHED -> หยุด loop
my-coupons -> total_claimed = 2
summary -> remaining_stock = 9
```

Application status ที่คาดจาก client หนึ่งตัวตามลำดับคือ:

```text
SUCCESS, SUCCESS, LIMIT_REACHED
```

หากมี client อื่นใช้คูปองก่อน ผลเลขคูปองและ stock จะเปลี่ยน และอาจได้ `OUT_OF_STOCK`

---

## 21. Local URL กับ Classroom URL

| กรณี | Base URL | ใช้เมื่อ |
|---|---|---|
| Local example | `http://127.0.0.1:8088` | server และ client อยู่เครื่องเดียวกัน |
| Server bind ทุก interface | `0.0.0.0:8088` | ค่าที่ server ใช้ listen; client ไม่ควรใช้ `0.0.0.0` เป็นปลายทางทั่วไป |
| Classroom server | `http://172.20.58.26:8088` | อยู่ใน network ที่เข้าถึง IP นี้ได้ |

จำง่าย ๆ:

- `127.0.0.1` = เครื่องนี้
- `0.0.0.0` = server ฟังทุก network interface
- `172.20.58.26` = เครื่องปลายทางในเครือข่ายห้องเรียนตาม `client.py`

การเปิด local server ไม่ได้ทำให้ `client.py` เปลี่ยนมาเรียก local โดยอัตโนมัติ เพราะ URL ถูกเขียนไว้ใน client

---

# Part F — วิธีรันจริง

## 22. เตรียม environment

จาก repo root ติดตั้ง dependency หากยังไม่มี:

```bash
python -m pip install fastapi uvicorn httpx
```

เปิด Terminal ที่ repo root:

```text
C:\Host\04 University\02 Education\Year 3\01 อ.วัฒนา(แดง) Asynchronous programming\02 sendCode\async-2026-CDTI
```

ต้องเปิด server ค้างไว้หนึ่ง Terminal และรัน client ในอีก Terminal

---

## 23. วิธีรัน Protected Example ที่ contract ครบ

### Terminal 1 — เปิด server

```bash
python Week7/server_example.py
```

หรือใช้ Uvicorn จาก repo root:

```bash
python -m uvicorn Week7.server_example:app --host 127.0.0.1 --port 8088
```

Swagger UI:

```text
http://127.0.0.1:8088/docs
```

### Terminal 2 — รัน client

```bash
python Week7/client_example.py
```

Expected statuses เมื่อ server เพิ่งเริ่มและไม่มี client อื่น:

```text
ครั้งที่ 1: SUCCESS
ครั้งที่ 2: SUCCESS
ครั้งที่ 3: LIMIT_REACHED
```

Expected summary หลัก:

```text
6710301033 ได้ 2 ใบ
remaining_stock = 9
```

เมื่อหยุดและเปิด server ใหม่ state ในหน่วยความจำจะเริ่มใหม่

---

## 24. วิธีรัน `server.py`

รันตรงจาก repo root:

```bash
python Week7/server.py
```

หรือ:

```bash
python -m uvicorn Week7.server:app --host 127.0.0.1 --port 8088
```

`server.py` มี `/claim` และ `/summary` แต่ไม่มี `/my-coupons/{student_id}`

ดังนั้นไม่ควรคาดว่า `client.py` หรือ `client_example.py` จะทำครบทุกส่วนกับ server นี้ โดยไม่เกิด 404 ที่ personal summary

---

## 25. วิธีรัน Vulnerable Server

จาก repo root:

```bash
python Week7/server_vulnerable.py
```

หรือ:

```bash
python -m uvicorn Week7.server_vulnerable:app --host 127.0.0.1 --port 8088
```

จากนั้นต้องส่ง request ที่ overlap กันจึงจะเห็น race ได้ชัด การกด claim ทีละ request หรือใช้ client เพียงตัวเดียวแบบ sequential อาจไม่พบปัญหา

> อย่ารัน server หลายไฟล์พร้อมกันบน port `8088` เดียวกัน เพราะไฟล์ที่เปิดทีหลังจะ bind port ไม่ได้

---

## 26. รันจากภายในโฟลเดอร์ `Week7`

ถ้าเปลี่ยน current directory เข้า `Week7` แล้ว import path ต้องไม่มี `Week7.`:

```bash
cd Week7
python -m uvicorn server_example:app --host 127.0.0.1 --port 8088
```

client:

```bash
python client_example.py
```

หลักจำ:

```text
อยู่ repo root  -> Week7.server_example:app
อยู่ Week7      -> server_example:app
```

---

# Part G — Tests

## 27. `test_server_example.py` ทำงานอย่างไร

ไฟล์ทดสอบใช้ standard library `unittest` และ `httpx.ASGITransport`

```python
transport = httpx.ASGITransport(app=app)
```

ข้อดีคือ:

- เรียก FastAPI app ใน process เดียวกัน
- ไม่ต้องเปิด Uvicorn
- ไม่ต้องใช้ port 8088
- ไม่ต้องพึ่ง network ห้องเรียน
- ทดสอบ response ได้เร็วและคงที่กว่า live server

helper `request()` สร้าง client ที่มี:

```python
base_url="http://test"
```

URL นี้เป็น base URL สำหรับ in-process transport ไม่ได้ส่งออก internet

---

## 28. ทำไมต้อง reset ก่อนแต่ละ test

```python
def setUp(self):
    reset_coupon_state()
```

`unittest` เรียก `setUp()` ก่อนทุก test เพื่อไม่ให้ state จาก test แรกไหลไป test ถัดไป

ถ้าไม่ reset:

- index อาจเริ่มจาก 2 แทน 0
- test อาจได้ `COUPON_03` แทน `COUPON_01`
- นักศึกษาอาจติด `LIMIT_REACHED`
- test อาจผ่านหรือพังตามลำดับการรัน

Test ที่ดีควร isolated และเริ่มจาก state ที่รู้แน่นอน

---

## 29. Test case ที่มีอยู่

### 29.1 `test_my_coupons_returns_only_requested_students_claims`

ลำดับ:

1. เลือก `STUDENTS[0]`
2. POST `/claim` ครั้งที่ 1
3. POST `/claim` ครั้งที่ 2
4. GET `/my-coupons/{student_id}`
5. ตรวจว่า POST ทั้งสองได้ `SUCCESS`
6. ตรวจว่า GET ได้ HTTP 200
7. ตรวจ JSON แบบ exact equality

Expected JSON:

```json
{
  "student_id": "6710301017",
  "total_claimed": 2,
  "claimed_coupons": ["COUPON_01", "COUPON_02"]
}
```

### 29.2 `test_my_coupons_rejects_unknown_student`

เรียก:

```text
GET /my-coupons/unknown
```

Expected:

```text
HTTP 404
response["detail"] == "ไม่พบรายชื่อในระบบ"
```

---

## 30. คำสั่งรัน test

จาก repo root:

```bash
python -m unittest discover -s Week7 -p "test_server_example.py" -v
```

Expected result:

```text
Ran 2 tests
OK
```

ไม่ต้องเปิด server ก่อนรัน test เพราะใช้ `ASGITransport`

---

## 31. Test นี้ยืนยันอะไร และยังไม่ยืนยันอะไร

### ยืนยันแล้ว

- claim สองครั้งแบบ sequential สำเร็จ
- คูปองเริ่มที่ `COUPON_01`, `COUPON_02`
- personal summary คืนเฉพาะคนที่ขอ
- unknown student ที่ personal endpoint ได้ HTTP 404
- reset ทำให้ test เริ่มจาก state ใหม่

### ยังไม่ได้ยืนยัน

- concurrent requests ไม่ได้คูปองซ้ำ
- lock ป้องกัน race จริง
- claim ครั้งที่ 3 ได้ `LIMIT_REACHED`
- invalid student ที่ `/claim` ได้ `INVALID_STUDENT`
- เมื่อแจกครบ 11 ใบ request ถัดไปได้ `OUT_OF_STOCK`
- `/summary` คำนวณ stock ถูกต้อง
- นักศึกษา 6 คนไม่มีใครเกิน 2 ใบ

ข้อสอบชอบถามประเด็นนี้:

> Test ผ่านไม่ได้แปลว่าทุก requirement ผ่าน โดยเฉพาะถ้า test ไม่สร้าง concurrency

---

# Part H — Expected Status และ Error Matrix

## 32. ตารางสถานะสำคัญ

| เหตุการณ์ | HTTP status | JSON/application status | ใช้กับ route |
|---|---:|---|---|
| claim สำเร็จ | 200 | `SUCCESS` | `POST /claim` |
| นักศึกษาไม่อยู่ในระบบ | 200 | `INVALID_STUDENT` | `POST /claim` |
| นักศึกษาครบ 2 ใบ | 200 | `LIMIT_REACHED` | `POST /claim` |
| คูปองหมด | 200 | `OUT_OF_STOCK` | `POST /claim` |
| personal summary สำเร็จ | 200 | ไม่มี field `status` | example `GET /my-coupons/{id}` |
| personal summary ไม่พบนักศึกษา | 404 | `detail` | example `GET /my-coupons/{id}` |
| path ไม่มีใน server | 404 | FastAPI `Not Found` | เช่น `/my-coupons` บน `server.py` |
| request body ไม่ครบ | 422 | FastAPI validation detail | `POST /claim` |
| server ไม่ได้เปิด/URL ผิด | ไม่มี HTTP response | `httpx` connection error | client |

อย่าสับสน:

```text
HTTP 200 + {"status": "LIMIT_REACHED"}
```

หมายถึง HTTP request ไปถึงและ server ประมวลผลสำเร็จ แต่ผลทางธุรกิจคือรับเพิ่มไม่ได้

---

# Part I — Pitfalls ที่พบบ่อย

## 33. จุดผิดพลาดที่ต้องระวัง

### 33.1 คิดว่า async thread เดียวไม่มี race

ผิด เพราะ coroutine สลับกันตรง `await` และสามารถอ่าน state เก่าคนละช่วงได้

### 33.2 Lock เฉพาะบรรทัด append หรือบรรทัดเพิ่ม index

ไม่พอ เพราะ validation/check ต้องอยู่ใน transaction ทางตรรกะเดียวกับการแก้ข้อมูล

### 33.3 ใช้ client sequential เพื่อพิสูจน์ว่าไม่มี race

ทำไม่ได้ เพราะ request ไม่ overlap การทดสอบ race ต้องสร้าง concurrency

### 33.4 รัน client ก่อน server

จะได้ connection error เพราะไม่มี process ฟัง port 8088

### 33.5 รัน local server แต่ใช้ `client.py`

`client.py` ส่งไป `172.20.58.26` ไม่ใช่ `127.0.0.1`

### 33.6 ใช้ `client_example.py` กับ `server.py`

claim ได้ แต่พอเรียก `/my-coupons` จะได้ 404 และ `raise_for_status()` ทำให้เกิด HTTP error

### 33.7 คิดว่า `0.0.0.0` คือ URL สำหรับ client

`0.0.0.0` ใช้ฝั่ง server เพื่อ bind ทุก interface ส่วน local client ควรเรียก `127.0.0.1`

### 33.8 สับสน `COUPON-01` กับ `COUPON_01`

vulnerable ใช้ขีดกลาง แต่ protected/example และ test ใช้ขีดล่าง

### 33.9 เปิดหลาย server บน port เดียวกัน

จะเกิด address already in use ต้องหยุด process เดิมก่อน

### 33.10 State ค้างระหว่างการทดลอง

server เก็บ state ใน memory ถ้ารัน client ซ้ำโดยไม่ restart/reset อาจเริ่มด้วย `LIMIT_REACHED` หรือ stock ที่ลดแล้ว

### 33.11 คิดว่า Lock ทำงานข้ามหลาย worker

`asyncio.Lock` object ไม่ได้แชร์ข้าม process

### 33.12 อ่าน `remaining_stock` อย่างเดียวแล้วสรุปว่าไม่มี race

ใน vulnerable server pointer อาจเพิ่มไม่ครบจำนวน claim เพราะ lost update จึงต้องตรวจทั้ง:

- คูปองซ้ำหรือไม่
- จำนวน claims รวม
- index/remaining stock
- per-student limit

---

# Part J — แบบฝึกหัด

## 34. Exercise 1 — ระบุ Critical Section

จากขั้นตอนต่อไปนี้ ให้เลือกว่าข้อใดควรอยู่ใน lock:

```text
A. ตรวจ student id
B. ตรวจจำนวนคูปองที่ student มี
C. ตรวจ stock
D. อ่าน index
E. เลือก coupon
F. append claim
G. อัปเดต index
H. print log ที่ไม่ใช้ shared state
```

คำถาม:

1. ถ้า B อยู่นอก lock จะเกิดอะไรได้
2. ถ้า C อยู่นอก lock จะเกิดอะไรได้
3. H จำเป็นต้องอยู่ใน lock หรือไม่ เพราะอะไร

---

## 35. Exercise 2 — วาด Timeline

กำหนดว่า:

```text
current_coupon_index = 5
Request A และ B เข้า server_vulnerable พร้อมกัน
```

ให้ตอบ:

1. A และ B อ่าน `index_to_claim` เท่าไร
2. แต่ละ request ได้ชื่อคูปองอะไร
3. index สุดท้ายเท่าไร
4. มี claim เพิ่มกี่รายการ
5. lost update อยู่ตรงไหน

---

## 36. Exercise 3 — API Contract Check

จับคู่ client/server ต่อไปนี้ แล้วทำนายผล:

| Client | Server | คำถาม |
|---|---|---|
| `client_example.py` | `server_example.py` | ทุก endpoint ครบหรือไม่ |
| `client_example.py` | `server.py` | พังที่ request ใด |
| `client.py` | local `server_example.py` | URL ชี้ถึงกันหรือไม่ |
| `client.py` | classroom server | ต้องมี route ใดบ้าง |

ให้แยกว่า failure เป็น:

- connection error
- HTTP 404
- application status
- race condition

---

## 37. Exercise 4 — ออกแบบ Concurrent Test

โดยไม่แก้ production code ให้ออกแบบ test ที่:

1. reset state
2. เลือกนักศึกษาต่างกันหลายคน
3. ส่ง `POST /claim` หลาย request แบบ overlap
4. รวม `claimed_coupon` ที่ status เป็น `SUCCESS`
5. ตรวจว่า coupon ไม่มีค่าซ้ำ
6. ตรวจว่าแต่ละคนไม่เกิน 2 ใบ
7. ตรวจว่าจำนวน success สอดคล้องกับ remaining stock

คำถามสำคัญ:

- ถ้าทดสอบ `server_vulnerable.py` ควรคาดว่าจะเห็นอะไร
- ถ้าทดสอบ `server_example.py` ควรคาดว่าจะเห็นอะไร
- ทำไม sequential test เดิมจึงไม่พอ

---

## 38. Exercise 5 — Status Reasoning

ทำนาย HTTP status และ application status:

1. POST `/claim` ด้วย student ที่ไม่มีในระบบ
2. POST `/claim` ครั้งที่ 3 ของคนที่ได้ครบ 2 ใบ
3. GET `/my-coupons/unknown` บน example server
4. GET `/my-coupons/6710301033` บน `server.py`
5. POST `/claim` ด้วย `{}`
6. เรียก `127.0.0.1:8088` ขณะที่ server ปิด

---

## 39. Exercise 6 — คิดเรื่อง Fairness

แม้ lock ป้องกันข้อมูลพัง แต่ตอบคำถามต่อไปนี้:

1. Lock รับประกันหรือไม่ว่านักศึกษาทุกคนจะได้อย่างน้อย 1 ใบ
2. ถ้านักศึกษาคนหนึ่งส่งเร็วมากจนได้ 2 ใบก่อนคนอื่น ถือว่าผิด max-limit หรือไม่
3. ถ้าต้องการ fairness แบบแจกคนละ 1 ใบก่อน ควรเพิ่มกฎธุรกิจอะไร
4. Correctness, fairness และ performance เป็นเรื่องเดียวกันหรือไม่

---

# Part K — แนวคำตอบสั้นสำหรับ Exercise

## 40. เฉลยแนวคิด

### Exercise 1

A–G เกี่ยวข้องกับการตัดสินใจ/เปลี่ยน shared state จึงควรอยู่ใน critical section เดียวกันสำหรับ implementation นี้ ส่วน H อาจย้ายออกได้ถ้า log ไม่ต้องอ่าน state ที่กำลังเปลี่ยนและไม่ต้องรักษาลำดับแบบ exact

### Exercise 2

ทั้งคู่มีโอกาสอ่าน index 5, ได้ `COUPON-06` ซ้ำ และต่างเขียน index เป็น 6 สุดท้าย claim เพิ่ม 2 รายการแต่ pointer เพิ่มเพียง 1

### Exercise 3

- example client + example server: contract ครบ
- example client + `server.py`: 404 ที่ personal summary และ `raise_for_status()` โยน error
- `client.py` + local example: ไม่ถึงกัน เพราะ client ชี้ classroom IP
- classroom server ต้องมี `/claim`, `/my-coupons/{id}`, `/summary` เพื่อให้ `client.py` ทำครบ

### Exercise 4

vulnerable server อาจคืน coupon ซ้ำและ accounting ไม่สอดคล้อง ส่วน protected example ควรให้ unique coupon ตาม stock/limit แต่ต้องใช้ concurrent requests จึงจะทดสอบประเด็น race ได้

### Exercise 5

1. HTTP 200 + `INVALID_STUDENT`
2. HTTP 200 + `LIMIT_REACHED`
3. HTTP 404 + `detail`
4. HTTP 404 เพราะ route ไม่มี
5. HTTP 422 validation error
6. connection error ไม่มี HTTP status

### Exercise 6

Lock รับประกัน mutual exclusion ไม่ได้รับประกัน fairness ทางธุรกิจ การได้ 2 ใบยังไม่ผิด max-limit แต่ถ้าต้องการแจกทั่วถึงต้องเพิ่ม policy เช่นรอบแรกทุกคนรับได้คนละ 1 ใบก่อน Correctness, fairness และ performance เป็นคนละมิติ

---

# Part L — Exam Recap

## 41. สรุปก่อนสอบแบบจำเร็ว

### 41.1 สูตรและค่าที่ต้องจำ

```text
นักศึกษา = 6 คน
สูงสุด = 2 ใบ/คน
ความต้องการสูงสุด = 12 ใบ
TOTAL_COUPONS = 11 ใบ
จึงขาดจาก maximum demand 1 ใบ
```

### 41.2 Shared state

```text
coupons_db
current_coupon_index
student_claims
```

### 41.3 Race pattern

```text
Read -> await -> Modify -> Write
```

ถ้าหลาย request อ่านค่าเดิมก่อนเขียน จะเกิด duplicate/lost update

### 41.4 Critical section

```text
Validate -> Check limit -> Check stock
-> Read index -> Assign coupon -> Append claim -> Update index
```

ต้องถูกป้องกันเป็นชุดเดียว

### 41.5 Lock pattern

```python
coupon_lock = asyncio.Lock()

async with coupon_lock:
    # critical section
```

มีเพียง coroutine ที่ถือ lock เท่านั้นที่เข้าช่วงนี้ได้

### 41.6 Server files

```text
server_vulnerable.py = ไม่มี lock + COUPON-01
server.py            = มี lock + COUPON_01 แต่ไม่มี /my-coupons
server_example.py    = มี lock + /my-coupons + reset helper + local run
```

### 41.7 Client files

```text
client.py         = classroom URL 172.20.58.26:8088
client_example.py = local URL 127.0.0.1:8088
```

### 41.8 API routes

```text
POST /claim
GET  /summary
GET  /my-coupons/{student_id}  # เฉพาะ server_example.py ในชุดนี้
```

### 41.9 Status ที่ต้องแยก

```text
SUCCESS
INVALID_STUDENT
LIMIT_REACHED
OUT_OF_STOCK
```

ทั้งหมดข้างบนเป็น application status ของ `/claim` และในโค้ดนี้มากับ HTTP 200

```text
404 = route/resource ไม่พบ
422 = request body validation ไม่ผ่าน
connection error = ยังไม่มี HTTP response
```

### 41.10 Test recap

```text
ASGITransport = test app โดยไม่เปิด port
setUp + reset  = test isolation
มี 2 tests     = personal summary success และ unknown student 404
ยังไม่มี concurrent race test
```

---

## 42. Checklist ก่อนส่งงานหรือเข้าสอบ

- [ ] อธิบาย race condition timeline ได้
- [ ] ชี้จุด `await` ที่เปิด interleaving window ได้
- [ ] อธิบาย duplicate coupon และ lost update ได้
- [ ] ระบุ critical section ครบตั้งแต่ check ถึง update ได้
- [ ] อธิบาย `async with coupon_lock` ได้
- [ ] จำว่า 6 คน × 2 - 1 = 11 คูปองได้
- [ ] จำ max 2 claims ต่อคนได้
- [ ] แยก local URL กับ classroom URL ได้
- [ ] รู้ว่า `server.py` ไม่มี `/my-coupons`
- [ ] แยก HTTP status กับ application status ได้
- [ ] รู้ว่า sequential client ไม่ได้พิสูจน์ว่าไม่มี race
- [ ] รัน example server/client และ unit tests ด้วยคำสั่งที่ถูกต้องได้
- [ ] รู้ขอบเขตว่า `asyncio.Lock` ไม่ได้แชร์ข้ามหลาย process

---

## 43. สรุปสุดท้าย

บทเรียน Week 7 แสดงให้เห็นว่าโค้ด async อาจให้ผลผิดได้แม้ไม่มี thread หลายตัว เพราะ coroutine สามารถสลับกันตรง `await` ได้ `server_vulnerable.py` อ่าน index แล้วพัก ทำให้ request อื่นอ่าน index เดียวกันและแจกคูปองซ้ำ ส่วน `server.py` และ `server_example.py` ใช้ `asyncio.Lock` ครอบการตรวจและแก้ shared state ทั้งชุด จึงทำให้หนึ่ง claim เสร็จสมบูรณ์ก่อนอีก claim เข้ามา

นอกจาก concurrency แล้ว ต้องตรวจ API contract ด้วย: `client.py` เรียก `/my-coupons/{student_id}` แต่ `server.py` ไม่มี route นี้ จึงเกิด 404 แม้ logic การ claim มี lock ถูกต้อง คู่ local ที่ใช้งานครบคือ `client_example.py` กับ `server_example.py` และ test ที่มีอยู่ตรวจ personal summary สองกรณี แต่ยังไม่ได้ทดสอบ race แบบ concurrent

> ประโยคจำก่อนสอบ: **ข้อมูลร่วม + check แล้วมี await ก่อน update + ไม่มี lock = เปิดโอกาสให้ race condition**
