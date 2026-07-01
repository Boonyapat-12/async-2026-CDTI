# Week 2 Restaurant 01 Code Study Guide

คู่มือนี้เขียนจากโค้ดจริงล่าสุดในไฟล์ร้านอาหารทั้ง 4 ไฟล์ของใบค่ะ:

- `Week2/restaurant_01_simple.py`
- `Week2/restaurant_01_thread.py`
- `Week2/restaurant_01_multiprocess.py`
- `Week2/restaurant_01_asyncio.py`

> เป้าหมาย: ให้ใบอ่านแล้วเข้าใจว่าโค้ดแต่ละไฟล์ทำอะไร ทำไม output ถึงเป็นแบบนั้น และต่างกันตรงไหนระหว่าง simple, thread, multiprocess, และ asyncio

---

## 1. ภาพรวมโจทย์ร้านอาหาร

โค้ดทั้ง 4 ไฟล์จำลอง workflow ของร้านอาหารสำหรับลูกค้า 3 คน:

```python
customers = ["A", "B", "C"]
```

แต่ละลูกค้าต้องผ่านงานประมาณนี้:

1. `Greeting` — ทักทายลูกค้า
2. `Taking Order` — รับออเดอร์
3. `Cooking` หรือ `Cooking Spaghetti` — ทำอาหาร
4. `Mini bar` หรือ `Manage bar for Drink` — จัดเครื่องดื่ม

ในทุกไฟล์ใช้เวลา `1 วินาที` ต่อหนึ่งขั้นตอน ด้วย `sleep(1)` หรือ `await asyncio.sleep(1)`

---

## 2. แนวคิดสำคัญของ Lab นี้

สิ่งที่อาจารย์ต้องการให้เห็นไม่ใช่แค่ print output แต่คือ **รูปแบบการจัดงาน** ค่ะ

| ไฟล์ | วิธีคิด | Greeting | งานหลัง Greeting | เวลารวมโดยประมาณ |
|---|---|---|---|---:|
| `restaurant_01_simple.py` | ทำทีละลูกค้าแบบปกติ | เรียง A -> B -> C | เรียง A -> B -> C | ~12 วิ |
| `restaurant_01_thread.py` | แยก thread ให้ลูกค้าแต่ละคน | เรียง A -> B -> C | A/B/C ทำพร้อมกันด้วย thread | ~6 วิ |
| `restaurant_01_multiprocess.py` | แยก process ให้ลูกค้าแต่ละคน | เรียง A -> B -> C | A/B/C ทำพร้อมกันด้วย process | ~6-8 วิ |
| `restaurant_01_asyncio.py` | แยก async task ให้ลูกค้าแต่ละคน | เรียง A -> B -> C | A/B/C สลับกันทำผ่าน event loop | ~6 วิ |

ทำไม simple ถึง ~12 วิ?

- Greeting 3 คน × 1 วิ = 3 วิ
- แต่ละลูกค้าหลัง greeting มี 3 งาน × 1 วิ = 3 วิ
- ลูกค้า 3 คน × 3 วิ = 9 วิ
- รวม 3 + 9 = 12 วิ

ทำไม thread/process/asyncio ถึง ~6 วิ?

- Greeting ยังเรียงกันอยู่ = 3 วิ
- งานหลัง greeting ของ A/B/C ทำพร้อมกันหรือสลับกัน = ประมาณ 3 วิ
- รวม 3 + 3 = 6 วิ

---

## 3. คำศัพท์ที่ต้องเข้าใจก่อนอ่านโค้ด

| คำ | ความหมายง่าย ๆ | ใน Lab นี้คือ |
|---|---|---|
| sequential | ทำทีละขั้น เรียงกัน | simple version |
| concurrent | หลายงานคืบหน้าในช่วงเวลาเดียวกัน | thread/process/asyncio version |
| blocking | รอแล้วหยุดการทำงานตรงนั้น | `sleep(1)` |
| non-blocking | รอแล้วให้ระบบไปทำงานอื่นก่อนได้ | `await asyncio.sleep(1)` |
| thread | เส้นทางการทำงานย่อยใน process เดียว | `threading.Thread(...)` |
| process | โปรแกรมย่อยแยก memory กัน | `multiprocessing.Process(...)` |
| coroutine | function แบบ async ที่ await ได้ | `async def ...` |
| task | coroutine ที่ถูกส่งให้ event loop จัดการ | `asyncio.create_task(...)` |
| join | รอ thread/process ให้ทำงานเสร็จ | `t.join()` / `p.join()` |
| await | รอ async operation ให้เสร็จ | `await task` |

---

## 4. Common Pattern ที่ทั้ง 4 ไฟล์ใช้เหมือนกัน

### 4.1 มีลูกค้า 3 คน

```python
customers = ["A", "B", "C"]
```

ตรงนี้คือ list ที่ใช้ loop สร้างงานให้ลูกค้าแต่ละคน

---

### 4.2 จับเวลารวม

```python
start_time = time()
```

ตอนท้ายจะเอาเวลาปัจจุบันลบเวลาเริ่ม:

```python
print(f"Total Operation time: {time() - start_time:.2f} seconds")
```

หรือใน simple version:

```python
print(f"{ctime()} Finished Entire Restaurant Operation in {time() - start_time:.2f} seconds.")
```

`:.2f` หมายถึงแสดงทศนิยม 2 ตำแหน่ง เช่น `6.01`

---

### 4.3 ใช้ `ctime()` ทำ timestamp

```python
from time import ctime

print(f"{ctime()} -> Greeting for customer-A ...")
```

ตัวอย่าง output:

```text
Wed Jul  1 11:34:46 2026 -> Greeting for customer-A ...
```

---

## 5. File 1 — `restaurant_01_simple.py`

### 5.1 หน้าที่ของไฟล์นี้

ไฟล์นี้เป็น version พื้นฐานที่สุด ทำงานแบบ **sequential** คือทำทีละขั้น ไม่ได้แยก thread/process/task

flow คือ:

```text
Greeting A
Greeting B
Greeting C
Serve A ทั้งหมด
Serve B ทั้งหมด
Serve C ทั้งหมด
```

---

### 5.2 Library ที่ใช้

```python
from time import sleep, ctime, time
```

| ชื่อ | ใช้ทำอะไร |
|---|---|
| `sleep(1)` | จำลองงานที่ใช้เวลา 1 วินาที |
| `ctime()` | แสดงเวลาปัจจุบัน |
| `time()` | จับเวลารวม |

---

### 5.3 Function สำคัญ

#### `greet_diners(customer)`

ใช้ทักทายลูกค้า 1 คน:

```python
def greet_diners(customer):
    print(f"{ctime()} Greeting for Customer-{customer} ...")
    sleep(1)
    print(f"{ctime()} Greeting for Customer-{customer} ...Done!")
```

ถ้าเรียก:

```python
greet_diners("A")
```

จะได้ประมาณ:

```text
Greeting for Customer-A ...
Greeting for Customer-A ...Done!
```

---

#### `take_order(customer)`

รับออเดอร์ลูกค้า:

```python
def take_order(customer):
    print(f"{ctime()} [Customer-{customer}] Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Taking Order ...Done!")
```

---

#### `do_cooking(customer)`

ทำอาหาร:

```python
def do_cooking(customer):
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...Done!")
```

---

#### `mini_bar(customer)`

จัดเครื่องดื่ม:

```python
def mini_bar(customer):
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...Done!")
```

---

#### `serve_customer(customer)`

รวม 3 งานหลัง greeting ให้ลูกค้าหนึ่งคน:

```python
def serve_customer(customer):
    take_order(customer)
    do_cooking(customer)
    mini_bar(customer)
    print(f"{ctime()} [Customer-{customer}] All served!")
    print()
```

แปลว่า ลูกค้าแต่ละคนต้อง:

```text
Taking Order -> Cooking Spaghetti -> Manage Bar for Drink -> All served
```

---

### 5.4 `main()` ทำอะไร

```python
def main():
    customers = ["A", "B", "C"]
    start_time = time()

    for customer in customers:
        greet_diners(customer)

    print()
    print(f"{ctime()} --- All customers greeted. Serving customers one by one! ---")
    print()

    for customer in customers:
        serve_customer(customer)
```

แปลเป็นภาษาคน:

1. ตั้งรายชื่อลูกค้า A, B, C
2. จับเวลาเริ่ม
3. greeting ลูกค้าทุกคนแบบเรียงกัน
4. print ข้อความบอกว่า greeting ครบแล้ว
5. serve ลูกค้าทีละคนแบบเรียงกัน

---

### 5.5 Example output ที่ควรเข้าใจ

```text
Greeting for Customer-A ...
Greeting for Customer-A ...Done!
Greeting for Customer-B ...
Greeting for Customer-B ...Done!
Greeting for Customer-C ...
Greeting for Customer-C ...Done!

--- All customers greeted. Serving customers one by one! ---

[Customer-A] Taking Order ...
[Customer-A] Taking Order ...Done!
[Customer-A] Cooking Spaghetti ...
[Customer-A] Cooking Spaghetti ...Done!
[Customer-A] Manage Bar for Drink ...
[Customer-A] Manage Bar for Drink ...Done!
[Customer-A] All served!
```

จุดสังเกต: ลูกค้า B จะยังไม่เริ่ม service จนกว่า A จะ `All served!`

---

### 5.6 Lab สำหรับ `restaurant_01_simple.py`

ลองแก้จำนวนลูกค้า:

```python
customers = ["A", "B", "C", "D"]
```

คำถาม:

1. เวลารวมควรเพิ่มจากประมาณ 12 วิเป็นกี่วิ?
2. ลูกค้า D เริ่ม service ก่อน C เสร็จได้ไหม?
3. ถ้าเพิ่ม `sleep(2)` ทุกจุด เวลาจะเพิ่มอย่างไร?

เฉลยแนวคิด:

- Greeting 4 คน × 1 = 4 วิ
- Service 4 คน × 3 งาน × 1 = 12 วิ
- รวมประมาณ 16 วิ

---

## 6. File 2 — `restaurant_01_thread.py`

### 6.1 หน้าที่ของไฟล์นี้

ไฟล์นี้ใช้ `threading` เพื่อให้ลูกค้า A, B, C ทำ workflow หลัง greeting ได้พร้อมกันมากขึ้น

flow คือ:

```text
Greeting A
Greeting B
Greeting C
สร้าง Thread-A, Thread-B, Thread-C
Thread-A ทำงานของ A
Thread-B ทำงานของ B
Thread-C ทำงานของ C
main รอทุก thread ด้วย join()
```

---

### 6.2 Library ที่ใช้

```python
from time import sleep, ctime, time
import threading
```

| ชื่อ | ใช้ทำอะไร |
|---|---|
| `threading.Thread(...)` | สร้าง thread ใหม่ |
| `t.start()` | เริ่มให้ thread ทำงาน |
| `t.join()` | รอ thread ทำงานเสร็จ |
| `sleep(1)` | จำลองงานที่ใช้เวลา |

---

### 6.3 Function `greet_diners(customer)`

ในไฟล์นี้ greeting ยังเป็น synchronous เหมือนเดิม:

```python
def greet_diners(customer):
    print(f"{ctime()} -> Greeting for customer-{customer} ...")
    sleep(1)
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")
```

ดังนั้นช่วง greeting ยังใช้เวลาประมาณ 3 วินาที

---

### 6.4 Function `customer_private_workflow(customer)`

นี่คือ function ที่แต่ละ thread จะไปรันเอง:

```python
def customer_private_workflow(customer):
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...Done!")

    print(f"{ctime()} [Thread-{customer}] -> Cooking ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Cooking ...Done!")

    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...Done!")
```

ชื่อ `customer_private_workflow` แปลว่า workflow ส่วนตัวของลูกค้าแต่ละคน

ถ้า customer เป็น `A` output จะมี label:

```text
[Thread-A]
```

ถ้า customer เป็น `B` output จะมี label:

```text
[Thread-B]
```

---

### 6.5 จุดสำคัญใน main

```python
processes = []

for customer in customers:
    t = threading.Thread(target=customer_private_workflow, args=(customer,))
    t.start()
    processes.append(t)

for t in processes:
    t.join()
```

ถึงตัวแปรชื่อ `processes` แต่ในไฟล์นี้จริง ๆ เก็บ **thread objects** ค่ะ

อธิบายทีละบรรทัด:

| บรรทัด | ความหมาย |
|---|---|
| `processes = []` | list ไว้เก็บ thread ที่สร้างแล้ว |
| `threading.Thread(...)` | สร้าง thread ใหม่ |
| `target=customer_private_workflow` | ให้ thread ไปรัน function นี้ |
| `args=(customer,)` | ส่ง customer เข้า function |
| `t.start()` | เริ่ม thread ทันที |
| `processes.append(t)` | เก็บไว้เพื่อรอทีหลัง |
| `t.join()` | รอ thread นั้นให้เสร็จ |

---

### 6.6 ทำไมต้องมี comma ใน `args=(customer,)`

ใน Python tuple ที่มีสมาชิกตัวเดียวต้องใส่ comma:

```python
args=(customer,)
```

ถ้าเขียนแบบนี้:

```python
args=(customer)
```

Python จะมองว่าเป็น string ธรรมดา ไม่ใช่ tuple

---

### 6.7 Example output ที่ควรเข้าใจ

```text
--- All customers greeted, FORKING into independent processes for each customer ...
Wed ... [Thread-A] -> Taking Order ...
Wed ... [Thread-B] -> Taking Order ...
Wed ... [Thread-C] -> Taking Order ...
Wed ... [Thread-A] -> Taking Order ...Done!
Wed ... [Thread-A] -> Cooking ...
Wed ... [Thread-B] -> Taking Order ...Done!
Wed ... [Thread-B] -> Cooking ...
```

จุดสังเกต:

- A/B/C เริ่ม Taking Order ใกล้ ๆ กัน
- output อาจสลับลำดับกันได้
- เพราะ thread ทำงาน concurrent

---

### 6.8 Lab สำหรับ `restaurant_01_thread.py`

#### Lab A — เปลี่ยนชื่อ list ให้ตรงความหมาย

ตอนนี้ใช้:

```python
processes = []
```

แต่ไฟล์นี้เก็บ thread ดังนั้นลองเปลี่ยนเป็น:

```python
threads = []
```

แล้วแก้ทุกจุดที่เกี่ยวข้อง:

```python
threads.append(t)
for t in threads:
    t.join()
```

คำถาม:

1. output เปลี่ยนไหม?
2. ทำไมเปลี่ยนชื่อตัวแปรแล้ว behavior ไม่เปลี่ยน?
3. ชื่อตัวแปรที่ดีช่วยให้อ่านโค้ดง่ายขึ้นยังไง?

#### Lab B — ใส่ชื่อ thread จริง

ลองสร้าง thread แบบมี name:

```python
t = threading.Thread(
    target=customer_private_workflow,
    args=(customer,),
    name=f"Thread-{customer}"
)
```

แล้วใน function ลองอ่านชื่อ thread จริง:

```python
thread_name = threading.current_thread().name
```

---

## 7. File 3 — `restaurant_01_multiprocess.py`

### 7.1 หน้าที่ของไฟล์นี้

ไฟล์นี้ใช้ `multiprocessing` เพื่อสร้าง process แยกสำหรับลูกค้าแต่ละคน

flow คล้าย thread มาก แต่เปลี่ยนจาก:

```python
threading.Thread(...)
```

เป็น:

```python
multiprocessing.Process(...)
```

---

### 7.2 Library ที่ใช้

```python
from time import sleep, ctime, time
import multiprocessing
```

| ชื่อ | ใช้ทำอะไร |
|---|---|
| `multiprocessing.Process(...)` | สร้าง process ใหม่ |
| `p.start()` | เริ่ม process |
| `p.join()` | รอ process จบ |

---

### 7.3 Function สำคัญ

`greet_diners(customer)` เหมือน thread version คือ greeting เรียงกันก่อน

`customer_private_workflow(customer)` คือ workflow ที่ process ลูกจะทำ:

```python
def customer_private_workflow(customer):
    print(f"{ctime()} [Process-{customer}] -> Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Taking Order ...Done!")

    print(f"{ctime()} [Process-{customer}] -> Cooking ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Cooking ...Done!")

    print(f"{ctime()} [Process-{customer}] -> Mini bar ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Mini bar ...Done!")
```

---

### 7.4 จุดสำคัญใน main

```python
processes = []

for customer in customers:
    p = multiprocessing.Process(target=customer_private_workflow, args=(customer,))
    p.start()
    processes.append(p)

for p in processes:
    p.join()
```

อธิบาย:

| บรรทัด | ความหมาย |
|---|---|
| `p = multiprocessing.Process(...)` | สร้าง process ลูก |
| `target=customer_private_workflow` | process ลูกจะรัน function นี้ |
| `args=(customer,)` | ส่งค่า customer เข้าไป |
| `p.start()` | เริ่ม process |
| `processes.append(p)` | เก็บ process ไว้ใน list |
| `p.join()` | process หลักรอ process ลูกเสร็จ |

---

### 7.5 ทำไมต้องมี `if __name__ == "__main__"`

ไฟล์นี้มี:

```python
if __name__ == "__main__":
    customers = ["A", "B", "C"]
    ...
```

สำหรับ `multiprocessing` สำคัญมาก โดยเฉพาะบน Windows เพราะถ้าไม่มี guard นี้ process ลูกอาจ import ไฟล์ซ้ำแล้วสร้าง process ต่อไม่หยุด

จำง่าย ๆ:

```text
ถ้าใช้ multiprocessing ต้องมี if __name__ == "__main__": เสมอ
```

---

### 7.6 Example output ที่ควรเข้าใจ

```text
--- All customers greeted, FORKING into independent processes for each customer ...
Wed ... [Process-A] -> Taking Order ...
Wed ... [Process-B] -> Taking Order ...
Wed ... [Process-C] -> Taking Order ...
Wed ... [Process-A] -> Taking Order ...Done!
Wed ... [Process-A] -> Cooking ...
```

จุดสังเกต:

- output ของ process อาจสลับแปลกกว่า thread ได้
- บางครั้งเวลารวมอาจมากกว่า 6 วิเล็กน้อย เพราะ process มี overhead มากกว่า thread
- ตอนที่ไอริสรันจริงได้ `Total Operation time: 7.69 seconds` ในรอบนั้น ซึ่งถือว่าเป็น overhead/สภาพแวดล้อมการรันได้ค่ะ

---

### 7.7 Lab สำหรับ `restaurant_01_multiprocess.py`

#### Lab A — ดู PID ของแต่ละ process

เพิ่ม import:

```python
import os
```

ใน `customer_private_workflow` เพิ่ม:

```python
pid = os.getpid()
print(f"PID: {pid}")
```

คำถาม:

1. ลูกค้า A/B/C มี PID เหมือนกันไหม?
2. PID ของ process ลูกเหมือนกับ process หลักไหม?
3. สิ่งนี้ต่างจาก thread ยังไง?

#### Lab B — เปรียบเทียบเวลารัน

รันไฟล์นี้ 3 รอบ:

```bash
python3 Week2/restaurant_01_multiprocess.py
python3 Week2/restaurant_01_multiprocess.py
python3 Week2/restaurant_01_multiprocess.py
```

คำถาม:

1. เวลารวมเท่ากันทุกรอบไหม?
2. ทำไม multiprocessing อาจแกว่งกว่า asyncio/thread?

---

## 8. File 4 — `restaurant_01_asyncio.py`

### 8.1 หน้าที่ของไฟล์นี้

ไฟล์นี้ใช้ `asyncio` สร้าง async task สำหรับลูกค้าแต่ละคน

flow คือ:

```text
await Greeting A
await Greeting B
await Greeting C
create task ของ A
create task ของ B
create task ของ C
await task ทุกตัว
```

---

### 8.2 Library ที่ใช้

```python
import asyncio
import threading
from time import ctime,time
```

ในโค้ดล่าสุด:

- `asyncio` ใช้จริง
- `ctime` และ `time` ใช้จริง
- `threading` import มา แต่ยังไม่ได้ใช้ในไฟล์นี้ค่ะ

---

### 8.3 Function `greet_diners(customer)`

```python
async def greet_diners(customer):
    print(f"{ctime()} -> Greeting for customer-{customer} ...")    
    await asyncio.sleep(1)
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")
```

จุดสำคัญ:

- เป็น `async def`
- ใช้ `await asyncio.sleep(1)` แทน `sleep(1)`
- ต้องถูกเรียกด้วย `await greet_diners(customer)`

ใน `main()` ตอนนี้เขียนแบบนี้:

```python
for customer in customers:
    await greet_diners(customer)
```

แปลว่า greeting ยังเรียงกันอยู่ ไม่ได้ concurrent

---

### 8.4 Function `customer_private_workflow(customer)`

```python
async def customer_private_workflow(customer):
    print(f"{ctime()} [Task-{customer}] Taking Order ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Taking Order ...Done!")

    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Cooking Spaghetti ...Done!")

    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...")
    await asyncio.sleep(1)
    print(f"{ctime()} [Task-{customer}] Manage bar for Drink ...Done!")

    print(f"\n{ctime()} [Task-{customer}] All served!")
```

จุดที่ควรรู้:

- แต่ละลูกค้าเป็น coroutine แยกกัน
- แต่ละจุด `await asyncio.sleep(1)` คือจุดที่ event loop สามารถสลับไปทำ task อื่นได้
- label `[Task-A]`, `[Task-B]`, `[Task-C]` ไม่ได้มาจากชื่อ task จริง แต่เขียนจากค่า `customer` ใน f-string

---

### 8.5 จุดสำคัญใน `main()`

```python
tasks = []

for customer in customers:
    task = asyncio.create_task(customer_private_workflow(customer))
    tasks.append(task)

for task in tasks:
    await task
```

อธิบายทีละส่วน:

| บรรทัด | ความหมาย |
|---|---|
| `tasks = []` | list เก็บ task ทั้งหมด |
| `asyncio.create_task(...)` | ส่ง coroutine ให้ event loop เริ่มจัดการ |
| `tasks.append(task)` | เก็บ task ไว้รอทีหลัง |
| `for task in tasks: await task` | รอ task ทุกตัวให้เสร็จ |

ถึงจะ `await` ทีละ task ใน loop แต่เพราะ task ทั้งหมดถูก `create_task` ก่อนแล้ว งานจึงเริ่ม concurrent ได้ค่ะ

---

### 8.6 ทำไม `asyncio` ใช้เวลาประมาณ 6 วิ

Greeting:

```python
for customer in customers:
    await greet_diners(customer)
```

ตรงนี้ใช้ประมาณ 3 วิ เพราะ await ทีละคน

หลัง greeting:

```python
for customer in customers:
    task = asyncio.create_task(customer_private_workflow(customer))
    tasks.append(task)
```

ตรงนี้สร้าง task A/B/C ก่อน แล้วแต่ละ task มี 3 งาน งานละ 1 วิ จึงใช้ประมาณ 3 วิ

รวมประมาณ:

```text
3 วิ greeting + 3 วิ workflow concurrent = 6 วิ
```

---

### 8.7 Example output ที่ควรเข้าใจ

```text
Wed ... -> Greeting for customer-A ...
Wed ... -> Greeting for customer-A ...Done!
Wed ... -> Greeting for customer-B ...
Wed ... -> Greeting for customer-B ...Done!
Wed ... -> Greeting for customer-C ...
Wed ... -> Greeting for customer-C ...Done!
Wed ... --- All customers greeted, FORKING into independent tasks for each customer ...
Wed ... [Task-A] Taking Order ...
Wed ... [Task-B] Taking Order ...
Wed ... [Task-C] Taking Order ...
Wed ... [Task-A] Taking Order ...Done!
Wed ... [Task-A] Cooking Spaghetti ...
Wed ... [Task-B] Taking Order ...Done!
Wed ... [Task-B] Cooking Spaghetti ...
```

จุดสังเกต:

- Task A/B/C เริ่ม `Taking Order` ในเวลาใกล้กัน
- หลัง `await asyncio.sleep(1)` event loop สลับไปให้ task อื่นทำงาน
- output อาจ interleave กัน

---

### 8.8 Lab สำหรับ `restaurant_01_asyncio.py`

#### Lab A — ใช้ `asyncio.gather()` แทน await ทีละ task

ตอนนี้ใช้:

```python
for task in tasks:
    await task
```

ลองเปลี่ยนเป็น:

```python
await asyncio.gather(*tasks)
```

คำถาม:

1. output เปลี่ยนมากไหม?
2. เวลารวมยังประมาณ 6 วิไหม?
3. `gather()` อ่านง่ายกว่าไหมเวลา task เยอะ?

#### Lab B — ทำ Greeting ให้ concurrent ด้วย

ตอนนี้ greeting เรียงกัน:

```python
for customer in customers:
    await greet_diners(customer)
```

ลองเปลี่ยนเป็น:

```python
greeting_tasks = []
for customer in customers:
    greeting_tasks.append(asyncio.create_task(greet_diners(customer)))
await asyncio.gather(*greeting_tasks)
```

คำถาม:

1. เวลารวมควรลดจาก 6 วิ เหลือประมาณกี่วิ?
2. output greeting ยังเรียง A/B/C แบบเดิมไหม?
3. ถ้า greeting คือการคุยกับลูกค้าจริง ๆ ควร concurrent ไหม หรือควรเรียงทีละคน?

เฉลยแนวคิด:

- ถ้า greeting concurrent ใช้ประมาณ 1 วิ
- workflow หลัง greeting ใช้ประมาณ 3 วิ
- รวมประมาณ 4 วิ

---

## 9. เปรียบเทียบ Thread vs Process vs Asyncio ใน Lab นี้

| เรื่อง | Thread | Process | Asyncio |
|---|---|---|---|
| สร้างด้วย | `threading.Thread` | `multiprocessing.Process` | `asyncio.create_task` |
| รอด้วย | `join()` | `join()` | `await` หรือ `gather()` |
| ใช้ memory | process เดียวกัน | แยก process/memory | process/thread เดียวโดยทั่วไป |
| เหมาะกับ | งานรอ I/O | งาน CPU หนัก | งานรอ I/O จำนวนมาก |
| overhead | ปานกลาง | สูงกว่า | ต่ำกว่า |
| ใน Lab นี้ | ทำพร้อมกันหลัง greeting | ทำพร้อมกันหลัง greeting | สลับ task หลัง greeting |

---

## 10. Lab รวมทั้ง 4 ไฟล์

### Lab รวม A — ทำนายเวลาก่อนรัน

ก่อนรัน ให้เติมตารางนี้เอง:

| ไฟล์ | Greeting ใช้กี่วิ | Workflow ใช้กี่วิ | รวมที่คาดไว้ |
|---|---:|---:|---:|
| simple | 3 | 9 | 12 |
| thread | 3 | 3 | 6 |
| multiprocess | 3 | 3 + overhead | 6-8 |
| asyncio | 3 | 3 | 6 |

จากนั้นรัน:

```bash
python3 Week2/restaurant_01_simple.py
python3 Week2/restaurant_01_thread.py
python3 Week2/restaurant_01_multiprocess.py
python3 Week2/restaurant_01_asyncio.py
```

แล้วจดเวลาจริงค่ะ

---

### Lab รวม B — เพิ่มลูกค้า D

แก้ทุกไฟล์:

```python
customers = ["A", "B", "C", "D"]
```

ทำนายเวลา:

| ไฟล์ | เวลาที่คาดไว้ |
|---|---:|
| simple | 4 + 12 = 16 วิ |
| thread | 4 + 3 = 7 วิ |
| multiprocess | 4 + 3 + overhead = ประมาณ 7-9 วิ |
| asyncio | 4 + 3 = 7 วิ |

คำถาม:

1. ทำไม simple เพิ่มเยอะที่สุด?
2. ทำไม thread/process/asyncio เพิ่มแค่ช่วง greeting?
3. ถ้า greeting ก็ทำ concurrent ด้วย เวลาจะเหลือประมาณเท่าไร?

---

### Lab รวม C — เปลี่ยนเวลาทำอาหารเป็น 2 วิ

เปลี่ยนเฉพาะขั้น Cooking:

ใน simple/thread/process:

```python
sleep(2)
```

ใน asyncio:

```python
await asyncio.sleep(2)
```

ทำนายเวลา:

| ไฟล์ | เวลาที่คาดไว้ |
|---|---:|
| simple | greeting 3 + workflow 12 = 15 วิ |
| thread | greeting 3 + workflow 4 = 7 วิ |
| multiprocess | greeting 3 + workflow 4 + overhead = 7+ วิ |
| asyncio | greeting 3 + workflow 4 = 7 วิ |

---

## 11. Example: ทำไม create ก่อน await ถึง concurrent

ใน asyncio ถ้าเขียนแบบนี้:

```python
for customer in customers:
    await customer_private_workflow(customer)
```

จะกลายเป็นเรียงกัน:

```text
A เสร็จหมด -> B เสร็จหมด -> C เสร็จหมด
```

แต่โค้ดปัจจุบันทำแบบนี้:

```python
for customer in customers:
    task = asyncio.create_task(customer_private_workflow(customer))
    tasks.append(task)

for task in tasks:
    await task
```

แปลว่า:

```text
สร้าง Task-A
สร้าง Task-B
สร้าง Task-C
แล้วค่อยรอทุก task
```

จุดนี้สำคัญมากค่ะ เพราะเป็นเหตุผลที่ output สลับกันและเวลารวมสั้นลง

---

## 12. Common Mistakes ที่ต้องระวัง

### 12.1 ลืม `join()` ใน thread/process

ถ้าไม่ join:

```python
for t in processes:
    t.join()
```

main program อาจจบก่อนงานลูกเสร็จ หรือเวลา total อาจไม่สะท้อนงานจริง

---

### 12.2 ลืม `await` ใน asyncio

ผิด:

```python
greet_diners(customer)
```

ถูก:

```python
await greet_diners(customer)
```

ถ้าลืม await จะได้ coroutine object แต่ไม่รันจริง

---

### 12.3 ใช้ `time.sleep()` ใน async function

ผิด:

```python
async def customer_private_workflow(customer):
    sleep(1)
```

ถึงจะรันได้ถ้า import มา แต่จะ block event loop ทำให้ task อื่นไม่ได้ทำงานระหว่างรอ

ถูก:

```python
await asyncio.sleep(1)
```

---

### 12.4 เข้าใจผิดว่า multiprocessing output ต้องเรียงเสมอ

process ทำงานแยกกัน ดังนั้น output อาจสลับ ไม่เรียง A/B/C เสมอค่ะ

นี่ไม่ใช่ error ถ้า logic ถูกและทุก process `join()` ครบ

---

### 12.5 ชื่อตัวแปรไม่ตรงความหมาย

ใน `restaurant_01_thread.py` ใช้ตัวแปรชื่อ `processes` เพื่อเก็บ thread

โค้ดรันได้ แต่เวลาอ่านอาจสับสน ควรรู้ว่า:

```python
processes = []  # ในไฟล์ thread นี้จริง ๆ คือ list ของ thread
```

ถ้าจะทำให้สะอาดขึ้น ใช้ `threads = []` จะตรงกว่า

---

## 13. คำสั่งตรวจงาน

ตรวจ syntax:

```bash
python3 -m py_compile \
  Week2/restaurant_01_simple.py \
  Week2/restaurant_01_thread.py \
  Week2/restaurant_01_multiprocess.py \
  Week2/restaurant_01_asyncio.py
```

รันทีละไฟล์:

```bash
python3 Week2/restaurant_01_simple.py
python3 Week2/restaurant_01_thread.py
python3 Week2/restaurant_01_multiprocess.py
python3 Week2/restaurant_01_asyncio.py
```

รันทั้งหมดแบบ loop:

```bash
for f in Week2/restaurant_01_*.py; do
  echo "===== $f ====="
  python3 "$f"
  echo
done
```

---

## 14. สรุปสั้นที่สุด

```text
simple:
  ทุกอย่างเรียงกัน จึงช้าที่สุด

thread:
  greeting เรียงกัน แต่หลังจากนั้นลูกค้าแต่ละคนแยก thread ทำงานพร้อมกัน

multiprocess:
  greeting เรียงกัน แต่หลังจากนั้นลูกค้าแต่ละคนแยก process ทำงานพร้อมกัน

asyncio:
  greeting เรียงกัน แต่หลังจากนั้นลูกค้าแต่ละคนเป็น async task และสลับกันทำตอน await
```

จำหัวใจของงานนี้แบบนี้ค่ะ:

```text
ความต่างไม่ได้อยู่ที่ร้านอาหารทำอะไร
แต่อยู่ที่ “จัดคิวงานหลัง greeting ยังไง”
```

ถ้าใบอธิบายได้ว่า `start()`, `join()`, `create_task()`, และ `await` ทำอะไร ใบจะเข้าใจ Lab นี้แล้วค่ะ
