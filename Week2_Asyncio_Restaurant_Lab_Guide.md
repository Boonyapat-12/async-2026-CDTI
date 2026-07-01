# Week 2 Asyncio + Restaurant Lab Guide

คู่มือฉบับนี้เขียนไว้ให้ใบอ่านตั้งแต่พื้นฐานมาก ๆ เพื่อเข้าใจว่า Week2 เรียนเรื่อง `asyncio` ยังไง ไฟล์ `asyncio01.py` ถึง `asyncio10.py` ทำอะไรไปแล้ว และควรเอาความรู้นี้ไปทำไฟล์ Lab ร้านอาหาร 4 ไฟล์ที่เหลือยังไงค่ะ

> เป้าหมาย: อ่านคู่มือนี้แล้วเข้าใจภาพรวมของ asynchronous programming และรู้ว่าจะเขียน `restaurant_01_simple.py`, `restaurant_01_thread.py`, `restaurant_01_multiprocess.py`, `restaurant_01_asyncio.py` ต่อยังไง โดยไม่ต้องมีพื้นฐานมาก่อน

---

## 1. Week2 กำลังเรียนเรื่องอะไร

Week2 เรียนเรื่อง **Asynchronous Programming** หรือการเขียนโปรแกรมให้ “รอหลายงานได้ฉลาดขึ้น” โดยเฉพาะงานที่มีช่วงรอ เช่น

- รออาหารสุก
- รอกาแฟชงเสร็จ
- รอไฟล์ดาวน์โหลด
- รอข้อมูลจากอินเทอร์เน็ต
- รอ database ตอบกลับ

ปัญหาคือ ถ้าเราเขียนแบบปกติ โปรแกรมจะทำงานแบบนี้:

```text
ทำงาน A -> รอ A เสร็จ -> ทำงาน B -> รอ B เสร็จ -> ทำงาน C -> รอ C เสร็จ
```

แต่ asynchronous programming ทำให้โปรแกรมทำงานประมาณนี้:

```text
เริ่มงาน A -> ระหว่าง A รอ ให้ไปเริ่มงาน B -> ระหว่าง B รอ ให้ไปเริ่มงาน C -> กลับมาเก็บงานที่เสร็จ
```

สิ่งสำคัญ: `asyncio` ไม่ได้แปลว่ามีหลาย CPU หรือหลาย thread เสมอไปค่ะ  
โดยทั่วไป `asyncio` คือ **งานหลายงานสลับกันทำใน thread เดียว ผ่าน event loop**

---

## 2. คำศัพท์สำคัญที่ต้องรู้ก่อน

| คำ | แปลแบบง่าย | จำแบบร้านอาหาร |
|---|---|---|
| synchronous | ทำทีละอย่างตามลำดับ | ทำอาหารจาน A ให้เสร็จก่อน ค่อยเริ่มจาน B |
| asynchronous | ทำงานแบบสลับระหว่างช่วงรอ | ระหว่างต้มเส้นอยู่ ไปชงกาแฟให้ลูกค้าอีกคนได้ |
| coroutine | งาน async ที่ยังไม่ถูกรันจริง | ใบสั่งงานที่เขียนไว้ แต่ยังไม่ได้เอาเข้าครัว |
| event loop | ตัวจัดคิวงาน async | ผู้จัดการครัวที่คอยดูว่างานไหนรอ งานไหนทำต่อได้ |
| `async def` | ประกาศ function แบบ async | เขียนสูตรงานที่ให้ event loop จัดการได้ |
| `await` | จุดที่บอกว่า “ตอนนี้รอได้ ไปทำงานอื่นก่อนได้” | ต้มเส้น 1 นาที ระหว่างนี้ไปทำอย่างอื่นก่อน |
| task | coroutine ที่ถูกส่งให้ event loop รัน | ใบสั่งงานที่ถูกเอาเข้าคิวครัวแล้ว |
| `asyncio.run()` | เปิด event loop แล้วรันงานหลัก | เปิดร้าน แล้วเริ่มให้ผู้จัดการครัวทำงาน |
| `asyncio.create_task()` | สร้าง task ให้เริ่มรันแบบ concurrent | ส่งออเดอร์เข้าครัวโดยไม่ต้องยืนรอหน้าหม้อ |
| `asyncio.gather()` | รอหลาย task พร้อมกัน | รอทุกออเดอร์ในชุดนี้เสร็จทั้งหมด |

---

## 3. ภาพใหญ่ของไฟล์ Week2

| ไฟล์ | หัวข้อ | สิ่งที่ใบควรเข้าใจ |
|---|---|---|
| `asyncio01.py` | `async def` คืออะไร | แค่ประกาศ async function ยังไม่ได้รัน |
| `asyncio02.py` | coroutine object | เรียก async function แล้วได้ coroutine object แต่ยังไม่ execute |
| `asyncio03.py` | event loop | ใช้ `asyncio.run()` เพื่อให้ coroutine ทำงานจริง |
| `asyncio04.py` | `await` | coroutine หยุดรอแบบไม่ block event loop |
| `asyncio05.py` | sequential async | ใช้ `await` ทีละบรรทัดยังทำงานเรียงกันอยู่ |
| `asyncio06.py` | `create_task()` | สร้าง task ให้ไปทำงานเบื้องหลังได้ |
| `asyncio07.py` | two concurrent tasks | สร้าง 2 task แล้วเวลารวมใกล้ 1 วินาที ไม่ใช่ 2 วินาที |
| `asyncio08.py` | task interleaving | เห็นการสลับงานระหว่าง kitchen/bar ใน thread เดียว |
| `asyncio09.py` | dynamic task list | สร้าง task หลายตัวจาก list ลูกค้า |
| `asyncio10.py` | return values | task สามารถ `return` ค่า แล้วเอาผลลัพธ์มาใช้ต่อได้ |
| `restaurant_01_simple.py` | Lab | เขียนร้านอาหารแบบ synchronous |
| `restaurant_01_thread.py` | Lab | เขียนร้านอาหารแบบ threading |
| `restaurant_01_multiprocess.py` | Lab | เขียนร้านอาหารแบบ multiprocessing |
| `restaurant_01_asyncio.py` | Lab | เขียนร้านอาหารแบบ asyncio |

---

## 4. อธิบายไฟล์ `asyncio01.py` ถึง `asyncio10.py`

### 4.1 `asyncio01.py` — The First Coroutine Function

แนวคิดหลัก:

```python
async def greet():
    print("Hello from the Coroutine")

print(type(greet))
```

จุดสำคัญ:

- `async def greet()` คือการประกาศ function แบบ async
- แต่ตัว `greet` เองยังเป็น function อยู่
- ยังไม่มีข้อความ `Hello from the Coroutine` ออกมา เพราะยังไม่ได้เรียกและยังไม่ได้รันด้วย event loop

สิ่งที่ควรจำ:

```text
async def = สร้าง function ที่สามารถกลายเป็น coroutine ได้
```

---

### 4.2 `asyncio02.py` — The Coroutine Object

แนวคิดหลัก:

```python
coro_object = greet()
print(type(coro_object))
coro_object.close()
```

จุดสำคัญ:

- พอเรียก `greet()` จะได้ coroutine object
- coroutine object ยังไม่ทำงานเอง
- ถ้าสร้าง coroutine แล้วไม่รัน ควร `close()` เพื่อไม่ให้ Python เตือนว่า coroutine was never awaited

เปรียบเทียบง่าย ๆ:

```text
greet       = สูตรอาหาร

greet()     = ใบสั่งอาหารที่ถูกเขียนแล้ว

await/run   = เอาใบสั่งอาหารไปให้ครัวทำจริง
```

---

### 4.3 `asyncio03.py` — The Event Loop

แนวคิดหลัก:

```python
coro_object = greet()
asyncio.run(coro_object)
```

จุดสำคัญ:

- `asyncio.run()` คือการเปิด event loop
- event loop จะรับ coroutine ไปทำงานจริง
- ตอนนี้ข้อความใน `greet()` ถึงจะ print ออกมา

จำสั้น ๆ:

```text
coroutine จะทำงานจริงเมื่อถูก await หรือถูกส่งให้ event loop ผ่าน asyncio.run()
```

---

### 4.4 `asyncio04.py` — The `await` Keyword

แนวคิดหลัก:

```python
async def main():
    print("Task Started")
    await asyncio.sleep(1)
    print("Task Finished")
```

`await asyncio.sleep(1)` ไม่เหมือน `time.sleep(1)`:

| คำสั่ง | พฤติกรรม |
|---|---|
| `time.sleep(1)` | block thread ทิ้งไว้ 1 วินาที ทำอย่างอื่นไม่ได้ |
| `await asyncio.sleep(1)` | รอ 1 วินาทีแบบคืน control ให้ event loop ไปจัดการงานอื่นได้ |

ในไฟล์นี้มี task เดียว เลยยังไม่เห็นความต่างมาก แต่เป็นพื้นฐานของไฟล์ถัดไปค่ะ

---

### 4.5 `asyncio05.py` — Sequential Execution

แนวคิดหลัก:

```python
await serve_customer("A")
await serve_customer("B")
```

ถึงจะเป็น async function แต่ถ้าเขียน `await` ต่อกันตรง ๆ แบบนี้:

```text
รอ A เสร็จ -> ค่อยเริ่ม B
```

ดังนั้นถ้า A ใช้ 1 วินาที และ B ใช้ 1 วินาที เวลารวมจะประมาณ 2 วินาที

ข้อควรจำ:

```text
async ไม่ได้ทำให้เร็วเอง ถ้า await ทีละอันแบบเรียงกัน ก็ยัง sequential
```

---

### 4.6 `asyncio06.py` — Creating a Concurrent Task

แนวคิดหลัก:

```python
task1 = asyncio.create_task(cook_spaghetti("A"))
print("Main program can do other things...")
await task1
```

จุดสำคัญ:

- `asyncio.create_task(...)` ส่ง coroutine เข้า event loop
- task เริ่มมีโอกาสทำงานแบบเบื้องหลัง
- main program ยังสามารถทำงานอื่นต่อได้
- สุดท้ายต้อง `await task1` เพื่อรอให้ task เสร็จ

ภาพจำ:

```text
create_task = ฝากงานไว้กับ event loop ก่อน
await task  = กลับมารอรับผลลัพธ์ตอนต้องการ
```

---

### 4.7 `asyncio07.py` — Dual Tasks Concurrency

แนวคิดหลัก:

```python
task_a = asyncio.create_task(cook_spaghetti("A"))
task_b = asyncio.create_task(cook_spaghetti("B"))

await task_a
await task_b
```

ทำไมเวลารวมประมาณ 1 วินาที ไม่ใช่ 2 วินาที?

เพราะ task A และ task B ถูกสร้างก่อนทั้งคู่ จากนั้นทั้งสอง task มีโอกาสเริ่มทำงานพร้อม ๆ กันใน event loop

ลำดับประมาณนี้:

```text
สร้าง task A
สร้าง task B
A เริ่มทำอาหาร -> await sleep
B เริ่มทำอาหาร -> await sleep
A เสร็จ
B เสร็จ
```

ข้อควรจำ:

```text
ถ้าต้องการ concurrency ต้องสร้าง task ก่อน แล้วค่อย await
```

---

### 4.8 `asyncio08.py` — Task Interleaving

ไฟล์นี้แสดงภาพการสลับงานชัดมาก:

```python
task_kitchen = asyncio.create_task(kitchen_crew())
task_bar = asyncio.create_task(bar_crew())

await task_kitchen
await task_bar
```

สิ่งที่ควรสังเกต:

- kitchen เริ่มต้มเส้นแล้ว `await asyncio.sleep(1)`
- ระหว่าง kitchen รอ event loop ไปให้ bar ทำงาน
- bar เริ่มบดกาแฟแล้ว `await asyncio.sleep(1)`
- พอเวลาครบ event loop กลับมาให้แต่ละ task ทำต่อ

นี่คือหัวใจของ `asyncio`:

```text
ไม่ได้ทำพร้อมกันจริงแบบหลาย CPU แต่สลับงานตอนแต่ละงานกำลังรอ
```

---

### 4.9 `asyncio09.py` — Dynamically Tracking Tasks in a List

แนวคิดหลัก:

```python
customers = ["A", "B", "C", "D"]
task_list = []

for name in customers:
    t = asyncio.create_task(serve_customer(name))
    task_list.append(t)

for t in task_list:
    await t
```

นี่คือ pattern ที่สำคัญมาก เพราะในชีวิตจริงจำนวนงานมักไม่ได้มีแค่ 2 งานตายตัว

เช่น:

- ลูกค้า 4 คน
- URL 100 ลิงก์
- ไฟล์ 30 ไฟล์
- query database หลายอัน

ขั้นตอนคือ:

1. มี list ของงาน เช่น `customers`
2. loop สร้าง task จากแต่ละ item
3. เก็บ task ไว้ใน `task_list`
4. loop รอทุก task ให้เสร็จ

แบบที่อ่านง่ายขึ้นในอนาคตคือใช้ `asyncio.gather()`:

```python
tasks = []

for name in customers:
    tasks.append(asyncio.create_task(serve_customer(name)))

await asyncio.gather(*tasks)
```

---

### 4.10 `asyncio10.py` — Extracting Return Values from Tasks

แนวคิดหลัก:

```python
task_a = asyncio.create_task(calculate_bill("A", 100))
task_b = asyncio.create_task(calculate_bill("B", 200))

result_a = await task_a
result_b = await task_b
```

สิ่งที่เพิ่มจากไฟล์ก่อน ๆ:

- coroutine สามารถ `return` ค่าได้
- task ที่ await แล้วจะคืนค่ากลับมา
- เอาค่าที่ได้ไปคำนวณต่อได้

ตัวอย่าง:

```python
async def calculate_bill(customer, base_price):
    await asyncio.sleep(2)
    final_price = base_price * 1.07
    return final_price
```

ผลลัพธ์:

```text
A: 100 + VAT 7% = 107
B: 200 + VAT 7% = 214
Total = 321
```

ข้อควรจำ:

```text
await task ไม่ได้แค่รอ task เสร็จ แต่ยังเอาค่า return กลับมาได้ด้วย
```

---

## 5. เปรียบเทียบ 4 วิธีที่จะใช้ใน Restaurant Lab

Lab ร้านอาหาร 4 ไฟล์น่าจะให้ใบเขียน logic เดียวกัน แต่ใช้วิธีรันงานต่างกันค่ะ

| ไฟล์ | วิธีทำงาน | เวลาที่คาดหวังถ้ามีลูกค้า 3 คน คนละ 2 วิ | จุดประสงค์ |
|---|---|---:|---|
| `restaurant_01_simple.py` | synchronous | ประมาณ 6 วิ | เห็น baseline ทำทีละคน |
| `restaurant_01_thread.py` | threading | ประมาณ 2 วิ | เห็นงานรอ I/O ทำพร้อมกันผ่านหลาย thread |
| `restaurant_01_multiprocess.py` | multiprocessing | ประมาณ 2 วิ | เห็นการแยก process จริง |
| `restaurant_01_asyncio.py` | asyncio | ประมาณ 2 วิ | เห็น concurrency แบบ event loop/thread เดียว |

> หมายเหตุ: ถ้างานเป็น `sleep()` หรือ “รอ” threading กับ asyncio จะเห็นเร็วขึ้นชัดมาก  
> ถ้างานเป็นคำนวณหนัก CPU จริง ๆ multiprocessing จะเหมาะกว่า

---

## 6. แบบจำลองร้านอาหารสำหรับ Lab

เพื่อให้ทั้ง 4 ไฟล์เทียบกันง่าย ให้ใช้โจทย์เดียวกัน:

```text
ร้านอาหารมีลูกค้า A, B, C
แต่ละคนสั่ง spaghetti
การทำอาหาร 1 จานใช้เวลา 2 วินาที
ให้แสดง log ว่าเริ่มทำอาหาร / ทำเสร็จ / เวลารวม
```

Output โดยประมาณ:

```text
Wed Jul  1 10:00:00 2026 -> Start cooking spaghetti for customer A
Wed Jul  1 10:00:02 2026 -> Finished spaghetti for customer A
...
Total time: 6.00 seconds
```

สิ่งที่ทุกไฟล์ควรมี:

| ส่วน | ทำอะไร |
|---|---|
| `customers = ["A", "B", "C"]` | รายชื่อลูกค้า |
| `cook_spaghetti(customer)` | function หลักของการทำอาหาร |
| `main()` | จุดเริ่มจัดคิวงาน |
| `start = time()` | จับเวลาเริ่ม |
| `print(f"Total time: ...")` | สรุปเวลารวม |

---

## 7. Lab 1 — `restaurant_01_simple.py`

### เป้าหมาย

เขียนร้านอาหารแบบ synchronous คือทำอาหารทีละคนตามลำดับ

### ความรู้ที่ใช้

```python
from time import sleep, ctime, time
```

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `sleep(2)` | จำลองเวลาทำอาหาร 2 วินาที แบบ blocking |
| `ctime()` | print เวลาปัจจุบันให้อ่านง่าย |
| `time()` | จับเวลารวม |

### โครงสร้างที่ควรเขียน

```python
from time import sleep, ctime, time


def cook_spaghetti(customer):
    print(f"{ctime()} -> Start cooking spaghetti for customer {customer}")
    sleep(2)
    print(f"{ctime()} -> Finished spaghetti for customer {customer}")


def main():
    start = time()
    customers = ["A", "B", "C"]

    for customer in customers:
        cook_spaghetti(customer)

    print(f"Total time: {time() - start:.2f} seconds")


if __name__ == "__main__":
    main()
```

### สิ่งที่ควรเกิดขึ้น

```text
A เริ่ม -> A เสร็จ -> B เริ่ม -> B เสร็จ -> C เริ่ม -> C เสร็จ
```

เวลารวมควรประมาณ:

```text
2 + 2 + 2 = 6 seconds
```

### คำถามทบทวน

1. ทำไม B ต้องรอ A เสร็จก่อน?
2. `sleep(2)` ทำให้โปรแกรมทำอะไรไม่ได้เลยระหว่างรอใช่ไหม?
3. ถ้ามีลูกค้า 10 คน เวลาจะเพิ่มเป็นประมาณกี่วินาที?

---

## 8. Lab 2 — `restaurant_01_thread.py`

### เป้าหมาย

เขียนร้านอาหารแบบใช้ thread เพื่อให้ลูกค้า A, B, C เริ่มทำอาหารได้ใกล้เคียงกัน

### ความรู้ที่ใช้

```python
import threading
from time import sleep, ctime, time
```

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `threading.Thread(...)` | สร้าง thread ใหม่ |
| `target=cook_spaghetti` | บอกว่า thread นี้จะรัน function ไหน |
| `args=(customer,)` | ส่งค่า customer เข้า function |
| `start()` | เริ่ม thread |
| `join()` | รอ thread จบ |

### โครงสร้างที่ควรเขียน

```python
import threading
from time import sleep, ctime, time


def cook_spaghetti(customer):
    thread_name = threading.current_thread().name
    print(f"{ctime()} -> [{thread_name}] Start cooking spaghetti for customer {customer}")
    sleep(2)
    print(f"{ctime()} -> [{thread_name}] Finished spaghetti for customer {customer}")


def main():
    start = time()
    customers = ["A", "B", "C"]
    threads = []

    for customer in customers:
        t = threading.Thread(
            target=cook_spaghetti,
            args=(customer,),
            name=f"Chef-{customer}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Total time: {time() - start:.2f} seconds")


if __name__ == "__main__":
    main()
```

### สิ่งที่ควรเกิดขึ้น

```text
A เริ่ม
B เริ่ม
C เริ่ม
รอประมาณ 2 วิ
A/B/C เสร็จใกล้ ๆ กัน
```

เวลารวมควรประมาณ:

```text
2 seconds
```

### ข้อควรระวัง

`args=(customer,)` ต้องมี comma หลัง `customer` เพราะ Python ต้องการ tuple

ผิด:

```python
args=(customer)
```

ถูก:

```python
args=(customer,)
```

### คำถามทบทวน

1. ถ้าไม่เรียก `start()` thread จะทำงานไหม?
2. ถ้าไม่เรียก `join()` main program อาจจบก่อน thread ทำงานเสร็จไหม?
3. Thread เหมาะกับงานรอ เช่น `sleep()` หรือ network ไหม?

---

## 9. Lab 3 — `restaurant_01_multiprocess.py`

### เป้าหมาย

เขียนร้านอาหารแบบใช้ process แยกจริง ๆ เพื่อให้เห็นว่าแต่ละงานสามารถไปรันใน process ของตัวเองได้

### ความรู้ที่ใช้

```python
import os
import multiprocessing
from time import sleep, ctime, time
```

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `multiprocessing.Process(...)` | สร้าง process ใหม่ |
| `target=cook_spaghetti` | function ที่ process ลูกจะรัน |
| `args=(customer,)` | ส่ง argument เข้า process |
| `start()` | เริ่ม process |
| `join()` | รอ process จบ |
| `os.getpid()` | ดู process id ปัจจุบัน |

### โครงสร้างที่ควรเขียน

```python
import os
import multiprocessing
from time import sleep, ctime, time


def cook_spaghetti(customer):
    pid = os.getpid()
    print(f"{ctime()} -> [PID {pid}] Start cooking spaghetti for customer {customer}")
    sleep(2)
    print(f"{ctime()} -> [PID {pid}] Finished spaghetti for customer {customer}")


def main():
    start = time()
    customers = ["A", "B", "C"]
    processes = []

    for customer in customers:
        p = multiprocessing.Process(
            target=cook_spaghetti,
            args=(customer,)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"Total time: {time() - start:.2f} seconds")


if __name__ == "__main__":
    main()
```

### สิ่งที่ควรเกิดขึ้น

```text
ลูกค้า A, B, C ถูกทำใน process แยกกัน
แต่ละ process มี PID ต่างกัน
เวลารวมประมาณ 2 วินาที
```

### ข้อควรระวังสำคัญ

ต้องมีบรรทัดนี้เสมอ:

```python
if __name__ == "__main__":
    main()
```

โดยเฉพาะบน Windows ถ้าไม่มี guard นี้ multiprocessing อาจสร้าง process วนผิดปกติได้ค่ะ

### คำถามทบทวน

1. PID ของแต่ละ process เหมือนกันหรือต่างกัน?
2. ทำไม multiprocessing หนักกว่า threading?
3. ถ้างานเป็นคำนวณหนัก CPU จริง ๆ multiprocessing มีประโยชน์กว่า asyncio ไหม?

---

## 10. Lab 4 — `restaurant_01_asyncio.py`

### เป้าหมาย

เขียนร้านอาหารแบบ `asyncio` โดยใช้ event loop จัดการหลาย task ใน thread เดียว

### ความรู้ที่ใช้

```python
import asyncio
from time import ctime, time
```

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `async def` | ประกาศ coroutine function |
| `await asyncio.sleep(2)` | รอแบบ non-blocking |
| `asyncio.create_task(...)` | สร้าง task ให้ event loop รัน |
| `asyncio.gather(*tasks)` | รอ task ทุกตัวให้เสร็จ |
| `asyncio.run(main())` | เปิด event loop และรัน main coroutine |

### โครงสร้างที่ควรเขียน

```python
import asyncio
from time import ctime, time


async def cook_spaghetti(customer):
    print(f"{ctime()} -> Start cooking spaghetti for customer {customer}")
    await asyncio.sleep(2)
    print(f"{ctime()} -> Finished spaghetti for customer {customer}")


async def main():
    start = time()
    customers = ["A", "B", "C"]
    tasks = []

    for customer in customers:
        task = asyncio.create_task(cook_spaghetti(customer))
        tasks.append(task)

    await asyncio.gather(*tasks)

    print(f"Total time: {time() - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
```

### สิ่งที่ควรเกิดขึ้น

```text
A เริ่ม
B เริ่ม
C เริ่ม
รอประมาณ 2 วิ
A/B/C เสร็จใกล้ ๆ กัน
Total time ประมาณ 2 วิ
```

### ทำไม asyncio ถึงเร็วกว่า simple ในโจทย์นี้

เพราะ `await asyncio.sleep(2)` เป็นการบอก event loop ว่า:

```text
ตอนนี้ task นี้กำลังรออยู่ ไปให้ task อื่นทำงานก่อนได้
```

แต่ `sleep(2)` ใน simple version คือ:

```text
หยุดทั้งโปรแกรมไว้ 2 วินาที
```

### คำถามทบทวน

1. ถ้าเปลี่ยน `await asyncio.sleep(2)` เป็น `time.sleep(2)` จะยัง concurrent อยู่ไหม?
2. ทำไมต้องใช้ `asyncio.run(main())`?
3. `asyncio.gather(*tasks)` ช่วยให้โค้ดอ่านง่ายกว่าการ `await` ทีละ task ยังไง?

---

## 11. Example รวม — Expected Behavior ของทั้ง 4 ไฟล์

ถ้าลูกค้า 3 คน และแต่ละคนใช้เวลา 2 วินาที ผลที่คาดหวังควรเป็นประมาณนี้:

| ไฟล์ | เริ่มพร้อมกันไหม | เวลารวมโดยประมาณ | สิ่งที่สังเกต |
|---|---|---:|---|
| `restaurant_01_simple.py` | ไม่ | 6 วิ | ทำทีละคน A -> B -> C |
| `restaurant_01_thread.py` | ใช่ | 2 วิ | หลาย thread, thread name ต่างกัน |
| `restaurant_01_multiprocess.py` | ใช่ | 2 วิ | หลาย process, PID ต่างกัน |
| `restaurant_01_asyncio.py` | ใช่แบบ event loop | 2 วิ | thread เดียวก็สลับ task ได้ถ้าเป็นงานรอ |

ตัวอย่าง output แบบ simple:

```text
Wed Jul  1 10:00:00 2026 -> Start cooking spaghetti for customer A
Wed Jul  1 10:00:02 2026 -> Finished spaghetti for customer A
Wed Jul  1 10:00:02 2026 -> Start cooking spaghetti for customer B
Wed Jul  1 10:00:04 2026 -> Finished spaghetti for customer B
Wed Jul  1 10:00:04 2026 -> Start cooking spaghetti for customer C
Wed Jul  1 10:00:06 2026 -> Finished spaghetti for customer C
Total time: 6.00 seconds
```

ตัวอย่าง output แบบ asyncio/thread/process:

```text
Wed Jul  1 10:00:00 2026 -> Start cooking spaghetti for customer A
Wed Jul  1 10:00:00 2026 -> Start cooking spaghetti for customer B
Wed Jul  1 10:00:00 2026 -> Start cooking spaghetti for customer C
Wed Jul  1 10:00:02 2026 -> Finished spaghetti for customer A
Wed Jul  1 10:00:02 2026 -> Finished spaghetti for customer B
Wed Jul  1 10:00:02 2026 -> Finished spaghetti for customer C
Total time: 2.00 seconds
```

หมายเหตุ: ลำดับ output ของ concurrent version อาจไม่เหมือนเดิมทุกครั้ง เพราะงานทำพร้อมกัน/สลับกันค่ะ

---

## 12. Mini Lab สำหรับใบลองทำเอง

### Mini Lab A — เพิ่มลูกค้า

แก้ทุกไฟล์ให้มีลูกค้า 5 คน:

```python
customers = ["A", "B", "C", "D", "E"]
```

แล้วตอบคำถาม:

| ไฟล์ | เวลาที่ควรได้ถ้าคนละ 2 วิ |
|---|---:|
| simple | ประมาณ 10 วิ |
| thread | ประมาณ 2 วิ |
| multiprocess | ประมาณ 2 วิ |
| asyncio | ประมาณ 2 วิ |

---

### Mini Lab B — เพิ่มเมนูอาหาร

เปลี่ยนจาก spaghetti อย่างเดียว เป็นให้แต่ละลูกค้าสั่งคนละเมนู:

```python
orders = [
    ("A", "spaghetti"),
    ("B", "steak"),
    ("C", "salad"),
]
```

function อาจเปลี่ยนเป็น:

```python
def cook_order(customer, menu):
    print(f"Start cooking {menu} for customer {customer}")
```

สำหรับ asyncio:

```python
async def cook_order(customer, menu):
    print(f"Start cooking {menu} for customer {customer}")
    await asyncio.sleep(2)
```

---

### Mini Lab C — คืนค่าราคาอาหารแบบ `asyncio10.py`

ลองให้ `restaurant_01_asyncio.py` return ราคาอาหารกลับมา:

```python
async def cook_order(customer, price):
    await asyncio.sleep(2)
    return price
```

แล้วใน `main()`:

```python
results = await asyncio.gather(*tasks)
print(f"Total income: {sum(results)} baht")
```

คำถาม:

1. `results` เป็น list ของอะไร?
2. ทำไม `asyncio.gather()` ถึงเหมาะกับการเก็บ return value จากหลาย task?

---

## 13. Checklist ก่อนส่ง Lab

ใช้ checklist นี้เช็กทั้ง 4 ไฟล์ค่ะ

### Common checklist

- [ ] มี `customers = ["A", "B", "C"]`
- [ ] มี function ทำอาหาร เช่น `cook_spaghetti(customer)`
- [ ] มี log ตอนเริ่มและตอนเสร็จ
- [ ] มีการจับเวลารวมด้วย `time()`
- [ ] มี `if __name__ == "__main__":`
- [ ] รันแล้วไม่มี error

### Simple checklist

- [ ] ใช้ `sleep(2)`
- [ ] ใช้ `for customer in customers:` แล้วเรียก function ตรง ๆ
- [ ] เวลารวมประมาณ 6 วินาที

### Thread checklist

- [ ] import `threading`
- [ ] สร้าง `threading.Thread(...)`
- [ ] เรียก `start()` ทุก thread
- [ ] เรียก `join()` ทุก thread
- [ ] เวลารวมประมาณ 2 วินาที

### Multiprocess checklist

- [ ] import `multiprocessing`
- [ ] สร้าง `multiprocessing.Process(...)`
- [ ] เรียก `start()` ทุก process
- [ ] เรียก `join()` ทุก process
- [ ] มี `if __name__ == "__main__":` แน่นอน
- [ ] เวลารวมประมาณ 2 วินาที

### Asyncio checklist

- [ ] import `asyncio`
- [ ] function หลักเป็น `async def`
- [ ] ใช้ `await asyncio.sleep(2)` ไม่ใช่ `time.sleep(2)`
- [ ] สร้าง task ด้วย `asyncio.create_task(...)`
- [ ] รอทุก task ด้วย `await asyncio.gather(*tasks)` หรือ await ทีละ task
- [ ] เริ่มโปรแกรมด้วย `asyncio.run(main())`
- [ ] เวลารวมประมาณ 2 วินาที

---

## 14. ข้อผิดพลาดที่เจอบ่อย

### 14.1 เรียก async function แล้วไม่มีอะไรเกิดขึ้น

ผิด:

```python
async def main():
    print("Hello")

main()
```

เพราะ `main()` จะคืน coroutine object แต่ยังไม่รันจริง

ถูก:

```python
asyncio.run(main())
```

---

### 14.2 ใช้ `time.sleep()` ใน async function

ผิด:

```python
async def cook():
    time.sleep(2)
```

เพราะมัน block ทั้ง event loop

ถูก:

```python
async def cook():
    await asyncio.sleep(2)
```

---

### 14.3 สร้าง task แล้วไม่ได้ await

ผิด:

```python
asyncio.create_task(cook_spaghetti("A"))
```

ถ้า main จบเร็ว task อาจยังทำไม่เสร็จ

ถูก:

```python
task = asyncio.create_task(cook_spaghetti("A"))
await task
```

หรือหลาย task:

```python
await asyncio.gather(*tasks)
```

---

### 14.4 ลืม comma ใน `args`

ผิด:

```python
args=(customer)
```

ถูก:

```python
args=(customer,)
```

---

### 14.5 ลืม `if __name__ == "__main__"` ใน multiprocessing

ควรมีเสมอ:

```python
if __name__ == "__main__":
    main()
```

โดยเฉพาะตอนรันบน Windows ค่ะ

---

## 15. คำสั่งสำหรับรันตรวจงาน

รันทีละไฟล์:

```bash
python3 Week2/restaurant_01_simple.py
python3 Week2/restaurant_01_thread.py
python3 Week2/restaurant_01_multiprocess.py
python3 Week2/restaurant_01_asyncio.py
```

ตรวจ syntax ทั้งชุด:

```bash
python3 -m py_compile \
  Week2/restaurant_01_simple.py \
  Week2/restaurant_01_thread.py \
  Week2/restaurant_01_multiprocess.py \
  Week2/restaurant_01_asyncio.py
```

ถ้าจะรันตัวอย่าง `asyncio01-10` ทั้งหมด:

```bash
for f in Week2/asyncio{01..10}.py; do
  echo "===== $f ====="
  python3 "$f"
  echo
done
```

---

## 16. สรุปสุดท้ายแบบจำง่าย

```text
simple          = ทำทีละงาน ช้าที่สุด แต่อ่านง่ายสุด
threading       = หลาย thread เหมาะกับงานรอ / I/O
multiprocessing = หลาย process เหมาะกับงาน CPU หนัก
asyncio         = thread เดียว + event loop เหมาะกับงานรอจำนวนมาก
```

สำหรับ Week2 ให้จำหัวใจของ `asyncio` แบบนี้ค่ะ:

```text
async def สร้าง coroutine
await คือจุดที่ยอมให้ event loop ไปทำงานอื่น
create_task ทำให้งานเริ่ม concurrent
gather ใช้รอหลาย task พร้อมกัน
asyncio.run ใช้เปิด event loop
```

ถ้าใบเข้าใจ 5 บรรทัดนี้ ใบจะอ่านไฟล์ `asyncio01.py` ถึง `asyncio10.py` และทำ Lab ร้านอาหาร 4 ไฟล์ต่อได้แล้วค่ะ
