# Week 8 — Asyncio Queue & Producer–Consumer Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงปัจจุบันทั้ง 8 ไฟล์** ในโฟลเดอร์ `Week8` โดยเรียงจากพื้นฐาน synchronous/asynchronous ไปจนถึงระบบ Producer–Consumer ที่มี Consumer หลายตัว

ไฟล์ที่ใช้เรียน:

1. `Week8/01_synchronous_vs_asynchronous.py`
2. `Week8/02_basic_asyncio_queue.py`
3. `Week8/03_put_and_get_mechanism.py`
4. `Week8/04_bounded_queue_backpressure.py`
5. `Week8/05_task_completion_and_join.py`
6. `Week8/06_scraper_downloader.py`
7. `Week8/07_coupon_producer_consumer.py`
8. `Week8/08_coupon_producer_consumer2.py`

> เป้าหมาย: อ่านจบแล้วอธิบายได้ว่า `asyncio.Queue` ทำงานแบบ FIFO อย่างไร, `put()` และ `get()` รอเมื่อใด, bounded queue สร้าง backpressure อย่างไร, `task_done()` และ `join()` ทำงานร่วมกันอย่างไร และควรปิด Consumer ด้วยการ cancel หรือ sentinel อย่างไร

---

## 1. ภาพใหญ่ของ Week 8

Week 8 เปลี่ยนจากการ “สร้าง Task หลายงาน” มาเป็นการ “ส่งข้อมูลระหว่าง Task” อย่างเป็นระบบ

ปัญหาตัวอย่างมีสองบทบาท:

- **Producer (ผู้ผลิต)** — สร้างงานหรือข้อมูล แล้วใส่เข้า Queue
- **Consumer (ผู้บริโภค/ผู้ประมวลผล)** — ดึงงานออกจาก Queue แล้วประมวลผล

Queue อยู่ตรงกลางและช่วยแยกความเร็วของสองฝั่ง:

```text
                    asyncio.Queue
Producer          (พื้นที่พักงาน)                 Consumer
─────────      ┌──────────────────┐             ──────────
สร้าง item ──> │ item 1 | item 2  │ ── get() ─> ประมวลผล
               └──────────────────┘
                  put()      FIFO
```

เมื่อมีหลาย Consumer:

```text
                              ┌──> Consumer_01
Producer ── put() ──> Queue ──┤
                              └──> Consumer_02

Consumer ตัวใดมาถึง await queue.get() และได้รับการ schedule ก่อน
จะได้ item ถัดไปจากหัวคิว
```

Queue ช่วยเรื่องสำคัญ 4 อย่าง:

1. เก็บงานระหว่าง Producer กับ Consumer
2. รักษาลำดับแบบ FIFO
3. ให้ `get()` รอได้โดยไม่ block event loop เมื่อคิวว่าง
4. ให้ `put()` รอได้เมื่อ bounded queue เต็ม เพื่อควบคุมความเร็วของ Producer

---

## 2. คำศัพท์พื้นฐาน

| คำ | ความหมายแบบง่าย | ตัวอย่างใน Week 8 |
|---|---|---|
| Synchronous | ทำทีละงาน งานถัดไปต้องรองานก่อนหน้า | งาน A 2 วินาที แล้วงาน B 3 วินาที |
| Asynchronous | สลับไปทำงานอื่นได้ระหว่างรอ I/O | A และ B เริ่มใกล้กันด้วย `gather()` |
| Blocking | คำสั่งทำให้ thread หยุดรอ | `time.sleep()` |
| Non-blocking wait | ระหว่างรอเปิดโอกาสให้ event loop รัน Task อื่น | `await asyncio.sleep()` |
| Coroutine | งานที่ประกาศด้วย `async def` | `producer()`, `consumer()` |
| Task | Coroutine ที่ถูก schedule บน event loop | ผลจาก `asyncio.create_task()` |
| Event loop | ตัวสลับและจัดตาราง coroutine/Task | เริ่มด้วย `asyncio.run(main())` |
| Queue | โครงสร้างพักข้อมูลระหว่าง Task | `asyncio.Queue()` |
| FIFO | First In, First Out — เข้าก่อนออกก่อน | `Order #1` ออกก่อน `Order #2` |
| Producer | ผู้สร้าง item แล้ว `put()` เข้าคิว | ผู้สร้าง coupon |
| Consumer | ผู้ `get()` item ไปประมวลผล | ผู้รับ coupon |
| Bounded queue | Queue ที่จำกัดจำนวน item | `asyncio.Queue(maxsize=2)` |
| Backpressure | แรงต้านที่ทำให้ Producer ต้องชะลอเมื่อคิวเต็ม | `await queue.put(...)` รอพื้นที่ |
| Unfinished task | item ที่ `put()` แล้ว แต่ยังไม่ได้รับ `task_done()` | ตัวนับภายใน Queue |
| `task_done()` | แจ้งว่า item ที่ `get()` มาหนึ่งชิ้นทำเสร็จแล้ว | Worker เรียกหลังประมวลผล |
| `join()` | รอจน unfinished-task count เป็นศูนย์ | `await queue.join()` |
| Sentinel | ค่าพิเศษสำหรับสั่ง Consumer ให้หยุด | `None` |
| Cancellation | ส่งคำขอยกเลิก Task | `task.cancel()` |
| Race condition | ผลขึ้นกับจังหวะการสลับ Task | เช็ก `empty()` แล้วสถานะเปลี่ยนก่อน `get()` |

---

## 3. API สำคัญของ `asyncio.Queue`

### 3.1 สร้าง Queue

```python
queue = asyncio.Queue()
```

ค่าเริ่มต้นคือ queue แบบไม่กำหนดขีดจำกัดที่ใช้งานจริง (`maxsize=0`)

สร้าง queue จำกัดขนาด:

```python
queue = asyncio.Queue(maxsize=2)
```

### 3.2 ใส่ข้อมูล

```python
await queue.put(item)
```

- Queue ปกติ: ใส่ได้ทันทีโดยทั่วไป
- Bounded queue ที่เต็ม: coroutine จะรอจนมีพื้นที่
- ทุก `put()` เพิ่ม unfinished-task count ภายใน Queue 1

### 3.3 ดึงข้อมูล

```python
item = await queue.get()
```

- ถ้ามีข้อมูล จะดึง item หัวคิว
- ถ้าคิวว่าง จะรอแบบ async
- การรอไม่ทำให้ event loop ค้าง งานอื่นจึงยังทำต่อได้

### 3.4 ดูจำนวนและสถานะ

```python
queue.qsize()
queue.empty()
queue.full()
```

ค่าพวกนี้เป็นเพียง snapshot ณ ขณะตรวจ ในระบบ concurrent สถานะอาจเปลี่ยนทันทีหลังตรวจ

### 3.5 รับรองว่างานหนึ่งชิ้นเสร็จแล้ว

```python
queue.task_done()
```

ต้องเรียก **หนึ่งครั้งต่อหนึ่ง item ที่ `get()` ออกมา** เมื่อประมวลผล item นั้นเสร็จ

### 3.6 รอให้งานที่ใส่ไว้เสร็จครบ

```python
await queue.join()
```

`join()` ไม่ได้รอให้ Queue “ดูเหมือนว่าง” เท่านั้น แต่รอจนจำนวน `put()` ที่ยังไม่ได้จับคู่กับ `task_done()` เหลือศูนย์

```text
put(A)        unfinished = 1
put(B)        unfinished = 2
get(A)        unfinished = 2   # get อย่างเดียวยังไม่ลด
 task_done()  unfinished = 1
get(B)        unfinished = 1
 task_done()  unfinished = 0   # join() จึงผ่าน
```

---

# Part A — พื้นฐาน Async และ Queue

## 4. `01_synchronous_vs_asynchronous.py`

### 4.1 เป้าหมาย

เปรียบเทียบการรอแบบ blocking กับการรอแบบ async โดยใช้งาน A = 2 วินาที และ B = 3 วินาที

### 4.2 ฝั่ง Synchronous

```python
sync_task("A", 2)
sync_task("B", 3)
```

ภายใน `sync_task()` ใช้:

```python
time.sleep(delay)
```

Flow:

```text
0s              2s                         5s
|--- Sync A ---|---------- Sync B ----------|
```

จึงใช้เวลาประมาณ:

```text
2 + 3 = 5 วินาที
```

`time.sleep()` หยุด thread ที่กำลังทำงาน จึงเริ่ม B ไม่ได้จนกว่า A จะเสร็จ

### 4.3 ฝั่ง Asynchronous

```python
await asyncio.gather(
    async_task("A", 2),
    async_task("B", 3)
)
```

ภายใน `async_task()` ใช้:

```python
await asyncio.sleep(delay)
```

Flow:

```text
0s              2s              3s
|--- Async A ---|
|---------- Async B ------------|
```

ทั้งสองงานคืบหน้าร่วมกัน เวลารวมจึงใกล้เวลาของงานที่ช้าที่สุด:

```text
max(2, 3) = ประมาณ 3 วินาที
```

### 4.4 Sync 5 วินาที vs Async ประมาณ 3 วินาที

| แบบ | วิธีรอ | สูตรเวลา | เวลาที่คาด |
|---|---|---:|---:|
| Sync | เรียง A แล้ว B | `2 + 3` | ~5 วินาที |
| Async | A และ B overlap | `max(2, 3)` | ~3 วินาที |

เมื่อรันไฟล์ทั้งไฟล์ จะทำ Sync ก่อนแล้ว Async ดังนั้น wall time รวมประมาณ 8 วินาที ไม่ใช่ 3 วินาที

### 4.5 Expected behavior

```text
=== เริ่มทำงานแบบ Synchronous ===
[Sync] เริ่มงาน A ...
[Sync] งาน A เสร็จสิ้น!
[Sync] เริ่มงาน B ...
[Sync] งาน B เสร็จสิ้น!
เวลารวมแบบ Sync: 5.00 วินาที

=== เริ่มทำงานแบบ Asynchronous ===
[Async] เริ่มงาน A ...
[Async] เริ่มงาน B ...
[Async] งาน A เสร็จสิ้น!
[Async] งาน B เสร็จสิ้น!
เวลารวมแบบ Async: 3.00 วินาที
```

ค่าจริงอาจต่างเล็กน้อยจาก overhead ของระบบ

### 4.6 จำให้ได้

Async ไม่ได้ทำให้ delay 3 วินาทีหายไป แต่ทำให้เวลา 2 วินาทีของ A ซ้อนอยู่ภายในช่วงรอ 3 วินาทีของ B

---

## 5. `02_basic_asyncio_queue.py`

### 5.1 เป้าหมาย

เรียนโครงสร้าง Producer–Consumer ขั้นพื้นฐานและลำดับ FIFO

Producer ใส่ข้อมูล:

```python
[" Order #1", "Order #2", "Order #3"]
```

เวลาผลิตต่อชิ้น = `0.5` วินาที และเวลาประมวลผลของ Consumer ต่อชิ้น = `1` วินาที

### 5.2 Producer

```python
for item in [" Order #1", "Order #2", "Order #3"]:
    await queue.put(item)
    await asyncio.sleep(0.5)
```

ข้อมูลถูก put ตามลำดับ 1 → 2 → 3

### 5.3 Consumer และ FIFO

```python
item = await queue.get()
```

เพราะ Queue เป็น FIFO ลำดับที่ Consumer ได้ควรเป็น:

```text
" Order #1" -> "Order #2" -> "Order #3"
```

Queue ไม่ได้เรียงตามตัวอักษรหรือเลข แต่รักษาลำดับที่ put เข้ามา

### 5.4 รันพร้อมกัน

```python
await asyncio.gather(
    producer(queue),
    consumer(queue)
)
```

Producer และ Consumer เริ่มเป็นงานร่วมกัน Consumer อาจรอข้อมูล และ Producer ยังมีโอกาสผลิต item ต่อได้ระหว่าง Consumer `await asyncio.sleep(1)`

### 5.5 Caveat ของโค้ดปัจจุบัน: leading space

item แรกเขียนเป็น:

```python
" Order #1"
```

มีช่องว่างนำหน้าก่อนคำว่า `Order` จริง ๆ จึงพิมพ์ต่างจาก item อื่น และการเปรียบเทียบ string แบบ exact จะถือว่า:

```python
" Order #1" != "Order #1"
```

คู่มือนี้บันทึกตามโค้ดปัจจุบัน ไม่ได้แก้ Python file

### 5.6 Caveat ของโค้ดปัจจุบัน: stop condition ผูกกับข้อมูล

Consumer หยุดด้วย:

```python
if item == "Order #3":
    break
```

ตัวอย่างปัจจุบันจบได้ เพราะ item สุดท้ายสะกดตรงกับ `"Order #3"` แต่รูปแบบนี้เปราะบาง:

- ถ้าเปลี่ยนชื่อ item สุดท้าย Consumer จะรอ `get()` ตลอดไป
- ถ้ามี `"Order #3"` อยู่กลางคิว Consumer จะหยุดเร็วและทิ้งงานที่เหลือ
- ถ้า `"Order #3"` มีช่องว่างนำหน้าเหมือน item แรก เงื่อนไขจะไม่ตรง
- business data ถูกใช้เป็นทั้ง “งานจริง” และ “สัญญาณหยุด”

แนวคิดที่ทนกว่าคือส่ง sentinel เช่น `None` แยกจากข้อมูลจริง ซึ่งไฟล์ 06–08 แสดงให้เห็น

### 5.7 Caveat เพิ่มเติม: ยังไม่มี `task_done()`

ไฟล์นี้ไม่ได้ใช้ `queue.join()` จึงยังไม่ต้องพึ่ง unfinished-task accounting เพื่อจบตัวอย่าง แต่ถ้านำไปต่อยอดให้ `main()` เรียก `join()` ต้องเพิ่ม `task_done()` ให้ทุก item ที่ get ออกมา มิฉะนั้นโปรแกรมจะรอไม่จบ

---

## 6. `03_put_and_get_mechanism.py`

### 6.1 เป้าหมาย

พิสูจน์ว่า `await queue.get()` รอข้อมูลจากคิวว่างได้ โดยไม่ block event loop

ค่าจริง:

- Producer รอ `2` วินาทีก่อนผลิต
- item คือ `"Data-Alpha"`
- Consumer พยายาม `get()` ทันที

### 6.2 Timeline

```text
เวลา 0s
  eager_consumer: เรียก await queue.get()
  Queue ว่าง -> Consumer ถูกพักไว้

เวลา 0s–2s
  event loop ยังรัน slow_producer ได้
  Producer รอ await asyncio.sleep(2)

เวลาประมาณ 2s
  Producer put("Data-Alpha")
  Consumer ถูกปลุกและได้รับ Data-Alpha
```

Architecture:

```text
Consumer: await get() ──รอ──┐
                            │ เมื่อ put เกิดขึ้น
Producer: sleep(2) -> put ──┴──> Consumer ทำต่อ
```

### 6.3 จุดสำคัญ

คำว่า “รอ” ไม่เท่ากับ “แฮงก์” เสมอ:

- `queue.get()` รอเฉพาะ coroutine นี้
- event loop ยังสลับไปทำ Producer ได้
- เมื่อมี item ระบบปลุก Consumer โดยอัตโนมัติ

### 6.4 Expected behavior

บรรทัด Consumer ที่พยายาม get จะออกก่อน จากนั้นประมาณ 2 วินาทีจึงเห็น Producer put และ Consumer รับ `Data-Alpha`

---

## 7. `04_bounded_queue_backpressure.py`

### 7.1 เป้าหมาย

เรียน bounded queue และ backpressure เมื่อ Producer เร็วกกว่า Consumer

ค่าจริง:

| ค่า | จำนวน/เวลา |
|---|---:|
| งาน | `Task #1` ถึง `Task #5` |
| Queue capacity | `maxsize=2` |
| Consumer รอก่อนเริ่ม | `1` วินาที |
| เวลาประมวลผลต่อชิ้น | `2` วินาที |

### 7.2 ทำไม `maxsize=2` สำคัญ

```python
bounded_queue = asyncio.Queue(maxsize=2)
```

Producer ใส่ Task #1 และ #2 ได้จนคิวเต็ม เมื่อพยายามใส่ Task #3:

```python
await queue.put("Task #3")
```

coroutine ของ Producer ต้องรอจน Consumer ดึง item ออกอย่างน้อยหนึ่งชิ้น

### 7.3 Backpressure

```text
Producer เร็ว                       Consumer ช้า
   |                                   |
put #1 -> Queue [#1]                   |
put #2 -> Queue [#1, #2] (เต็ม)        |
put #3 -> ต้องรอ                       |
   |                              get #1
   └──────── มีพื้นที่แล้ว ────────────┘
put #3 สำเร็จ -> Queue [#2, #3]
```

Backpressure ป้องกันไม่ให้ Producer สร้างข้อมูลสะสมไม่จำกัดจนใช้หน่วยความจำมากเกินไป

### 7.4 `qsize()` ที่พิมพ์คือค่าก่อน `put()`

บรรทัดนี้ทำงานก่อนใส่ item:

```python
print(f"... (คิวนับได้ {queue.qsize()} ชิ้น)")
await queue.put(...)
```

ถ้าเห็น “คิวนับได้ 2 ชิ้น” แล้วข้อความ “ใส่สำเร็จ” ออกช้า แปลว่า `put()` กำลังถูก backpressure

### 7.5 Caveat ของโค้ดปัจจุบัน: `while not queue.empty()`

Consumer ใช้:

```python
while not queue.empty():
    item = await queue.get()
```

โค้ดนี้รันได้ในตัวอย่างปัจจุบันเพราะ:

- Producer เริ่มก่อน
- Consumer ตั้งใจรอ `1` วินาที
- Queue `maxsize=2` ทำให้เมื่อ Consumer เริ่ม มีงานอยู่แล้ว
- Producer และ Consumer ประสานกันตาม timing ที่กำหนด

แต่ `empty()` เป็น snapshot และรูปแบบ check-then-act มี race:

```text
ตรวจว่าไม่ว่าง -> Task ถูกสลับ -> Consumer อื่นดึง item สุดท้าย
-> กลับมา get() แล้วต้องรอทั้งที่ไม่มี Producer ส่งเพิ่ม
```

หรือในอีกกรณี Consumer อาจเห็นว่างและออกจาก loop ก่อน Producer ที่ช้ากว่าจะใส่งานใหม่

ดังนั้น `while not queue.empty()` เหมาะเป็น **บทเรียนแบบย่อที่ควบคุม timing** มากกว่า lifecycle ของระบบจริง แนวทางจริงควรใช้ sentinel, จำนวนงานที่แน่นอน หรือ `join()` ร่วมกับ protocol ปิด worker

### 7.6 Expected behavior

- Producer ใส่ #1 และ #2 ได้เร็ว
- การใส่ #3, #4 และ #5 ถูกควบคุมด้วยพื้นที่ที่ Consumer คืนให้
- Consumer ประมวลผลครบ 5 ชิ้น ชิ้นละประมาณ 2 วินาที
- จากการรันปัจจุบันไฟล์จบประมาณ 11 วินาที (รวมการรอเริ่ม 1 วินาที)

---

# Part B — ติดตามงานให้เสร็จและปิด Worker

## 8. `05_task_completion_and_join.py`

### 8.1 เป้าหมาย

ใช้ `task_done()` และ `join()` เพื่อให้โปรแกรมหลักรู้ว่างานทั้ง 5 ชิ้นถูกประมวลผลเสร็จจริง

ค่าจริง:

- งาน `Job #1` ถึง `Job #5`
- Worker 2 ตัว: `Worker-1`, `Worker-2`
- ประมวลผลงานละ `1` วินาที

### 8.2 ใส่งานก่อนสร้าง Worker

```python
for i in range(1, 6):
    await queue.put(f"Job #{i}")
```

หลัง loop unfinished-task count = 5

### 8.3 สร้าง Worker เป็น background tasks

```python
task = asyncio.create_task(worker(i, queue))
```

สร้าง Worker 2 ตัวและเก็บ Task references ใน list `workers`

### 8.4 Worker ทำงานตลอดไป

```python
while True:
    item = await queue.get()
    await asyncio.sleep(1)
    queue.task_done()
```

หลังงานหมด Worker ไม่รู้เองว่าจะหยุด จึงกลับไปรอ `queue.get()` รอบถัดไป

### 8.5 `task_done()` กับ `join()`

ทุกครั้งที่ Worker ทำ Job เสร็จ จะเรียก:

```python
queue.task_done()
```

`main()` รอ:

```python
await queue.join()
```

เมื่อมี `task_done()` ครบ 5 ครั้ง ตัวนับจึงเป็นศูนย์และ `join()` ผ่าน

> `queue.empty()` หมายถึงตอนนี้ไม่มี item รอถูก get ส่วน `queue.join()` หมายถึง item ที่ put ทั้งหมดได้รับการยืนยันว่าประมวลผลเสร็จแล้ว ความหมายไม่เหมือนกัน

### 8.6 ทำไมต้อง cancel Worker

หลัง `join()` Worker ทั้งสองยังอยู่ใน `while True` และรอ `get()` จึงยกเลิกด้วย:

```python
for task in workers:
    task.cancel()
```

นี่คือ shutdown แบบ cancellation ต่างจากไฟล์ 06–08 ที่ใช้ sentinel

### 8.7 Caveat ของโค้ดปัจจุบัน

ไฟล์นี้ส่ง `cancel()` แต่ไม่ได้ await Task หลัง cancel แนวทาง cleanup ที่ชัดเจนกว่าในโปรแกรมทั่วไปคือ:

```python
for task in workers:
    task.cancel()
await asyncio.gather(*workers, return_exceptions=True)
```

อย่างไรก็ตาม คู่มือนี้อธิบายโค้ดปัจจุบันและไม่ได้แก้ไฟล์ Python

### 8.8 เวลาที่คาด

Worker 2 ตัวแบ่ง 5 งาน:

```text
รอบ 1: Job #1, #2
รอบ 2: Job #3, #4
รอบ 3: Job #5
```

จึงใช้เวลาประมาณ 3 วินาที ไม่ใช่ 5 วินาที

### 8.9 ข้อผิดพลาดสำคัญ

- ลืม `task_done()` หนึ่งครั้ง → `join()` รอตลอดไป
- เรียก `task_done()` มากกว่าจำนวน item ที่ put/get → เกิด `ValueError`
- `join()` ไม่ได้หยุด Worker ที่วน `while True` → ต้อง cancel หรือส่ง sentinel

---

# Part C — Producer–Consumer แบบใช้งานจริงขึ้น

## 9. `06_scraper_downloader.py`

### 9.1 เป้าหมายและสถาปัตยกรรม

จำลอง pipeline ที่ Producer สแกนหน้าเว็บและ Consumer ดาวน์โหลดรูป

```text
pages 3 หน้า
    |
    v
link_scraper (Producer)
    | สร้าง 2 URL ต่อหน้า
    v
asyncio.Queue (รวม 6 URL, FIFO)
    |
    v
image_downloader("Downloader_01")
    | ดาวน์โหลดทีละ URL
    v
ดาวน์โหลดครบ 6 รูป -> รับ None -> หยุด
```

### 9.2 ข้อมูลจริง

```python
pages = ["page_1", "page_2", "page_3"]
```

แต่ละหน้าสร้าง URL 2 รายการ:

```text
https://example.com/images/page_1_img1.jpg
https://example.com/images/page_1_img2.jpg
https://example.com/images/page_2_img1.jpg
https://example.com/images/page_2_img2.jpg
https://example.com/images/page_3_img1.jpg
https://example.com/images/page_3_img2.jpg
```

รวม `3 × 2 = 6` URL

- เวลาสแกนต่อหน้า = `0.3` วินาที
- เวลาดาวน์โหลดต่อรูป = `0.5` วินาที
- Consumer ชื่อ `Downloader_01`

### 9.3 สร้าง Producer และ Consumer ก่อนรอ

```python
producer_task = asyncio.create_task(link_scraper(queue, pages))
downloader_task = asyncio.create_task(
    image_downloader(queue, "Downloader_01")
)
```

ทั้งสอง Task เริ่มคืบหน้าร่วมกัน Downloader จึงดาวน์โหลด URL ชุดแรกได้ระหว่าง Producer กำลังสแกนหน้าถัดไป

### 9.4 ลำดับ shutdown

```text
1. await producer_task    รอให้ไม่มี URL ใหม่แล้ว
2. await queue.join()     รอให้ 6 URL ถูกดาวน์โหลดและ task_done ครบ
3. await queue.put(None)  ส่ง sentinel ให้ Consumer หนึ่งตัว
4. await downloader_task  รอ Consumer ปิดตัว
```

ลำดับนี้สำคัญมาก ถ้าส่ง `None` ก่อนงานจริงเสร็จ Consumer อาจหยุดและทิ้ง URL ในคิว

### 9.5 Sentinel และ `task_done()`

Consumer ทำ:

```python
img_url = await queue.get()
if img_url is None:
    queue.task_done()
    break
```

แม้ `None` ไม่ใช่งานดาวน์โหลด แต่ถูกใส่ด้วย `queue.put(None)` จึงเพิ่ม unfinished-task count และควรมี `task_done()` จับคู่เพื่อให้ accounting ของ Queue สอดคล้อง

ข้อสังเกต: ในไฟล์นี้ `join()` ถูกเรียก **ก่อน** put sentinel ดังนั้นการลืม `task_done()` ของ sentinel จะไม่ทำให้ `join()` ที่ผ่านมาแล้วค้างในรอบนี้ แต่จะทิ้งตัวนับภายในไม่สมดุล และอาจทำให้ `join()` ภายหลังค้างหากนำ Queue ไปใช้ต่อ

### 9.6 Expected behavior

- Producer สแกน `page_1`, `page_2`, `page_3`
- Downloader รับ URL ตาม FIFO
- ข้อความสุดท้ายรายงาน:

```text
[Downloader_01] ทำงานเสร็จสิ้น! ดาวน์โหลดรวมทั้งหมด 6 รูป
```

ไฟล์นี้เป็น simulation ไม่มี HTTP request จริงและไม่ได้สร้างไฟล์รูปจริง

---

## 10. `07_coupon_producer_consumer.py`

### 10.1 เป้าหมาย

Producer 1 ตัวสร้างคูปอง 20 ใบ และ Consumer 1 ตัวรับคูปองทั้งหมด

ค่าจริง:

| ค่า | ค่าปัจจุบัน |
|---|---|
| `TOTAL_COUPONS` | `20` |
| ชื่อ Coupon | `COUPON-01` ถึง `COUPON-20` |
| Producer delay | `0.02` วินาที/ใบ |
| Consumer delay | `0.05` วินาที/ใบ |
| Consumer name | `Consumer_01` |
| จำนวน sentinel | `1` |

### 10.2 การ format รหัส Coupon

```python
coupon = f"COUPON-{i:02d}"
```

`:02d` แปลว่าแสดง integer อย่างน้อย 2 หลักและเติมศูนย์ด้านหน้า:

```text
1  -> 01 -> COUPON-01
9  -> 09 -> COUPON-09
10 -> 10 -> COUPON-10
```

### 10.3 ทำไม log จึงสลับกัน

Producer ใช้ `0.02` วินาที ส่วน Consumer ใช้ `0.05` วินาที Producer จึงเร็วกว่าและอาจสร้างคูปองสะสมในคิว แต่ทั้งสอง Task ถูกสร้างก่อน await:

```python
prod_task = asyncio.create_task(...)
cons_task = asyncio.create_task(...)
```

จึงเห็นข้อความของ Producer และ Consumer interleave กัน

### 10.4 FIFO กับ Consumer เดียว

Consumer เดียวรับ item ตามหัวคิว จึงควรได้ list:

```text
['COUPON-01', 'COUPON-02', ..., 'COUPON-20']
```

ไม่มี Consumer ตัวอื่นมาแย่ง item ดังนั้นลำดับใน `claimed_coupons` เหมือนลำดับการ put

### 10.5 Lifecycle

```text
สร้าง Producer + Consumer
        |
await prod_task
        |
await queue.join()  รอคูปองจริง 20 ใบ task_done ครบ
        |
put(None)           sentinel 1 ตัวสำหรับ Consumer 1 ตัว
        |
await cons_task
```

Consumer เรียก `task_done()` ทั้งคูปองจริงและ sentinel

### 10.6 Expected behavior

- Producer สร้างครบ 20 ใบ
- `Consumer_01` เก็บครบ 20 ใบ
- ไม่มี coupon ซ้ำหรือหาย
- รายการสุดท้ายเรียง `COUPON-01` ถึง `COUPON-20`

เวลาจบโดยประมาณขึ้นกับฝั่งช้ากว่าและการ overlap โดย Consumer ต้องใช้ราว `20 × 0.05 = 1.0` วินาที บวก overhead และช่วงเริ่ม/จบเล็กน้อย

---

## 11. `08_coupon_producer_consumer2.py`

### 11.1 เป้าหมาย

ต่อยอดจากไฟล์ 07 ด้วย Consumer 2 ตัวที่ช่วยกันรับคูปองจาก Queue เดียว

ค่าจริง:

| ค่า | ค่าปัจจุบัน |
|---|---|
| `TOTAL_COUPONS` | `20` |
| `NUM_CONSUMERS` | `2` |
| ชื่อ Consumer | `Consumer_01`, `Consumer_02` |
| Producer delay | `0.01` วินาที/ใบ |
| Consumer delay | `0.04` วินาที/ใบ |
| จำนวน sentinel | `2` |

### 11.2 สร้าง Consumer 2 ตัว

```python
consumers = [
    asyncio.create_task(consumer(queue, f"Consumer_{i:02d}"))
    for i in range(1, NUM_CONSUMERS + 1)
]
```

เมื่อ `i` เป็น 1 และ 2 ชื่อจึงเป็น:

```text
Consumer_01
Consumer_02
```

### 11.3 การแบ่งงานไม่ใช่ค่าตายตัว

ทั้งสอง Consumer รอจาก Queue เดียวกัน Consumer ที่พร้อมและได้รับการ schedule ก่อนจะได้ coupon ถัดไป

ด้วย delay เท่ากัน มักเห็นรูปแบบใกล้เคียง:

```text
Consumer_01: COUPON-01, COUPON-03, ...
Consumer_02: COUPON-02, COUPON-04, ...
```

และอาจแบ่ง 10/10 แต่ **ห้ามใช้ 10/10 หรือ odd/even เป็นกฎตายตัว** เพราะ event-loop scheduling และสภาพเครื่องอาจทำให้แบ่งต่างกัน

สัญญาที่ควรตรวจคือ:

```text
จำนวนของ Consumer_01 + จำนวนของ Consumer_02 = 20
union ของทั้งสอง list = COUPON-01 ถึง COUPON-20
ไม่มี coupon ซ้ำ
ไม่มี coupon หาย
Consumer ทั้งสองหยุดได้
```

### 11.4 ทำไมต้องมี `None` สองตัว

Consumer แต่ละตัวต้อง get sentinel ของตัวเอง:

```python
for _ in range(NUM_CONSUMERS):
    await queue.put(None)
```

Architecture:

```text
Queue หลังงานจริงหมด: [None, None]
                         |     |
                         |     └──> Consumer_02 หยุด
                         └────────> Consumer_01 หยุด
```

ถ้าส่ง `None` เพียงตัวเดียว Consumer หนึ่งตัวหยุด แต่อีกตัวอาจรอ `queue.get()` ตลอดไป ทำให้ `gather(*consumers)` ไม่จบ

กฎจำง่าย:

```text
N long-running consumers -> N sentinels
```

### 11.5 รอ Consumer ทั้งหมด

```python
await asyncio.gather(*consumers)
```

Consumer แต่ละตัว return list ของตนเอง แม้โค้ดปัจจุบันไม่ได้เก็บค่าที่ `gather()` คืนมา จุดประสงค์หลักของบรรทัดนี้คือรอให้ทั้งสอง Task ปิดสมบูรณ์

หากต้องการตรวจผลรวม สามารถต่อยอดเป็น:

```python
results = await asyncio.gather(*consumers)
```

โดย `results` จะเป็น list ที่บรรจุ list คูปองของแต่ละ Consumer

### 11.6 Expected behavior

- Producer สร้าง 20 coupons
- Consumer 2 ตัวแบ่งงานกัน
- จำนวนรวมต้องเท่ากับ 20
- จบด้วย:

```text
=== ระบบประมวลผลคูปองแบบ Multi-Consumer ทำงานเสร็จสิ้นทั้งหมด ===
```

---

## 12. สถาปัตยกรรมเปรียบเทียบไฟล์ 06–08

```text
06 Scraper/Downloader
3 pages -> Producer -> [6 image URLs] -> 1 Downloader -> 1 None

07 Single Consumer
20 coupons -> Producer -> [Queue] -> 1 Consumer -> 1 None

08 Multi Consumer
                         ┌-> Consumer_01 -> None
20 coupons -> Producer -> Queue
                         └-> Consumer_02 -> None
```

| ไฟล์ | Producer | จำนวนงานจริง | Consumer | Sentinel |
|---|---|---:|---:|---:|
| `06_scraper_downloader.py` | สแกน 3 pages | 6 URLs | 1 | 1 |
| `07_coupon_producer_consumer.py` | สร้าง coupons | 20 | 1 | 1 |
| `08_coupon_producer_consumer2.py` | สร้าง coupons | 20 | 2 | 2 |

---

## 13. เปรียบเทียบวิธีปิด Worker

### 13.1 Cancellation — ใช้ในไฟล์ 05

```python
task.cancel()
```

ข้อดี:

- หยุด Task ที่กำลังรอได้ทันที
- เหมาะกับ cleanup หรือ shutdown จากภายนอก

ข้อควรระวัง:

- cancellation เป็นคำขอ ไม่ควรสมมติว่า cleanup เสร็จทันที
- โดยทั่วไปควร await Task หลัง cancel
- ถ้า cancel ระหว่างประมวลผล ต้องออกแบบให้ state ไม่ค้าง

### 13.2 Sentinel — ใช้ในไฟล์ 06–08

```python
await queue.put(None)
```

ข้อดี:

- เป็น cooperative shutdown ที่อ่านง่าย
- Consumer ปิดตัวผ่าน flow ปกติ
- Consumer สามารถ cleanup ก่อน break ได้

ข้อควรระวัง:

- ต้องส่งหลังงานจริงถูกจัดการตาม protocol
- ต้องส่งหนึ่ง sentinel ต่อ Consumer ที่ต้องหยุด
- Sentinel ที่ put เข้าคิวควรได้รับ `task_done()` เช่น item อื่น

---

## 14. ลำดับ Lifecycle ที่ปลอดภัย

รูปแบบของไฟล์ 06–08:

```python
# 1) สร้าง tasks ให้เริ่มพร้อมกัน
producer_task = asyncio.create_task(producer(...))
consumer_tasks = [...]

# 2) รอให้ Producer ผลิตงานจริงครบ
await producer_task

# 3) รอให้งานจริงทุกชิ้นได้รับ task_done()
await queue.join()

# 4) ส่งสัญญาณหยุดตามจำนวน Consumer
for _ in consumer_tasks:
    await queue.put(None)

# 5) รอ Consumer ปิดตัว
await asyncio.gather(*consumer_tasks)
```

เหตุผลที่ `join()` อยู่ก่อน sentinel ในตัวอย่างชุดนี้คือ ต้องการยืนยันว่างานจริงหมดก่อนสั่ง Consumer หยุด

> ถ้าออกแบบอีกแบบโดย put sentinel ก่อน `join()` ก็ทำได้ แต่ Consumer ต้อง `task_done()` ให้ sentinel ทุกตัว และต้องมั่นใจว่า FIFO/protocol ทำให้ sentinel อยู่หลังงานจริงทั้งหมด

---

## 15. `task_done()` สำหรับ Sentinel — จุดที่มักพลาด

ในไฟล์ 06–08 มี pattern:

```python
item = await queue.get()
if item is None:
    queue.task_done()
    break
```

ทำไมต้องเรียก:

1. `queue.put(None)` เพิ่ม unfinished-task count
2. `queue.get()` เอา `None` ออกจากคิว แต่ไม่ลด count
3. `queue.task_done()` จึงเป็น acknowledgement ของ item นั้น

กฎที่แม่นกว่า “เรียกเฉพาะงานจริง” คือ:

```text
ทุกครั้งที่ get สำเร็จหนึ่งครั้ง
ต้องมี task_done หนึ่งครั้งเมื่อจัดการ item นั้นเสร็จ
```

โครงสร้างที่ช่วยป้องกันการลืมในระบบที่มี exception:

```python
item = await queue.get()
try:
    if item is None:
        break
    await process(item)
finally:
    queue.task_done()
```

นี่เป็น pattern ต่อเพื่อศึกษา ไม่ใช่การแก้ไฟล์ปัจจุบัน

---

## 16. Expected behavior และเวลารวมโดยสรุป

เวลาจริงขึ้นกับ scheduler และ overhead ตารางนี้ใช้ค่าจากโค้ดปัจจุบัน:

| ไฟล์ | พฤติกรรมหลัก | เวลาประมาณ |
|---|---|---:|
| 01 | Sync 2+3 แล้ว Async max(2,3) | ~8 วินาทีทั้งไฟล์; แยกเป็น ~5 และ ~3 |
| 02 | Producer 3 items, Consumer ชิ้นละ 1s | ~3 วินาที |
| 03 | Consumer รอ Producer 2s | ~2 วินาที |
| 04 | 5 tasks, slow Consumer 2s, รอเริ่ม 1s | ~11 วินาที |
| 05 | 5 jobs / 2 workers, งานละ 1s | ~3 วินาที |
| 06 | 3 pages, 6 downloads, overlap | ~3–4 วินาที |
| 07 | 20 coupons, 1 consumer | ~1 วินาทีบวก overhead |
| 08 | 20 coupons, 2 consumers | ~0.4–0.6 วินาทีโดยทั่วไป |

สิ่งสำคัญกว่าทศนิยมของเวลาคือ order และ lifecycle:

- ทุกโปรแกรมต้องจบ ไม่ค้าง
- 06 ต้องดาวน์โหลด 6 URL
- 07 ต้องได้ 20 coupons ใน Consumer เดียว
- 08 ผลรวมสอง Consumer ต้องได้ 20 coupons แบบไม่ซ้ำและไม่หาย

---

## 17. วิธีรัน

เปิด Terminal ที่ repo root แล้วรันทีละไฟล์:

```bash
python Week8/01_synchronous_vs_asynchronous.py
python Week8/02_basic_asyncio_queue.py
python Week8/03_put_and_get_mechanism.py
python Week8/04_bounded_queue_backpressure.py
python Week8/05_task_completion_and_join.py
python Week8/06_scraper_downloader.py
python Week8/07_coupon_producer_consumer.py
python Week8/08_coupon_producer_consumer2.py
```

ไฟล์ทั้งหมดใช้ Python standard library จึงไม่ต้องติดตั้ง package เพิ่ม

ตรวจ syntax โดยไม่แก้ source:

```bash
python -m py_compile Week8/01_synchronous_vs_asynchronous.py
python -m py_compile Week8/02_basic_asyncio_queue.py
python -m py_compile Week8/03_put_and_get_mechanism.py
python -m py_compile Week8/04_bounded_queue_backpressure.py
python -m py_compile Week8/05_task_completion_and_join.py
python -m py_compile Week8/06_scraper_downloader.py
python -m py_compile Week8/07_coupon_producer_consumer.py
python -m py_compile Week8/08_coupon_producer_consumer2.py
```

> `py_compile` อาจสร้าง `Week8/__pycache__/` จึงควรลบ artifact นี้ก่อน commit ถ้า repository ไม่ได้ต้องการเก็บ

---

## 18. Pitfalls และวิธีคิดเวลา Debug

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ |
|---|---|---|
| `join()` ไม่จบ | จำนวน `task_done()` น้อยกว่า `put()` | นับ put/get/task_done ทุก path รวม sentinel |
| `ValueError: task_done() called too many times` | เรียก `task_done()` เกิน | ต้องหนึ่งครั้งต่อ item ที่ get |
| Consumer รอไม่จบ | ไม่มี Producer ส่ง item/sentinel เพิ่ม | ตรวจ lifecycle และจำนวน sentinels |
| Consumer บางตัวไม่หยุด | sentinels น้อยกว่าจำนวน Consumer | ส่ง N sentinel สำหรับ N Consumer |
| งานหาย | ส่ง sentinel เร็วเกินไป หรือ Consumer หยุดก่อนงานจริงหมด | await producer และจัดลำดับ shutdown |
| Producer ดูเหมือนค้างที่ `put()` | bounded queue เต็ม | นี่อาจเป็น backpressure ที่ตั้งใจไว้ |
| `empty()` แล้วผลไม่ตรงที่คาด | สถานะเปลี่ยนหลังตรวจ | อย่าใช้ `empty()` เป็น shutdown protocol |
| ลำดับการแบ่งงานสอง Consumer เปลี่ยน | scheduling ไม่ deterministic | ตรวจผลรวม/ความครบ ไม่ยึด 10/10 |
| 02 เปรียบเทียบ Order #1 ไม่ตรง | item แรกมี leading space | ดู `repr(item)` เพื่อเห็น whitespace |
| 02 ค้างหลังแก้รายการ | stop condition ผูกกับ `"Order #3"` | ใช้ sentinel หรือ protocol ที่แยกจาก data |
| Worker ถูก cancel แต่ cleanup ไม่ชัด | cancel แล้วไม่ await | gather cancelled tasks ด้วย `return_exceptions=True` |

### Checklist เมื่อโปรแกรมค้าง

1. มี Task ใดกำลังรอ `queue.get()` หรือไม่
2. จะมี Producer put item เพิ่มจริงหรือไม่
3. ส่ง sentinel ครบตามจำนวน Consumer หรือยัง
4. มี `join()` ที่รอ `task_done()` ซึ่งลืมเรียกหรือไม่
5. exception ทำให้ path ก่อน `task_done()` หลุดออกหรือไม่
6. bounded queue เต็มและไม่มี Consumer ทำงานอยู่หรือไม่
7. ใช้ `while not queue.empty()` ในระบบ concurrent หรือไม่

---

## 19. ตารางเปรียบเทียบแนวคิดในแต่ละไฟล์

| ไฟล์ | แนวคิดหลัก | คำสั่งที่ต้องจำ |
|---|---|---|
| 01 | Blocking vs non-blocking concurrency | `time.sleep`, `asyncio.sleep`, `gather` |
| 02 | Queue FIFO และ Producer–Consumer | `put`, `get` |
| 03 | `get()` รอคิวว่างแบบ async | `await queue.get()` |
| 04 | Bounded queue และ backpressure | `Queue(maxsize=2)`, `qsize` |
| 05 | ติดตามงานจนเสร็จและ cancel workers | `task_done`, `join`, `cancel` |
| 06 | Pipeline, 6 URLs, sentinel | `create_task`, `join`, `None` |
| 07 | 20 coupons, Consumer เดียว | FIFO, one sentinel |
| 08 | Consumer 2 ตัวและ shutdown ครบ | two sentinels, `gather(*consumers)` |

---

## 20. แบบฝึกหัด

### Exercise 1 — ทำนายเวลา

ถ้าในไฟล์ 01 เปลี่ยน A เป็น 4 วินาที และ B เป็น 6 วินาที:

1. Sync ใช้เวลาประมาณเท่าไร
2. Async ด้วย `gather()` ใช้เวลาประมาณเท่าไร
3. ถ้ารัน Sync แล้ว Async ในไฟล์เดียว เวลารวมเท่าไร

<details>
<summary>เฉลย</summary>

1. `4 + 6 = 10` วินาที
2. `max(4, 6) = 6` วินาที
3. ประมาณ `10 + 6 = 16` วินาที

</details>

### Exercise 2 — FIFO

Producer put ตามลำดับ:

```text
B, A, C
```

Consumer เดียวจะ get ลำดับใด

<details>
<summary>เฉลย</summary>

`B, A, C` เพราะ FIFO รักษาลำดับเข้า ไม่ได้ sort ตามตัวอักษร

</details>

### Exercise 3 — `get()` จากคิวว่าง

อธิบายว่าทำไม Consumer ในไฟล์ 03 ไม่ทำให้ Producer หยุดไปด้วยเมื่อเรียก `await queue.get()`

<details>
<summary>เฉลย</summary>

เพราะ `await` พัก coroutine ของ Consumer และคืน control ให้ event loop จึงสลับไปทำ Producer ได้ เมื่อ Producer put item แล้ว Consumer จึงถูกปลุก

</details>

### Exercise 4 — Backpressure

Queue มี `maxsize=2` และมี `[A, B]` อยู่แล้ว Producer เรียก `await queue.put(C)` จะเกิดอะไรขึ้น

<details>
<summary>เฉลย</summary>

Producer รอแบบ async จน Consumer get item ออกอย่างน้อยหนึ่งชิ้น เมื่อมีที่ว่างจึง put C สำเร็จ

</details>

### Exercise 5 — นับ unfinished tasks

สมมติทำตามลำดับ:

```text
put(A), put(B), get(A), task_done()
```

unfinished-task count เหลือเท่าไร และ `join()` ผ่านหรือไม่

<details>
<summary>เฉลย</summary>

เหลือ 1 สำหรับ B ดังนั้น `join()` ยังไม่ผ่านจน B ถูก get และ task_done

</details>

### Exercise 6 — Sentinel

มี Consumer 4 ตัวที่วน `while True` และหยุดเมื่อได้ `None` ต้อง put `None` อย่างน้อยกี่ครั้ง

<details>
<summary>เฉลย</summary>

4 ครั้ง หนึ่ง sentinel ต่อ Consumer

</details>

### Exercise 7 — ตรวจผล Multi-Consumer

ผลหนึ่งรอบเป็น:

```text
Consumer_01 = 12 coupons
Consumer_02 = 8 coupons
```

ถือว่าผิดหรือไม่

<details>
<summary>เฉลย</summary>

ยังสรุปไม่ได้จากจำนวนแบ่ง 12/8 เพราะ split ไม่จำเป็นต้องเท่ากัน ต้องตรวจว่าผลรวมเป็น 20 และ coupon 01–20 ครบ ไม่ซ้ำ ไม่หาย

</details>

### Exercise 8 — หา bug จาก `while not queue.empty()`

อธิบาย race ที่เป็นไปได้เมื่อมี Consumer 2 ตัว:

```python
while not queue.empty():
    item = await queue.get()
```

<details>
<summary>เฉลย</summary>

Consumer ทั้งคู่เห็นว่า Queue ไม่ว่าง แต่ตัวแรก get item สุดท้ายไปก่อน ตัวที่สองจึงกลับมา `get()` ตอนคิวว่างและอาจรอตลอดไปหากไม่มี item ใหม่

</details>

### Exercise 9 — ออกแบบ shutdown

เขียนลำดับเป็นคำพูดสำหรับ Producer 1 ตัว, Consumer 3 ตัว และงาน 100 ชิ้น

<details>
<summary>แนวคำตอบ</summary>

สร้าง Producer และ Consumer ทั้งสาม, รอ Producer ผลิตครบ, รอ `queue.join()` ให้งานจริงครบ 100 ชิ้น, put `None` 3 ครั้ง, แล้ว gather Consumer ทั้งสาม

</details>

### Exercise 10 — ปรับไฟล์ 02 บนกระดาษ

โดยไม่แก้ source จริง ลองร่างแนวคิดว่าจะเลิกใช้ `if item == "Order #3"` อย่างไร

<details>
<summary>แนวคำตอบ</summary>

ให้ Producer put Order จริงครบแล้ว put `None`; Consumer ถ้า get `None` ให้หยุด มิฉะนั้นประมวลผล Order ตามปกติ และถ้าใช้ `join()` ต้อง task_done ทั้ง Order และ sentinel ตาม protocol

</details>

---

## 21. คำถามแนวสอบพร้อมคำตอบสั้น

### 21.1 `asyncio.Queue` เป็น FIFO หรือไม่

เป็น โดย item ที่ put ก่อนจะอยู่หน้าคิวและถูก get ก่อน ภายใต้ Queue เดียว

### 21.2 ถ้า Queue ว่าง `await queue.get()` ทำอะไร

พัก coroutine ผู้เรียกไว้จนมี item โดยไม่ block event loop

### 21.3 ถ้า bounded queue เต็ม `await queue.put()` ทำอะไร

พัก Producer ไว้จน Consumer สร้างพื้นที่ว่าง นี่คือ backpressure

### 21.4 `queue.empty()` ใช้ตัดสินว่าระบบจบได้แน่นอนหรือไม่

ไม่แน่นอน เพราะเป็น snapshot และสถานะเปลี่ยนได้จาก Task อื่น ควรใช้ lifecycle protocol เช่น `join()` และ sentinel

### 21.5 `get()` ทำให้ `join()` ผ่านหรือไม่

ไม่ `get()` แค่นำ item ออกจากคิว ต้องเรียก `task_done()` หลังจัดการเสร็จจึงลด unfinished-task count

### 21.6 `task_done()` ต้องเรียกกี่ครั้ง

หนึ่งครั้งต่อ item ที่ get สำเร็จหนึ่งครั้ง รวม sentinel ที่ put เข้าคิว ถ้า protocol ใช้ accounting นี้

### 21.7 `join()` รออะไร

รอจนทุก item ที่ put เข้า Queue ได้รับ `task_done()` ครบ

### 21.8 `join()` หยุด Consumer ที่วนตลอดไปหรือไม่

ไม่ ต้อง cancel Task หรือส่ง sentinel ให้ Consumer หยุดเอง

### 21.9 ทำไมไฟล์ 01 แบบ Sync ใช้ 5 วินาที

เพราะ A 2 วินาทีและ B 3 วินาทีทำเรียงกัน: `2 + 3 = 5`

### 21.10 ทำไม Async ใช้ประมาณ 3 วินาที

เพราะ A และ B overlap กัน เวลารวมขึ้นกับงานช้าที่สุด: `max(2, 3) = 3`

### 21.11 ไฟล์ 06 มีรูปกี่รูป

3 pages × 2 URLs ต่อ page = 6 รูป

### 21.12 ไฟล์ 07 Consumer ได้กี่ coupons

`Consumer_01` ได้ครบ 20 ใบ ตั้งแต่ `COUPON-01` ถึง `COUPON-20`

### 21.13 ไฟล์ 08 ต้องแบ่ง 10/10 เสมอหรือไม่

ไม่ scheduling เปลี่ยนได้ ต้องตรวจผลรวม 20 และความครบแบบไม่ซ้ำไม่หาย

### 21.14 ทำไมไฟล์ 08 ต้องส่ง `None` สองครั้ง

เพราะมี Consumer 2 ตัว และ sentinel หนึ่งตัวหยุดได้เพียง Consumer ที่ get มันไปหนึ่งตัว

### 21.15 cancellation กับ sentinel ต่างกันอย่างไร

Cancellation เป็นคำขอยกเลิก Task จากภายนอก ส่วน sentinel เป็นข้อมูลควบคุมที่ Consumer รับและตัดสินใจปิดตัวผ่าน flow ปกติ

---

## 22. Exam Recap — สิ่งที่ต้องพูดได้ก่อนสอบ

ลองตอบโดยไม่เปิดคู่มือ:

- [ ] อธิบาย blocking และ non-blocking wait ได้
- [ ] คำนวณ Sync 2+3 = 5 วินาที และ Async max(2,3) ≈ 3 วินาทีได้
- [ ] อธิบาย Producer, Queue และ Consumer จาก architecture ได้
- [ ] บอกได้ว่า FIFO หมายถึงอะไร
- [ ] อธิบายว่า `get()` ทำอย่างไรเมื่อคิวว่าง
- [ ] อธิบายว่า `put()` ทำอย่างไรเมื่อ bounded queue เต็ม
- [ ] บอกได้ว่า `maxsize=2` สร้าง backpressure อย่างไร
- [ ] แยก `queue.empty()` ออกจาก `queue.join()` ได้
- [ ] อธิบาย unfinished-task counter ได้
- [ ] จำกฎหนึ่ง `task_done()` ต่อหนึ่ง `get()` ได้
- [ ] อธิบายว่าทำไม `join()` อย่างเดียวไม่หยุด worker loop
- [ ] เปรียบเทียบ cancel กับ sentinel ได้
- [ ] จำว่า N Consumer ต้องใช้ N sentinel ได้
- [ ] บอกได้ว่าไฟล์ 06 ใช้ 3 pages และสร้าง 6 URLs
- [ ] บอกได้ว่าไฟล์ 07 มี Consumer เดียวและ 20 coupons
- [ ] บอกได้ว่าไฟล์ 08 มี 2 workers และ `None` 2 ตัว
- [ ] รู้ว่า multi-consumer split ไม่ deterministic แต่ผลรวมต้องครบ 20
- [ ] เห็นปัญหา leading space และ hard-coded stop condition ในไฟล์ 02
- [ ] เห็น race ของ `while not queue.empty()` ในไฟล์ 04
- [ ] อธิบายว่าทำไม sentinel ก็ควรมี `task_done()` ได้

---

## 23. Cheat Sheet ก่อนสอบ

```text
asyncio.Queue()
    Queue สำหรับสื่อสารระหว่าง coroutine บน event loop

asyncio.Queue(maxsize=2)
    เก็บได้สูงสุด 2 item; put รอเมื่อเต็ม

await queue.put(item)
    ใส่ item; รอแบบ async ถ้า bounded queue เต็ม

item = await queue.get()
    ดึง item แบบ FIFO; รอแบบ async ถ้าคิวว่าง

queue.qsize()
    จำนวน item ที่รออยู่ ณ ตอนตรวจ

queue.empty()
    snapshot ว่าตอนนี้ว่างหรือไม่ ไม่ใช่ shutdown guarantee

queue.task_done()
    acknowledge ว่า item จาก get หนึ่งชิ้นทำเสร็จแล้ว

await queue.join()
    รอจน put ทุกชิ้นได้รับ task_done ครบ

asyncio.create_task(coro)
    schedule coroutine และคืน Task object

await asyncio.gather(*tasks)
    รอ Task ทั้งหมด

task.cancel()
    ส่งคำขอยกเลิก Task

None sentinel
    ค่าพิเศษสั่ง Consumer ให้ break

N consumers
    ส่ง N sentinels เพื่อหยุดครบทุกตัว
```

สูตรจำ:

```text
FIFO                 = เข้าก่อน ออกก่อน
Sync time            = ผลรวมเวลา
Concurrent async time = ใกล้เวลางานที่ช้าที่สุด
Queue full           = put รอ
Queue empty          = get รอ
put/get accounting   = 1 get ที่จัดการเสร็จ : 1 task_done
งานจริงครบ           = join
worker ต้องหยุด      = cancel หรือ sentinel
```

---

## 24. สรุปสุดท้าย

หัวใจของแต่ละไฟล์:

| ไฟล์ | จำสั้น ๆ |
|---|---|
| `01_synchronous_vs_asynchronous.py` | Sync ~5s; Async ~3s; ทั้งไฟล์ ~8s |
| `02_basic_asyncio_queue.py` | FIFO พื้นฐาน พร้อม caveat เรื่องช่องว่างและ stop condition |
| `03_put_and_get_mechanism.py` | `get()` รอคิวว่างโดยไม่ block event loop |
| `04_bounded_queue_backpressure.py` | `maxsize=2` ทำให้ Producer ชะลอ; `empty()` เป็นเพียง snapshot |
| `05_task_completion_and_join.py` | `task_done()` ปลด `join()` แล้ว cancel Worker |
| `06_scraper_downloader.py` | 3 pages → 6 URLs → Downloader เดียว → `None` หนึ่งตัว |
| `07_coupon_producer_consumer.py` | 20 coupons → Consumer เดียว → `None` หนึ่งตัว |
| `08_coupon_producer_consumer2.py` | 20 coupons → Consumer 2 ตัว → `None` สองตัว |

ประโยคเดียวที่สรุป Week 8:

> Producer ส่งงานเข้า FIFO Queue, Consumer รอและดึงงานไปทำ, bounded queue สร้าง backpressure, `task_done()`/`join()` รับรองว่างานครบ และ cancel/sentinel ทำให้ worker ปิดอย่างมี lifecycle ที่ชัดเจน
