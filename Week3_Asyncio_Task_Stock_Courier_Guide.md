# Week 3 Asyncio Task, Courier, and Stock Price Guide

คู่มือนี้เขียนจากโค้ดจริงล่าสุดในโฟลเดอร์ `Week3` ของใบค่ะ

ไฟล์ที่ใช้เรียนแบ่งเป็น 2 กลุ่มใหญ่:

1. **Example** — ไฟล์ `task_01` ถึง `task_10` ใช้เรียนคำสั่งย่อย ๆ ของ `asyncio.Task`
2. **Lab / Assignment** — ไฟล์งานจริง 4 ไฟล์ ได้แก่
   - `Week3/smart_courier.py`
   - `Week3/stock_price.py`
   - `Week3/stock_api.py`
   - `Week3/stock_price_httpx.py`

> เป้าหมาย: ให้ใบเข้าใจว่า Task ใน `asyncio` สร้างยังไง ตรวจสถานะยังไง ยกเลิกยังไง แข่ง task ด้วย `FIRST_COMPLETED` ยังไง และเอาไปใช้กับ HTTP request จริงผ่าน `httpx` ยังไง

---

## 1. ภาพรวม Week 3

Week 3 เน้นเรื่อง **Task Control** ใน `asyncio`

ถ้า Week 2 คือ “ทำหลายงานพร้อมกันได้ยังไง”  
Week 3 คือ “เมื่อสร้างงาน async แล้ว เราจะควบคุมมันยังไง”

สิ่งที่ต้องเข้าใจ:

| เรื่อง | ใช้ทำอะไร | ไฟล์ตัวอย่าง |
|---|---|---|
| `asyncio.create_task()` | สร้างงาน async ให้ event loop ดูแล | `task_01`, `smart_courier`, `stock_price` |
| `.done()` | เช็กว่า task เสร็จหรือยัง | `task_01`, `smart_courier` |
| `.cancel()` | สั่งยกเลิก task | `task_03`, `smart_courier`, `stock_price` |
| `.cancelled()` | เช็กว่า task ถูกยกเลิกจริงไหม | `task_01`, `smart_courier` |
| `asyncio.CancelledError` | exception ที่เกิดเมื่อ task ถูก cancel | `task_03`, `smart_courier` |
| `.result()` | อ่านค่าที่ task return กลับมา | `task_02`, `stock_price` |
| `.exception()` | ดูว่า task พังด้วย error อะไร | `task_02` |
| `.add_done_callback()` | ผูก function ให้ทำงานตอน task เสร็จ | `task_04` |
| `.get_name()` / `.set_name()` | อ่าน/ตั้งชื่อ task | `task_05`, `smart_courier` |
| `asyncio.current_task()` | ดู task ที่กำลังทำงานอยู่ตอนนี้ | `task_06` |
| `asyncio.all_tasks()` | ดู task ทั้งหมดใน event loop | `task_06` |
| `asyncio.gather()` | รอหลายงานให้เสร็จทั้งหมด | `task_07` |
| `asyncio.wait()` | รอหลายงานแบบควบคุมเงื่อนไขได้ | `task_08`, `stock_price` |
| `asyncio.FIRST_COMPLETED` | หยุดรอทันทีเมื่อมี task ตัวแรกเสร็จ | `task_08`, `stock_price`, `stock_price_httpx` |
| `asyncio.wait_for()` | จำกัดเวลารอ ถ้าเกินให้ timeout | `task_09` |
| `httpx.AsyncClient()` | ยิง HTTP request แบบ async | `stock_price_httpx` |

---

## 2. คำศัพท์สำคัญก่อนอ่านโค้ด

| คำ | ความหมายง่าย ๆ |
|---|---|
| coroutine | function แบบ async ที่ยังไม่เริ่มทำงานจริงจนกว่าจะ await หรือ create_task |
| task | coroutine ที่ถูกส่งเข้า event loop แล้ว พร้อมให้ระบบจัดการ |
| event loop | ตัวกลางที่คอยสลับงาน async หลายงาน |
| await | จุดที่งานยอมรอ และเปิดโอกาสให้งานอื่นทำต่อ |
| pending | task ที่ยังไม่เสร็จ |
| done | task ที่เสร็จแล้ว ไม่ว่าจะสำเร็จ พัง หรือถูกยกเลิก |
| cancel | การส่งสัญญาณให้ task หยุดทำงาน |
| callback | function ที่ถูกเรียกอัตโนมัติเมื่อ task เสร็จ |
| latency | ความหน่วง / เวลารอของ network หรือ server |
| HTTP request | การส่งคำขอไปยัง server เช่น GET `/price/Beta` |

---

## 3. Example Section — `task_01` ถึง `task_10`

ส่วนนี้คือไฟล์ตัวอย่างย่อยที่ปูพื้นก่อนทำ Lab จริงค่ะ

---

### Example 1 — `task_01_status.py`

#### แนวคิด

ไฟล์นี้สอนการเช็กสถานะ task ว่า:

- เสร็จหรือยังด้วย `.done()`
- ถูกยกเลิกหรือยังด้วย `.cancelled()`

#### Flow

```text
สร้าง task -> เช็กทันที -> ยังไม่เสร็จ
await task -> task เสร็จ
เช็กอีกครั้ง -> done เป็น True
```

#### จุดสำคัญ

```python
task = asyncio.create_task(short_job())
```

บรรทัดนี้สร้าง task จาก coroutine `short_job()`

```python
task.done()
```

ใช้ตอบว่า “งานเสร็จแล้วหรือยัง”

```python
task.cancelled()
```

ใช้ตอบว่า “งานนี้ถูก cancel หรือเปล่า”

#### Lab ย่อย

ลองเปลี่ยน `asyncio.sleep(1)` เป็น `asyncio.sleep(3)` แล้วดูว่า `.done()` ก่อน await ยังเป็น `False` อยู่ไหม

---

### Example 2 — `task_02_exception.py`

#### แนวคิด

ไฟล์นี้สอนว่า task มีได้ 2 แบบ:

1. task สำเร็จ และมี result
2. task พัง และมี exception

#### Flow

```text
สร้าง task_success -> 10 / 2 -> สำเร็จ
สร้าง task_fail -> 10 / 0 -> ZeroDivisionError
รอให้ทั้งคู่จบ
อ่าน result ของตัวที่สำเร็จ
อ่าน exception ของตัวที่พัง
```

#### จุดสำคัญ

```python
task_success.result()
```

อ่านค่าที่ coroutine return กลับมา

```python
task_fail.exception()
```

อ่าน error ที่เกิดใน task โดยไม่ทำให้ main loop พังทันที

#### Lab ย่อย

ลองเปลี่ยน `division_worker(10, 0)` เป็น `division_worker(10, 5)` แล้วดูว่า exception หายไปไหม

---

### Example 3 — `task_03_cancel.py`

#### แนวคิด

ไฟล์นี้สอนการหยุด task ที่กำลังทำงานไม่จบ เช่น loop ไม่รู้จบ

#### Flow

```text
background_loop เริ่มทำงาน
main รอ 2.5 วินาที
task.cancel()
background_loop จับ CancelledError แล้ว print cleanup
```

#### จุดสำคัญ

```python
task.cancel()
```

ส่งสัญญาณยกเลิก task

```python
except asyncio.CancelledError:
```

ใช้รับมือเมื่อ task ถูก cancel เพื่อ cleanup ก่อนออก

#### Lab ย่อย

ลองเปลี่ยนเวลารอใน main จาก `2.5` เป็น `4.5` แล้วดูว่า worker tick กี่ครั้งก่อนโดน cancel

---

### Example 4 — `task_04_callback.py`

#### แนวคิด

ไฟล์นี้สอน callback คือ function ที่จะถูกเรียกอัตโนมัติเมื่อ task เสร็จ

#### Flow

```text
สร้าง task ดาวน์โหลดไฟล์
ผูก callback ด้วย add_done_callback
เมื่อ task เสร็จ callback จะอ่าน result แล้ว print
```

#### จุดสำคัญ

```python
task.add_done_callback(alert_manager)
```

แปลว่าเมื่อ `task` เสร็จ ให้เรียก `alert_manager(task)` อัตโนมัติ

#### Lab ย่อย

ลองเพิ่ม callback อีกตัว เช่น `log_finished_task()` แล้วผูก callback 2 ตัวกับ task เดียวกัน

---

### Example 5 — `task_05_nameing.py`

> หมายเหตุ: ชื่อไฟล์เป็น `nameing` ตามไฟล์จริงของโปรเจกต์ แม้คำอังกฤษมาตรฐานจะเป็น `naming`

#### แนวคิด

ไฟล์นี้สอนการตั้งชื่อ task เพื่อช่วย debug

#### จุดสำคัญ

```python
task.get_name()
```

อ่านชื่อ task ปัจจุบัน

```python
task.set_name("Payment-Gateway-Validator")
```

เปลี่ยนชื่อ task ให้สื่อความหมาย

#### Lab ย่อย

ลองตั้งชื่อ task เป็นงานอื่น เช่น `Email-Sender` แล้วดู output ที่ได้

---

### Example 6 — `task_06_loop_introspection.py`

#### แนวคิด

ไฟล์นี้สอนการดูว่าใน event loop ตอนนี้มี task อะไรทำงานอยู่บ้าง

#### จุดสำคัญ

```python
asyncio.current_task()
```

ดู task ปัจจุบันที่กำลังรันอยู่

```python
asyncio.all_tasks()
```

ดู task ทั้งหมดที่ยัง active ใน loop

#### Lab ย่อย

ลองเปลี่ยน `range(3)` เป็น `range(5)` แล้วดูว่า Total Active Tasks เพิ่มขึ้นไหม

---

### Example 7 — `task_07_gather.py`

#### แนวคิด

`asyncio.gather()` ใช้รันหลาย coroutine พร้อมกัน แล้วรอให้เสร็จทั้งหมด

#### Flow

```text
Users ใช้ 1.0 วิ
Products ใช้ 0.5 วิ
Invoices ใช้ 1.0 วิ
gather รอทั้งหมด
คืน list ผลลัพธ์ตามลำดับที่ส่งเข้าไป
```

#### จุดสำคัญ

```python
results = await asyncio.gather(...)
```

แม้ Products จะเสร็จก่อน แต่ list ยังเรียงตามลำดับที่เราใส่เข้าไป

#### Lab ย่อย

ลองเพิ่ม `fetch_db_record("Orders", 0.2)` แล้วดูว่า output list มี 4 รายการไหม

---

### Example 8 — `task_08_wait.py`

#### แนวคิด

`asyncio.wait()` ใช้รอหลาย task แบบเลือกเงื่อนไขได้ เช่น “ใครเสร็จก่อนชนะ”

#### จุดสำคัญ

```python
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
```

แปลว่า:

- `done` = task ที่เสร็จแล้ว
- `pending` = task ที่ยังไม่เสร็จ
- `FIRST_COMPLETED` = หยุดรอทันทีเมื่อมีตัวแรกเสร็จ

#### Lab ย่อย

ลองเปลี่ยน delay ของ `Backup-Server-2` เป็น `0.2` แล้วดูว่าผู้ชนะเปลี่ยนไหม

---

### Example 9 — `task_09_wait_for.py`

#### แนวคิด

`asyncio.wait_for()` ใช้จำกัดเวลารอ task

#### Flow

```text
long_query_simulation ใช้ 5 วินาที
main ให้รอแค่ 2 วินาที
เกินเวลา -> TimeoutError
```

#### จุดสำคัญ

```python
await asyncio.wait_for(long_query_simulation(), timeout=2.0)
```

ถ้างานไม่เสร็จใน 2 วินาที จะโยน `asyncio.TimeoutError`

#### Lab ย่อย

ลองเปลี่ยน timeout เป็น `6.0` แล้วดูว่าโปรแกรมได้ result แทน timeout ไหม

---

### Example 10 — `task_10_gather_vs_wait.py`

#### แนวคิด

ไฟล์นี้เทียบ `gather()` กับ `wait()`

| คำสั่ง | เหมาะกับอะไร |
|---|---|
| `gather()` | ต้องการผลลัพธ์ครบทุกงาน |
| `wait(... FIRST_COMPLETED)` | ต้องการแค่ผู้ชนะ / ตัวแรกที่เสร็จ |

#### Flow

ช่วงแรกใช้ `gather()`:

```text
A ใช้ 0.5 วิ
B ใช้ 2.0 วิ
รอทั้งคู่จบ
```

ช่วงสองใช้ `wait()`:

```text
A ใช้ 0.5 วิ
B ใช้ 2.0 วิ
A เสร็จก่อน -> ประกาศผู้ชนะ
cancel B
```

#### Lab ย่อย

ลองเปลี่ยน speed ของ B เป็น `0.1` แล้วดูว่าผู้ชนะเปลี่ยนเป็น B หรือไม่

---

## 4. Lab Section — Assignment 1: `smart_courier.py`

### 4.1 เป้าหมายของ Lab

จำลองระบบพนักงานส่งพัสดุด่วน 1 คน ที่ต้องส่งของแบบ async

ถ้าส่งนานเกิน 2 วินาที โปรแกรมหลักจะยกเลิกงานทันที

---

### 4.2 Library ที่ใช้

```python
import asyncio
from time import ctime
```

| library | ใช้ทำอะไร |
|---|---|
| `asyncio` | สร้าง task, sleep แบบ async, cancel task |
| `ctime` | แสดงเวลาปัจจุบันใน output |

---

### 4.3 Function: `delivery_task(package_id, duration)`

หน้าที่: จำลองการส่งพัสดุ

```python
async def delivery_task(package_id, duration):
```

| parameter | ความหมาย | ค่าที่ใช้ใน lab |
|---|---|---|
| `package_id` | รหัสพัสดุ | `"P001"` |
| `duration` | เวลาที่ใช้ส่งพัสดุ | `5.0` วินาที |

ใน function นี้มี 2 กรณี:

#### กรณีส่งสำเร็จ

```python
await asyncio.sleep(duration)
return f"Package {package_id} Delivered!"
```

ถ้าไม่มีใคร cancel task งานจะรอครบ `duration` แล้ว return ข้อความสำเร็จ

#### กรณีถูกยกเลิก

```python
except asyncio.CancelledError:
    print(...)
    raise
```

เมื่อ task ถูก cancel จะเข้ามาใน `except` แล้ว print:

```text
Delivery Canceled! Returning package to warehouse.
```

แล้ว `raise` ต่อ เพื่อให้ task มีสถานะ cancelled จริง

---

### 4.4 Function: `main()`

หน้าที่: สร้าง task, รอ 2 วินาที, ตรวจสถานะ, แล้ว cancel ถ้ายังไม่เสร็จ

#### สร้าง task

```python
task = asyncio.create_task(
    delivery_task(package_id="P001", duration=5.0),
    name="Express-Courier"
)
```

แปลว่า:

- ส่งพัสดุ `P001`
- ใช้เวลาจำลอง `5.0` วินาที
- ตั้งชื่อ task ว่า `Express-Courier`

#### รอก่อนตรวจ

```python
await asyncio.sleep(2.0)
```

main รอแค่ 2 วินาที แต่ delivery ใช้ 5 วินาที ดังนั้น task จะยังไม่เสร็จ

#### ตรวจสถานะ

```python
task.done()
```

จะได้ `False`

#### ยกเลิก

```python
task.cancel()
```

ส่งสัญญาณ cancel ไปยัง task

#### ตรวจสุดท้าย

```python
task.cancelled()
```

จะได้ `True` เมื่อ task ถูกยกเลิกสำเร็จ

---

### 4.5 Expected Output

เวลาจะเปลี่ยนตามเครื่อง แต่ข้อความหลักควรเป็นแบบนี้:

```text
Wed Jul  8 11:05:46 2026 Courier started delivering P001...
Wed Jul  8 11:05:48 2026 Checking task 'Express-Courier'. Is it done? False
Wed Jul  8 11:05:48 2026 Taking too long! Canceling the task...
Wed Jul  8 11:05:48 2026 Delivery Canceled! Returning package to warehouse.
Wed Jul  8 11:05:48 2026 Final verify: Is task officially canceled? True
```

---

### 4.6 Lab Practice

1. เปลี่ยน `duration=5.0` เป็น `duration=1.0`
2. รันใหม่
3. สังเกตว่า task จะเสร็จก่อน 2 วินาทีไหม
4. ถ้าเสร็จก่อน `.done()` จะเป็น `True` และไม่ควรถูก cancel

> ถ้าทำ lab นี้จริง ต้องคิดต่อว่า code ควร handle กรณีส่งสำเร็จยังไง แต่ไฟล์ปัจจุบันออกแบบมาเพื่อโชว์กรณี cancel เป็นหลักค่ะ

---

## 5. Lab Section — Assignment 2: `stock_price.py`

### 5.1 เป้าหมายของ Lab

จำลองการแข่งขันดึงราคาหุ้นจาก server 3 ตัว โดยไม่ใช้ network จริง

server ทั้ง 3 ตัวมี delay ต่างกัน:

| Server | Delay | คาดหวัง |
|---|---:|---|
| Alpha | 3.0 วินาที | ช้าที่สุด |
| Beta | 0.8 วินาที | เร็วที่สุด / ผู้ชนะ |
| Gamma | 1.5 วินาที | ปานกลาง |

---

### 5.2 Function: `fetch_stock_price(server_name, delay)`

```python
async def fetch_stock_price(server_name, delay):
    await asyncio.sleep(delay)
    return f"[{server_name}] Price: 150 USD"
```

หน้าที่:

1. รับชื่อ server
2. รับ delay
3. รอด้วย `asyncio.sleep(delay)`
4. return ราคาหุ้นจำลอง

---

### 5.3 ทำไมต้องใช้ `asyncio.wait()`

โจทย์ต้องการ logic แบบ “ใครเสร็จก่อนชนะ”

จึงใช้:

```python
done, pending = await asyncio.wait(
    tasks,
    return_when=asyncio.FIRST_COMPLETED
)
```

เหตุผลที่ไม่ใช้ `gather()`:

| คำสั่ง | ผลลัพธ์ |
|---|---|
| `gather()` | รอทุก server เสร็จทั้งหมด |
| `wait(... FIRST_COMPLETED)` | รอแค่ server ตัวแรกที่เสร็จ |

สำหรับโจทย์นี้ต้องการตัวแรก จึงใช้ `wait()` ค่ะ

---

### 5.4 ทำไมต้อง cancel pending task

หลังจาก Beta ชนะแล้ว Alpha และ Gamma ยังอาจกำลังรออยู่

ถ้าไม่ cancel:

- งานที่เหลือจะยังค้างใน event loop
- เปลือง resource
- เป็นนิสัยที่ไม่ดีในการเขียนระบบจริง

จึงใช้:

```python
for pending_task in pending:
    pending_task.cancel()
```

และตามด้วย:

```python
await asyncio.gather(*pending, return_exceptions=True)
```

เพื่อให้ task ที่ถูก cancel เคลียร์ตัวเองจนจบ ไม่ทิ้ง warning ค้างไว้

---

### 5.5 Expected Output

```text
Wed Jul  8 11:11:53 2026 Winner Result: [Beta] Price: 150 USD
Wed Jul  8 11:11:53 2026 Cleaning up 2 pending tasks...
```

---

### 5.6 Lab Practice

#### Lab A — เปลี่ยนผู้ชนะ

ลองเปลี่ยน delay:

```python
asyncio.create_task(fetch_stock_price("Gamma", 0.3))
```

แล้วดูว่า Winner เปลี่ยนเป็น Gamma หรือไม่

#### Lab B — เพิ่ม server

เพิ่ม server อีกตัว:

```python
asyncio.create_task(fetch_stock_price("Delta", 0.2))
```

แล้วสังเกตว่า:

- Winner ควรเป็น Delta
- pending tasks จะกลายเป็น 3 ตัว

---

## 6. Lab Section — Assignment 3 API Server: `stock_api.py`

### 6.1 เป้าหมายของไฟล์นี้

`stock_api.py` เป็น server จำลองราคาหุ้นด้วย FastAPI

ไฟล์นี้ไม่ได้เป็นตัวแข่งเอง แต่เป็น “ปลายทาง” ให้ `stock_price_httpx.py` ยิง HTTP request เข้ามา

---

### 6.2 Endpoint สำคัญ

```python
@app.get("/price/{server_name}")
```

แปลว่า endpoint มีรูปแบบ:

```text
/price/Alpha
/price/Beta
/price/Gamma
```

ถ้ารันที่เครื่องตัวเอง port 8088 URL จะเป็น:

```text
http://127.0.0.1:8088/price/Beta
```

---

### 6.3 Function: `get_stock_price(server_name: str)`

หน้าที่:

1. รับชื่อ server จาก URL
2. แปลงเป็นตัวเล็กด้วย `.lower()`
3. เลือก delay และ price ตามชื่อ server
4. return JSON กลับไป

---

### 6.4 ตารางค่า delay และราคา

| server | delay | price_usd | ความหมาย |
|---|---:|---:|---|
| Alpha | 3.0 | 152.50 | ช้าที่สุด |
| Beta | 0.8 | 149.80 | เร็วที่สุด |
| Gamma | 1.5 | 150.20 | ปานกลาง |
| อื่น ๆ | 0.1 | 100.00 | ค่า default |

---

### 6.5 JSON ที่ API ส่งกลับ

ตัวอย่างเมื่อเรียก:

```text
http://127.0.0.1:8088/price/Beta
```

จะได้ประมาณ:

```json
{
  "server": "Beta",
  "price_usd": 149.8,
  "status": "success"
}
```

---

### 6.6 วิธีรัน API Server

จากโฟลเดอร์ `Week3`:

```bash
python stock_api.py
```

หรือ:

```bash
uvicorn stock_api:app --reload --port 8088
```

ถ้ารันสำเร็จจะเห็นประมาณ:

```text
Uvicorn running on http://0.0.0.0:8088
Application startup complete.
```

---

### 6.7 Lab Practice

#### Lab A — เปิด API docs

เปิด browser ไปที่:

```text
http://127.0.0.1:8088/docs
```

จะเห็นหน้า Swagger UI ของ FastAPI

#### Lab B — ทดลอง endpoint

เปิด:

```text
http://127.0.0.1:8088/price/Alpha
http://127.0.0.1:8088/price/Beta
http://127.0.0.1:8088/price/Gamma
```

แล้วดูว่าแต่ละตัวตอบช้าต่างกันไหม

---

## 7. Lab Section — Assignment 3 Client: `stock_price_httpx.py`

### 7.1 เป้าหมายของไฟล์นี้

ไฟล์นี้คือ client ที่ยิง request ไปหา `stock_api.py` พร้อมกัน 3 ตัว แล้วเลือกตัวที่ตอบกลับเร็วที่สุด

ต่างจาก `stock_price.py` ตรงนี้:

| ไฟล์ | ใช้ข้อมูลจากไหน |
|---|---|
| `stock_price.py` | mock delay ด้วย `asyncio.sleep()` ในไฟล์เดียว |
| `stock_price_httpx.py` | ยิง HTTP request ไปหา FastAPI server จริง |

---

### 7.2 Function: `fetch_stock_price(server_name: str)`

```python
async def fetch_stock_price(server_name: str):
```

รับแค่ `server_name` ตามโจทย์ ไม่รับ `delay`

เหตุผล: delay อยู่ที่ API server แล้ว ไม่ได้อยู่ใน client

---

### 7.3 URL

ในโค้ดจริงล่าสุดของใบใช้:

```python
url = f"http://127.0.0.1:8088/price/{server_name}"
```

ความหมาย:

- `127.0.0.1` = เครื่องตัวเอง
- `8088` = port ของ FastAPI server
- `/price/{server_name}` = endpoint ที่รับชื่อ server

ถ้าอาจารย์กำหนดให้ใช้ IP กลาง เช่น:

```text
http://172.16.2.117:8088/price/{server_name}
```

ให้เปลี่ยนเฉพาะส่วน host จาก `127.0.0.1` เป็น `172.16.2.117` เมื่อ server ปลายทางเปิดและเครื่องใบเข้าถึง network นั้นได้จริง

---

### 7.4 ใช้ `httpx.AsyncClient()` ทำไม

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

เหตุผล:

- ยิง request แบบ async ได้
- ระหว่างรอ network event loop ไปดู task อื่นต่อได้
- เหมาะกับการแข่ง request หลายตัวพร้อมกัน

---

### 7.5 แปลง JSON เป็นข้อความ

```python
data = response.json()
return f"[{data['server']}] Price: {data['price_usd']} USD"
```

API ส่ง JSON เช่น:

```json
{"server":"Beta","price_usd":149.8,"status":"success"}
```

client เอามาจัด format เป็น:

```text
[Beta] Price: 149.8 USD
```

---

### 7.6 Concurrency Racing

ใน `main()` สร้าง task 3 ตัวพร้อมกัน:

```python
tasks = {
    asyncio.create_task(fetch_stock_price("Alpha")),
    asyncio.create_task(fetch_stock_price("Beta")),
    asyncio.create_task(fetch_stock_price("Gamma"))
}
```

แล้วรอแบบ:

```python
done, pending = await asyncio.wait(
    tasks,
    return_when=asyncio.FIRST_COMPLETED
)
```

แปลว่า request ที่ตอบเร็วที่สุดจะชนะ และ request ที่เหลือจะถูก cancel

---

### 7.7 Expected Output

เมื่อเปิด `stock_api.py` อยู่ก่อน แล้วรัน `stock_price_httpx.py`:

```text
Wed Jul  8 11:05:53 2026 Winner Result: [Beta] Price: 149.8 USD
Wed Jul  8 11:05:53 2026 Cleaning up 2 pending tasks...
```

---

### 7.8 Lab Practice

#### Lab A — เปลี่ยน URL เป็น IP อาจารย์

ถ้า server ของอาจารย์เปิดที่ `172.16.2.117:8088` ให้แก้ URL เป็น:

```python
url = f"http://172.16.2.117:8088/price/{server_name}"
```

แล้วรัน:

```bash
python Week3/stock_price_httpx.py
```

ถ้า timeout แปลว่า network หรือ server ปลายทางยังไม่พร้อม ไม่ใช่ logic Python ผิดเสมอไป

#### Lab B — ทดสอบ API ก่อนรัน client

ก่อนรัน client ให้ลองเปิด:

```text
http://127.0.0.1:8088/price/Beta
```

ถ้าได้ JSON แปลว่า server พร้อม

---

## 8. วิธีรันทั้งชุด

### 8.1 รัน Assignment 1

```bash
python Week3/smart_courier.py
```

### 8.2 รัน Assignment 2

```bash
python Week3/stock_price.py
```

### 8.3 รัน Assignment 3 แบบ HTTPX

ต้องเปิด API server ก่อน 1 terminal:

```bash
cd Week3
python stock_api.py
```

จากนั้นเปิดอีก terminal แล้วรัน:

```bash
python Week3/stock_price_httpx.py
```

---

## 9. Debug Checklist

ถ้าโปรแกรมไม่ทำงาน ให้ไล่เช็กแบบนี้:

| อาการ | น่าจะเกิดจาก | วิธีเช็ก |
|---|---|---|
| `ModuleNotFoundError: fastapi` | ยังไม่ได้ติดตั้ง FastAPI | `pip install fastapi uvicorn httpx` |
| `ModuleNotFoundError: httpx` | ยังไม่ได้ติดตั้ง httpx | `pip install httpx` |
| `ConnectTimeout` | client หา API server ไม่เจอ | เช็กว่า `stock_api.py` รันอยู่ไหม |
| `Connection refused` | port ไม่มี server ฟังอยู่ | เปิด `python stock_api.py` ก่อน |
| ได้ output ไม่ใช่ Beta | delay ของ server เปลี่ยน | ดู delay ใน `stock_api.py` หรือ `stock_price.py` |
| ไม่มีบรรทัด Cleaning up | ยังไม่ได้ print ก่อน cancel pending | ดูส่วนหลัง `asyncio.wait()` |

---

## 10. สรุปจำง่าย

| ไฟล์ | จำง่าย ๆ ว่า |
|---|---|
| `task_01_status.py` | เช็ก task เสร็จหรือยัง |
| `task_02_exception.py` | อ่าน result และ exception |
| `task_03_cancel.py` | cancel task ที่ทำงานไม่จบ |
| `task_04_callback.py` | ให้ function ทำงานตอน task เสร็จ |
| `task_05_nameing.py` | ตั้งชื่อ task |
| `task_06_loop_introspection.py` | ดู task ใน event loop |
| `task_07_gather.py` | รอทุกงานให้เสร็จ |
| `task_08_wait.py` | รอแบบมีเงื่อนไข เช่น ตัวแรกเสร็จ |
| `task_09_wait_for.py` | จำกัดเวลารอ |
| `task_10_gather_vs_wait.py` | เทียบ gather กับ wait |
| `smart_courier.py` | ส่งพัสดุ ถ้านานเกินให้ cancel |
| `stock_price.py` | แข่งราคาหุ้นแบบ mock sleep |
| `stock_api.py` | API server จำลองราคา |
| `stock_price_httpx.py` | client ยิง HTTP request แบบ async |

---

## 11. แบบฝึกหัดรวมท้ายบท

### Exercise 1 — อธิบายด้วยคำพูดตัวเอง

ตอบคำถาม:

1. `.done()` ต่างจาก `.cancelled()` ยังไง
2. ทำไม `stock_price.py` ใช้ `wait()` แทน `gather()`
3. ทำไมต้อง cancel pending task
4. ทำไม `stock_price_httpx.py` ไม่รับ parameter `delay`

---

### Exercise 2 — เปลี่ยนผู้ชนะ

ใน `stock_price.py` ลองทำให้ Gamma ชนะโดยไม่เปลี่ยนชื่อ function

แนวทาง:

```python
asyncio.create_task(fetch_stock_price("Gamma", 0.3))
```

---

### Exercise 3 — ทดสอบ network จริง

1. เปิด `stock_api.py`
2. เปิด browser ไปที่ `/price/Beta`
3. รัน `stock_price_httpx.py`
4. อธิบายว่าทำไม Beta ถึงชนะ

---

## 12. ข้อควรระวัง

1. อย่าใช้ `time.sleep()` ใน async function เพราะจะบล็อก event loop
2. ถ้าใช้ `wait(... FIRST_COMPLETED)` แล้วต้องการหยุดงานที่เหลือ ควร cancel pending
3. ถ้า cancel แล้วไม่ await/gather pending ต่อ อาจมี warning ได้ในบางสถานการณ์
4. ถ้า HTTPX timeout ให้เช็ก network และ API server ก่อน ไม่ใช่แก้ logic ทันที
5. ถ้าเปลี่ยน URL เป็น IP อื่น ต้องแน่ใจว่าเครื่องนั้นเปิด port 8088 จริง

---

## 13. คำสั่งตรวจงาน

ตรวจ syntax:

```bash
python -m py_compile Week3/smart_courier.py Week3/stock_price.py Week3/stock_api.py Week3/stock_price_httpx.py
```

รันโปรแกรมหลัก:

```bash
python Week3/smart_courier.py
python Week3/stock_price.py
```

รัน API + HTTPX:

```bash
cd Week3
python stock_api.py
```

อีก terminal:

```bash
python Week3/stock_price_httpx.py
```

ถ้าทุกอย่างถูกต้อง จะเห็นว่า:

- `smart_courier.py` ถูก cancel สำเร็จ
- `stock_price.py` ได้ Beta เป็น winner ราคา `150 USD`
- `stock_price_httpx.py` ได้ Beta เป็น winner ราคา `149.8 USD`
- ทั้งสอง stock program มีบรรทัด `Cleaning up 2 pending tasks...`
