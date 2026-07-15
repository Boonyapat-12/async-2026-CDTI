# Week 4 Smart Lab Lighting Async Client Implementation Plan

> **For Hermes:** Use `subagent-driven-development` and `test-driven-development` skills to implement this plan task-by-task.

**Goal:** สร้างชุดโปรแกรม Python แบบ async ให้ใบควบคุมไฟจำลอง 4 ดวงของรหัส `6710301033` ผ่าน REST API ของอาจารย์ พร้อมเปรียบเทียบ sequential กับ concurrent และมีคู่มืออ่านก่อนสอบ

**Architecture:** ใช้ `httpx.AsyncClient` เป็น HTTP client และแยกฟังก์ชัน API ที่ใช้ซ้ำไว้ใน `light_utils.py` ส่วนไฟล์ตัวอย่างขนาดเล็กจะแสดงการอ่านสถานะ ควบคุมไฟหนึ่งดวง รีเซ็ต และเปรียบเทียบ sequential/concurrent โดยหน้า Dashboard เดิมรับ WebSocket broadcast และแสดงผลให้เอง ไม่สร้าง Server หรือ Dashboard ใหม่

**Tech Stack:** Python 3.12, `asyncio`, `httpx`, stdlib `unittest`, `httpx.MockTransport`

---

## Execution adjustment from Bai (2026-07-15)

This section overrides later draft filenames where they conflict:

- Use the two exact empty starter files now present: `Week4/light/light_01.py` and `Week4/light/light_02.py`.
- `light_01.py` will demonstrate the sequential REST flow.
- `light_02.py` will demonstrate concurrent control with `asyncio.gather()`.
- Do not create `light_03_*`, `light_04_*`, or `light_05_*`; they would be unnecessary scope beyond the provided starters.
- Save the separate exam study guide at project root as `Week4_Asyncio_Smart_Lab_Light_Guide.md`, not inside `Week4/light/`.
- The original API specification `Week4/light/Readme.md` remains unchanged.

---

## 1. Source of truth และขอบเขต

### Source of truth

- API specification: `Week4/light/Readme.md`
- Live HTTP base URL: `http://172.16.2.117:8088`
- Dashboard: `http://172.16.2.117:8088/6710301033`
- Student ID: `6710301033`
- Starter file ที่พบระหว่างวางแผน: `Week4/light/light_01.py` (ไฟล์ว่าง 0 bytes) — ต้องใช้ชื่อเดิมนี้แทนการสร้างชื่อใหม่

### REST endpoints ที่ต้องรองรับ

| Operation | Method | Endpoint |
|---|---|---|
| อ่านสถานะทั้งหมด | `GET` | `/api/{student_id}/lights` |
| เปิด/ปิดไฟหนึ่งดวง | `POST` | `/api/{student_id}/lights/{light_id}` |
| รีเซ็ตไฟทั้งหมด | `DELETE` | `/api/{student_id}/lights/reset` |

### สิ่งที่จะไม่สร้าง

- ไม่สร้าง FastAPI server ใหม่ เพราะ Server ของอาจารย์มีอยู่แล้ว
- ไม่สร้างหน้า Dashboard ใหม่ เพราะหน้าเดิมใช้ WebSocket แสดงผลแบบ real-time อยู่แล้ว
- ไม่เขียน WebSocket client ใน scope หลัก เพราะ README ระบุว่า channel นี้มีไว้สำหรับ Web Dashboard frontend
- ไม่เพิ่ม database, configuration framework หรือ abstraction ที่เกินงาน classroom
- ไม่แก้ `Week4/light/Readme.md` ซึ่งเป็น specification ต้นฉบับ

---

## 2. Critique และแนวทางที่ปลอดภัยกว่า

### จุดเสี่ยงที่ต้องแก้ตั้งแต่การออกแบบ

1. **ห้ามเขียน test ให้ยิง Server จริง** — จะเปลี่ยนสถานะไฟของใบและทำให้ test ไม่ deterministic
2. **การ cancel HTTP POST ไม่ได้แปลว่า Server rollback** — Server อาจรับคำสั่งไปแล้วแม้ client ยกเลิกการรอ จึงไม่ใช้ `FIRST_COMPLETED` แล้ว cancel คำสั่งควบคุมไฟเป็น core example
3. **Client timeout ไม่รับประกันว่าสถานะไฟไม่เปลี่ยน** — ถ้าทดลอง `wait_for()` ต้องตรวจสถานะจริงภายหลัง ไม่สมมติว่า timeout เท่ากับคำสั่งล้มเหลว
4. **README ใช้ local URL แต่ระบบจริงใช้ classroom URL** — constants และคู่มือต้องระบุความต่างชัดเจน
5. **ทุก live scenario ต้อง reset อย่างชัดเจน** — ป้องกันสถานะจากรอบก่อนรบกวนผลการทดลอง

### เวอร์ชันที่แนะนำ

สร้าง core lab ที่ปลอดภัยและตรง README ก่อน:

1. GET สถานะ
2. POST ควบคุมหนึ่งดวง
3. DELETE reset
4. เปิดไฟ 4 ดวงแบบ sequential
5. เปิดไฟ 4 ดวงแบบ concurrent ด้วย `gather()`
6. เปรียบเทียบเวลาที่คาด: sequential ประมาณ `4.5s`, concurrent ประมาณ `2.0s`

ส่วน `wait()`, cancellation และ `wait_for()` ให้เป็น **optional extension** หลัง core ผ่าน และต้องอธิบาย side effect caveat

---

## 3. Files ที่วางแผนสร้าง

```text
Week4/light/
├── Readme.md                         # เดิม — ไม่แก้
├── requirements.txt                  # httpx dependency
├── light_utils.py                    # REST helper functions + constants
├── light_01.py                       # starter เดิม — เติมการอ่าน/แสดงสถานะ 4 ดวง
├── light_02_control_one.py            # เปิด/ปิดไฟหนึ่งดวง
├── light_03_sequential.py             # ควบคุมครบ 4 ดวงแบบเรียงกัน
├── light_04_gather.py                 # ควบคุมครบ 4 ดวงพร้อมกัน
├── light_05_compare.py                # reset + เปรียบเทียบเวลา 2 วิธี
├── tests/
│   ├── __init__.py
│   └── test_light_utils.py            # offline API contract tests
└── GUIDE.md                           # คู่มือภาษาไทยจากศูนย์ + วิธีรัน/สอบ
```

> ชื่อไฟล์ข้างต้นเป็นชื่อที่เราออกแบบเองเพื่อให้อ่านง่าย เพราะ README ไม่ได้กำหนดชื่อไฟล์ส่งงาน

---

## 4. Output contract

### `light_01.py`

ต้องแสดงครบ 4 ดวง โดยแต่ละบรรทัดมี:

```text
light_1 | ไฟหน้าประตู (Light 1) | ON | delay=0.5s
```

### `light_02_control_one.py`

- รับ `light_id` และ `ON/OFF` ผ่าน command line
- ตรวจ input ก่อนส่ง request
- แสดง response จริงจาก Server

ตัวอย่างคำสั่ง:

```bash
python Week4/light/light_02_control_one.py light_1 OFF
```

### `light_03_sequential.py`

- reset เป็น OFF ก่อน
- เปิด `light_1` ถึง `light_4` ทีละดวง
- จับเวลาด้วย `perf_counter()`
- เวลาที่คาดเมื่อ network ปกติ: ประมาณ `4.5s` + overhead

### `light_04_gather.py`

- reset เป็น OFF ก่อน
- สร้างคำสั่งเปิดไฟ 4 ดวงพร้อมกัน
- ใช้ `asyncio.gather()`
- แสดงผลตามลำดับ `light_1` ถึง `light_4`
- เวลาที่คาด: ประมาณ `2.0s` + overhead

### `light_05_compare.py`

- รัน sequential และ concurrent ในไฟล์เดียว
- reset ระหว่างการทดลอง
- แสดงเวลาของทั้งสองวิธี
- ตรวจสถานะสุดท้ายด้วย GET
- ห้าม assert เวลาตายตัว เพราะ network latency แกว่งได้

---

## 5. Step-by-step implementation plan

### Task 1: สร้าง feature branch และบันทึก baseline

**Objective:** แยกงานจาก `main` และยืนยันว่าไม่มีการกลืนงานเดิมของใบ

**Files:** ไม่มีไฟล์ใหม่ในขั้นนี้

**Steps:**

1. รัน `git status --short --branch`
2. ถ้า working tree มีไฟล์อื่นนอก `.hermes/plans/` และ starter ว่าง `Week4/light/light_01.py` ให้หยุดและแยกงานเดิมก่อน ห้าม commit รวมโดยเดา
3. บันทึก baseline ด้วย `git rev-parse HEAD`
4. สร้าง branch:

```bash
git switch -c feat/week4-light-async-client
```

5. ยืนยันด้วย `git branch --show-current`

**Verification:** ต้องได้ `feat/week4-light-async-client`

---

### Task 2: เพิ่ม dependency declaration

**Objective:** ทำให้รู้ชัดว่า client ต้องใช้ package อะไร

**Files:**

- Create: `Week4/light/requirements.txt`

**Content:**

```text
httpx
```

**Verification:**

```bash
python -m pip install -r Week4/light/requirements.txt
python -c "import httpx; print(httpx.__version__)"
```

**Commit:**

```bash
git add Week4/light/requirements.txt
git commit -m "build: declare Week4 light client dependency"
```

---

### Task 3: RED — เขียน offline API contract tests

**Objective:** ระบุ behavior ของ REST helper ก่อนมี production code โดยไม่ยิง Server จริง

**Files:**

- Create: `Week4/light/tests/__init__.py`
- Create: `Week4/light/tests/test_light_utils.py`

**Tests ที่ต้องมี:**

1. `get_all_lights()` ส่ง `GET /api/6710301033/lights`
2. `set_light()` ส่ง `POST` พร้อม JSON `{"status": "ON"}`
3. `set_light()` แปลง `off` เป็น `OFF`
4. `set_light()` ปฏิเสธ status ที่ไม่ใช่ `ON/OFF` ก่อนยิง network
5. `set_light()` ปฏิเสธ light ID นอก `light_1`–`light_4`
6. `reset_all_lights()` ส่ง `DELETE /api/6710301033/lights/reset`
7. HTTP 404/400/422 ทำให้เกิด error ที่มีข้อความอ่านรู้เรื่อง
8. response JSON ถูก return ตามข้อมูลจาก Server

**Testing mechanism:** ใช้ `httpx.MockTransport` และ `unittest.IsolatedAsyncioTestCase`

**Run RED:**

```bash
python -m unittest discover -s Week4/light/tests -v
```

**Expected:** FAIL เพราะ `light_utils.py` ยังไม่มี

---

### Task 4: GREEN — สร้าง `light_utils.py`

**Objective:** ทำให้ API contract tests ผ่านด้วย implementation ที่เล็กและอ่านง่าย

**Files:**

- Create: `Week4/light/light_utils.py`

**Public interface:**

```python
BASE_URL = "http://172.16.2.117:8088"
STUDENT_ID = "6710301033"
LIGHT_IDS = ("light_1", "light_2", "light_3", "light_4")

async def get_all_lights(client, student_id=STUDENT_ID): ...
async def set_light(client, light_id, status, student_id=STUDENT_ID): ...
async def reset_all_lights(client, student_id=STUDENT_ID): ...
```

**Design rules:**

- รับ `httpx.AsyncClient` จาก caller เพื่อ reuse connection และ test ง่าย
- ใช้ `response.raise_for_status()`
- return `response.json()`
- validate `light_id` และ normalize `status.upper()`
- ไม่จับ `Exception` กว้าง ๆ ใน helper; ให้ CLI layer แสดง error เพื่อไม่กลบสาเหตุจริง

**Run GREEN:**

```bash
python -m unittest discover -s Week4/light/tests -v
```

**Expected:** tests ทั้งหมด PASS

**Commit:**

```bash
git add Week4/light/light_utils.py Week4/light/tests
git commit -m "feat: add tested Smart Lab light API client"
```

---

### Task 5: สร้าง status และ single-control examples

**Objective:** ให้ใบเข้าใจ GET และ POST ทีละอย่างก่อนเข้าสู่ concurrency

**Files:**

- Modify: `Week4/light/light_01.py` (starter เดิมเป็นไฟล์ว่าง)
- Create: `Week4/light/light_02_control_one.py`

**Implementation rules:**

- ใช้ `asyncio.run(main())`
- เปิด `httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)` หนึ่งครั้งต่อ script
- single-control รับ `light_id` และ `status` จาก `sys.argv`
- แสดง usage เมื่อ argument ไม่ครบ
- จับ `httpx.HTTPError` ที่ CLI boundary และ exit non-zero

**Offline verification:**

```bash
python -m py_compile Week4/light/light_01.py Week4/light/light_02_control_one.py
python Week4/light/light_02_control_one.py
```

Expected สำหรับคำสั่งที่สอง: แสดง usage โดยไม่ยิง Server

**Live verification:**

```bash
python Week4/light/light_01.py
python Week4/light/light_02_control_one.py light_1 OFF
python Week4/light/light_01.py
```

เปิด Dashboard แล้วตรวจว่า `light_1` เปลี่ยนเป็น OFF

**Commit:**

```bash
git add Week4/light/light_01.py Week4/light/light_02_control_one.py
git commit -m "feat: add light status and single-control examples"
```

---

### Task 6: RED/GREEN — เพิ่ม sequential และ gather scenarios

**Objective:** พิสูจน์ความต่างของเวลารอแบบเรียงกันกับ concurrent

**Files:**

- Modify: `Week4/light/tests/test_light_utils.py`
- Create: `Week4/light/light_03_sequential.py`
- Create: `Week4/light/light_04_gather.py`

**RED tests:**

- helper สร้างผลลัพธ์ครบ 4 ดวงตามลำดับที่กำหนด
- concurrent scenario เรียกครบทุก Light ID
- test behavior/requests ไม่ assert เวลาจริง

**GREEN implementation:**

Sequential:

```python
for light_id in LIGHT_IDS:
    result = await set_light(client, light_id, "ON")
```

Concurrent:

```python
results = await asyncio.gather(
    *(set_light(client, light_id, "ON") for light_id in LIGHT_IDS)
)
```

จับเวลาด้วย `perf_counter()` และพิมพ์ผลแต่ละดวง

**Verification:**

```bash
python -m unittest discover -s Week4/light/tests -v
python -m py_compile Week4/light/light_03_sequential.py Week4/light/light_04_gather.py
```

Live:

```bash
python Week4/light/light_03_sequential.py
python Week4/light/light_04_gather.py
```

Expected trend:

- sequential ใกล้ 4.5 วินาที + overhead
- gather ใกล้ 2.0 วินาที + overhead

**Commit:**

```bash
git add Week4/light/tests/test_light_utils.py Week4/light/light_03_sequential.py Week4/light/light_04_gather.py
git commit -m "feat: compare sequential and concurrent light control"
```

---

### Task 7: สร้าง combined comparison runner

**Objective:** ให้ใบสั่งครั้งเดียวแล้วเห็นความต่างครบ พร้อม reset และ final verification

**Files:**

- Create: `Week4/light/light_05_compare.py`

**Flow:**

1. GET สถานะเริ่มต้น
2. DELETE reset
3. รัน sequential ON และวัดเวลา
4. DELETE reset
5. รัน concurrent ON และวัดเวลา
6. GET สถานะสุดท้าย
7. แสดง summary table
8. `finally` reset เป็น OFF เพื่อคืนสถานะสะอาด หรือถามผู้ใช้ผ่าน flag ว่าต้องการคงสถานะไว้

**Safer default:** reset เป็น OFF ใน `finally` เพื่อไม่ทิ้ง state ค้างเมื่อ script error

**Verification:**

```bash
python -m py_compile Week4/light/light_05_compare.py
python Week4/light/light_05_compare.py
```

Expected:

- ได้ response ครบ 4 ดวงทั้งสองรอบ
- concurrent เร็วกว่า sequential ในสภาพ network ปกติ
- Dashboard อัปเดตแบบ real-time
- หลังจบไฟกลับเป็น OFF

**Commit:**

```bash
git add Week4/light/light_05_compare.py
git commit -m "feat: add end-to-end light concurrency comparison"
```

---

### Task 8: เขียนคู่มือภาษาไทย

**Objective:** ให้ใบอ่านจากศูนย์และอธิบายงานตอนสอบได้

**Files:**

- Create: `Week4/light/GUIDE.md`

**Sections:**

1. ระบบนี้คืออะไร
2. Dashboard, REST API และ WebSocket ทำงานร่วมกันอย่างไร
3. Endpoint ทั้งสาม
4. อธิบาย `light_utils.py`
5. อธิบาย example 01–05
6. Sequential 4.5s เทียบ concurrent 2.0s
7. วิธีติดตั้งและรัน
8. Expected behavior โดยไม่ปลอม timestamp/output
9. Error 400/404/422 และ connection failure
10. ข้อควรระวังเรื่อง timeout/cancel กับ side effects
11. คำถามแนวสอบ
12. Cheat sheet

**Documentation validation:**

- ตรวจ code fences สมดุล
- ตรวจชื่อไฟล์ใน GUIDE ว่ามีอยู่จริง
- ไม่ทำเนื้อหาซ้ำกับ `Week4/light/Readme.md`; GUIDE อธิบายวิธีเรียนและรัน ส่วน README เป็น API spec

**Commit:**

```bash
git add Week4/light/GUIDE.md
git commit -m "docs: add Week4 Smart Lab lighting study guide"
```

---

### Task 9: Final verification และ handoff

**Objective:** ยืนยัน artifact จริงก่อนรายงานว่าเสร็จ

**Commands:**

```bash
python -m unittest discover -s Week4/light/tests -v
python -m py_compile Week4/light/*.py
python Week4/light/light_01.py
python Week4/light/light_05_compare.py
git diff --check
git status --short
git log --oneline --decorate -10
```

**Acceptance criteria:**

- tests ผ่านทั้งหมด
- Python compile ผ่านทุกไฟล์
- GET คืนข้อมูลครบ `light_1`–`light_4`
- POST เปลี่ยนสถานะและ Dashboard แสดงผล
- DELETE reset ทุกดวงเป็น OFF
- sequential และ gather ทำงานครบ 4 ดวง
- concurrent เร็วกว่า sequential ในการทดสอบจริง หรือบันทึก network anomaly อย่างตรงไปตรงมา
- หลังจบ live test ไฟทั้ง 4 ดวงเป็น OFF
- ไม่มีการแก้ `Week4/light/Readme.md`
- ไม่มี secrets หรือ `.env` ถูกสร้าง

---

## 6. Optional extension — ทำเมื่ออาจารย์ระบุเท่านั้น

### `wait_for()` timeout experiment

- ทดลอง `light_3` delay 2.0s กับ client timeout ที่สั้นกว่า
- หลัง timeout รอแล้ว GET สถานะอีกครั้ง
- อธิบายว่า client timeout ไม่รับประกัน Server rollback

### WebSocket observer

- สร้างเฉพาะเมื่อโจทย์กำหนดให้เขียน WebSocket client
- เชื่อม `ws://172.16.2.117:8088/ws/6710301033`
- รับ full-state JSON ทุกครั้งที่สถานะเปลี่ยน
- ไม่จำเป็นสำหรับ core scope เพราะ Dashboard เดิมทำหน้าที่นี้แล้ว

---

## 7. Git Strategy

Branch: `feat/week4-light-async-client`

| # | Type | Commit message | Files |
|---:|---|---|---|
| 1 | Build | `build: declare Week4 light client dependency` | `requirements.txt` |
| 2 | Test + Feature | `feat: add tested Smart Lab light API client` | `light_utils.py`, `tests/*` |
| 3 | Feature | `feat: add light status and single-control examples` | example 01–02 |
| 4 | Feature | `feat: compare sequential and concurrent light control` | example 03–04, tests |
| 5 | Feature | `feat: add end-to-end light concurrency comparison` | example 05 |
| 6 | Docs | `docs: add Week4 Smart Lab lighting study guide` | `GUIDE.md` |

Rules:

- ไม่ commit ลง `main` โดยตรง
- ไม่รวม modified files เดิมของใบเข้า commit
- commit ทุก phase หลัง test ผ่าน
- ไม่ push จนทุก phase และ live verification ผ่าน
- ไม่ push เว้นแต่ใบสั่งโดยตรง

---

## 8. Risks และ open questions

| Risk / Question | Plan response |
|---|---|
| README ไม่กำหนดชื่อไฟล์ส่งงาน | ใช้ชื่อที่อ่านง่าย และแจ้งว่าเป็นชื่อที่เราออกแบบเอง |
| Server ห้องเรียนปิดหรือเข้าไม่ได้ | unit tests ยังต้องผ่าน; รายงาน live test ว่าถูก block โดย network |
| Network latency แกว่ง | เปรียบเทียบแนวโน้ม ไม่ assert วินาทีตายตัว |
| POST ถูก cancel แต่ Server ทำต่อ | ไม่ใช้ cancel เป็น core pattern สำหรับ side-effecting API |
| Student ID อาจต้องเปลี่ยน | รวมเป็น constant จุดเดียวใน `light_utils.py` |
| อาจารย์ต้องการ output/ชื่อฟังก์ชันเฉพาะ | ถ้ามี screenshot/ใบงานใหม่ ต้องถือเป็น grading contract และปรับแผนก่อน implement |

---

## 9. Definition of done

งานถือว่าเสร็จเมื่อใบสามารถ:

1. เปิด Dashboard ของรหัสตัวเอง
2. รัน Python เพื่ออ่านสถานะไฟ
3. เปิด/ปิดไฟเฉพาะดวง
4. reset ไฟทั้งหมด
5. รัน sequential และ concurrent comparison
6. เห็น Dashboard เปลี่ยน real-time
7. อธิบายได้ว่าเหตุใด sequential ใช้ประมาณ 4.5s แต่ gather ใช้ประมาณ 2.0s
8. รัน unit tests แล้วผ่านโดยไม่เปลี่ยนสถานะ Server จริง
9. ใช้ `GUIDE.md` ทบทวนก่อนสอบได้
