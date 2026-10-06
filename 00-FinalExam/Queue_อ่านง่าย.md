# Queue — สรุปเนื้อหาแบบอ่านง่าย

> เรียบเรียงจากเอกสาร **Queue** จำนวน 69 หน้า โดยคงแนวคิด คำศัพท์ และตัวอย่างหลักตามเอกสารต้นฉบับ

---

## สารบัญ

1. [พื้นฐาน Queue และ FIFO](#1-พื้นฐาน-queue-และ-fifo)
2. [โครงสร้างภายใน Queue](#2-โครงสร้างภายใน-queue)
3. [Queue ช่วยแยกระบบอย่างไร](#3-queue-ช่วยแยกระบบอย่างไร)
4. [Producer–Consumer](#4-producerconsumer)
5. [Blocking Queue vs Async Queue](#5-blocking-queue-vs-async-queue)
6. [เปรียบเทียบ Queue กับโครงสร้างอื่น](#6-เปรียบเทียบ-queue-กับโครงสร้างอื่น)
7. [asyncio.Queue](#7-asyncioqueue)
8. [put() และ get()](#8-put-และ-get)
9. [Bounded Queue และ Backpressure](#9-bounded-queue-และ-backpressure)
10. [task_done() และ join()](#10-task_done-และ-join)
11. [Web Scraper & Image Download](#11-web-scraper--image-download)
12. [Coupon Producer–Consumer](#12-coupon-producerconsumer)
13. [Multi-Consumer Coupon](#13-multi-consumer-coupon)
14. [สรุปจำก่อนสอบ](#14-สรุปจำก่อนสอบ)

---

# 1. พื้นฐาน Queue และ FIFO

## Queue คืออะไร?

Queue ถูกสร้างขึ้นเพื่อจัดการ **ลำดับการเข้ามาของข้อมูล (order of arrival)** ในระบบดิจิทัล โดยเลียนแบบแถวรอในชีวิตจริง

### FIFO — First-In, First-Out

หลักสำคัญของ Queue คือ

> **เข้าก่อน → ออกก่อน**

ข้อมูลที่ถูกเพิ่มเข้ามาก่อน จะถูกนำไปประมวลผลก่อน

**ตัวอย่าง**
- แถวจ่ายเงินในซูเปอร์มาร์เก็ต
- สายการผลิตในโรงงาน
- แถวรอลูกค้าใน Call Center

📌 **หน้า 3:** หลักการ FIFO และตัวอย่างการใช้งาน

---

# 2. โครงสร้างภายใน Queue

## Head และ Tail

| ส่วน | หน้าที่ |
|---|---|
| **Head** | จุดที่นำข้อมูลออก / Dequeue |
| **Tail** | จุดที่เพิ่มข้อมูลเข้า / Enqueue |

### Enqueue

เพิ่มข้อมูลใหม่เข้า Queue ที่ **Tail**

### Dequeue

นำข้อมูลเก่าสุดออกจาก Queue ที่ **Head**

### Time Complexity

Queue มีแนวคิดให้

```text
Enqueue = O(1)
Dequeue = O(1)
```

ไม่ว่าจะมีข้อมูลประมาณ 10 รายการ หรือ 1,000,000 รายการ เวลาในการทำงานของ operation ยังคงเป็นค่าคงที่ตามแนวคิดของ Queue ในเอกสาร

📌 **หน้า 4:** Head, Tail, Enqueue, Dequeue และ O(1)

---

## 2.1 Circular Buffer

Circular Buffer เป็นการจองพื้นที่หน่วยความจำแบบมีขนาดคงที่ แล้วให้ตำแหน่ง Head/Tail หมุนวนกลับมาใช้พื้นที่เดิม

แนวคิดง่าย ๆ:

```text
[0] [1] [2] [3] [4] [5]
 ↑                   ↑
Head                Tail
```

เมื่อข้อมูลที่ Head ถูกนำออก ช่องนั้นจะกลับมาใช้สำหรับข้อมูลใหม่ได้ โดยไม่ต้องเลื่อนข้อมูลทั้งหมด

### สิ่งสำคัญ

- Fixed-size allocation
- มี Head Pointer
- มี Tail Pointer
- ใช้ Modulo `%` เพื่อวนกลับต้น Buffer

ตัวอย่างแนวคิด:

```text
(Tail + 1) % N
```

📌 **หน้า 5–6:** Circular Buffer และภาพตัวอย่าง Capacity = 6

---

## 2.2 Linked List

Linked List เป็นการจองหน่วยความจำแบบ Dynamic

แต่ละ Node มี:

```text
Data + Next Pointer
```

`Next Pointer` จะชี้ไปยัง Node ถัดไป

### จุดเด่น

- เพิ่ม Node ตามจำนวนข้อมูลที่เข้ามา
- ขยายได้ตามต้องการจนกว่า RAM จะหมด
- เหมาะกับ Queue ที่ต้องการขนาด Dynamic

### ข้อควรระวัง

การสร้างและลบ Node บ่อย ๆ ทำให้เกิด Allocation/Deallocation overhead

📌 **หน้า 7:** Linked List และ Node Structure

---

# 3. Queue ช่วยแยกระบบอย่างไร

## System Decoupling

ถ้า System A เรียก System B โดยตรง:

```text
System A ───────► System B
```

ถ้า B ช้าหรือหยุดทำงาน A ก็อาจได้รับผลกระทบทันที

Queue ทำหน้าที่เป็น **Middleman**

```text
Producer ──► Queue ──► Consumer
```

Producer และ Consumer ไม่จำเป็นต้องรู้รายละเอียดภายในของกันและกัน

Queue จึงเป็นจุดกลางในการส่งต่องาน

📌 **หน้า 9:** Queue as a Middleman

---

# 4. Queue เป็น Buffer

Queue สามารถทำหน้าที่เป็น Buffer เพื่อรับมือกับ **Traffic Spike**

ตัวอย่าง:

```text
ช่วงปกติ
Producer → → → Queue → Consumer

ช่วงข้อมูลพุ่งสูง
Producer → → → → → → Queue → Consumer
                   ↑
              Buffer รองรับ
```

ถ้ามีข้อมูลเข้ามาเร็วมาก Queue จะช่วยเก็บงานที่เข้ามาก่อน เพื่อไม่ให้ Backend ถูกโจมตีด้วยงานจำนวนมากพร้อมกัน

📌 **หน้า 10:** Buffer Mechanism for Traffic Spikes

---

## Load Leveling

Queue ช่วยเปลี่ยน

```text
Traffic ไม่สม่ำเสมอ
████████████████
██
████████████
```

ให้กลายเป็นการประมวลผลที่สม่ำเสมอมากขึ้น

```text
Consumer
████ ████ ████ ████
```

### Pull-Based Pattern

Consumer เป็นฝ่าย **ดึงงานจาก Queue**

ไม่ใช่ Producer บังคับส่งงานให้ Consumer โดยตรง

```text
Producer → Queue ← Consumer
                    ↑
              ดึงตามความสามารถ
```

📌 **หน้า 11:** Load Leveling และ Pull-Based Pattern

---

# 5. Producer–Consumer

## Producer

ผู้สร้างงาน เช่น

- Checkout requests
- Web crawler
- IoT sensor logs

## Consumer

ผู้ประมวลผล/ทำงาน เช่น

- Payment gateway
- Web page downloader
- Analytics engine

## Queue

ทำหน้าที่เป็น **Neutral Handoff Boundary**

```text
Producer
   │
   ▼
 Queue
   │
   ▼
Consumer
```

📌 **หน้า 13:** Producer–Consumer Pattern

---

## ปัญหา Producer เร็วกว่า Consumer

ตัวอย่าง:

```text
Producer = 1,000 tasks/sec
Consumer =   100 tasks/sec
```

ถ้าไม่มี Queue งานจะไหลเข้าหา Consumer โดยตรงและอาจทำให้ระบบรับไม่ไหว

Queue ช่วยรับงานส่วนเกินไว้ก่อน

📌 **หน้า 15–16:** Handling Speed Mismatches

---

# 6. Multiple Consumers

ถ้างานเยอะ สามารถเพิ่ม Consumer ได้หลายตัว

```text
                 ┌─► Consumer 1
Producer → Queue ├─► Consumer 2
                 └─► Consumer 3
```

เรียกว่า **Competing Consumers Pattern**

Consumer หลายตัวช่วยแบ่งงานจาก Queue และประมวลผลแบบขนาน

ข้อดี:

- เพิ่ม Throughput
- ลดเวลาประมวลผล
- รองรับงานจำนวนมากขึ้น

📌 **หน้า 17:** Horizontal Scaling via Multiple Consumers

---

# 7. Blocking Queue vs Async Queue

## 7.1 Blocking Queue

เมื่อ Queue ว่าง Consumer จะรอ/Block

```text
Queue ว่าง
   ↓
Consumer รอ
   ↓
ข้อมูลมา
   ↓
Consumer ทำงาน
```

ข้อดี:
- เข้าใจง่าย
- Thread-safe

ข้อเสีย:
- Thread ถูกใช้เพื่อรอ
- ถ้ามี Thread จำนวนมากจะสิ้นเปลือง Resource

📌 **หน้า 18–20:** Blocking Queue และกรณี Queue เต็ม

---

## 7.2 Non-Blocking / Event-Driven Queue

แนวคิดคือ

> **Yield and Switch**

ถ้า Queue ว่าง Consumer จะไม่ทำให้ทั้งโปรแกรมหยุด

แต่จะ:

```text
Consumer รอ Queue
      ↓
Yield control
      ↓
Event Loop ไปทำ Task อื่น
      ↓
มีข้อมูลเข้า Queue
      ↓
กลับมาทำ Consumer
```

จึงใช้ Resource ได้มีประสิทธิภาพกว่าในระบบ Async

📌 **หน้า 21:** Non-Blocking / Event-Driven Queue

---

# 8. asyncio.Queue

`asyncio.Queue` คือ Queue ที่ออกแบบมาสำหรับ Coroutine ที่ทำงานบน Event Loop

หน้าที่หลัก:

```text
Producer Coroutine
       │
       ▼
asyncio.Queue
       │
       ▼
Consumer Coroutine
```

### คุณสมบัติสำคัญ

1. เป็น Async Communication Bridge
2. ใช้ส่ง Message/Task ระหว่าง Coroutine
3. ทำงานร่วมกับ Event Loop
4. รองรับ Concurrent Reads/Writes ของ Coroutine
5. ไม่จำเป็นต้องสร้าง Lock เองสำหรับการจัดการ Queue
6. รักษา FIFO

📌 **หน้า 36:** Understanding asyncio.Queue

---

# 9. put() และ get()

## `queue.put()`

ใช้เพิ่มข้อมูลเข้า Queue

```python
await queue.put(item)
```

ถ้ามีพื้นที่:

```text
put() → สำเร็จทันที
```

ถ้า Queue เต็ม:

```text
put()
 ↓
await
 ↓
รอจนกว่าจะมีพื้นที่
```

---

## `queue.get()`

ใช้ดึงข้อมูลจาก Queue

```python
item = await queue.get()
```

ถ้ามีข้อมูล:

```text
get() → ได้ข้อมูลทันที
```

ถ้า Queue ว่าง:

```text
get()
 ↓
await
 ↓
Coroutine หยุดรอ
 ↓
Event Loop ไปทำงานอื่น
```

**สำคัญ:** การรอแบบนี้ไม่ใช่การ Freeze ทั้ง Event Loop

📌 **หน้า 39–41:** Put/Get และ Empty Queue

---

# 10. Bounded Queue และ Backpressure

## `maxsize`

สามารถกำหนดขนาด Queue ได้

```python
queue = asyncio.Queue(maxsize=2)
```

หมายความว่า Queue รับข้อมูลได้สูงสุด 2 รายการก่อนที่ Producer จะต้องรอ

---

## เมื่อ Queue เต็ม

```text
Producer
   │
   ▼
[ A ][ B ]  ← เต็ม
   │
   X
   │
   ▼
await queue.put()
```

Producer จะถูกพักไว้จนกว่า Consumer จะนำข้อมูลออก

### Backpressure

Backpressure คือกลไกที่ทำให้ Producer ช้าลงโดยอัตโนมัติเมื่อ Consumer ประมวลผลไม่ทัน

```text
Producer เร็ว
      ↓
Queue เต็ม
      ↓
await put()
      ↓
Producer ช้าลง
      ↓
Consumer เคลียร์ Queue
```

ช่วยป้องกัน **Memory Exhaustion**

📌 **หน้า 42–44:** Bounded Queue และ Backpressure

---

# 11. task_done() และ join()

สองคำสั่งนี้สำคัญมากสำหรับการติดตามว่า Queue ทำงานครบหรือยัง

## `queue.task_done()`

Consumer ต้องเรียกหลังจากประมวลผล Item ที่ `get()` มาเสร็จแล้ว

```python
item = await queue.get()

# process item

queue.task_done()
```

หน้าที่คือแจ้ง Queue ว่า:

> งานชิ้นนี้เสร็จแล้ว

---

## `queue.join()`

ใช้รอจนกว่างานทั้งหมดที่ถูกใส่เข้า Queue จะถูกทำเสร็จและเรียก `task_done()` ครบ

```python
await queue.join()
```

แนวคิด:

```text
put()
 ↓
งานอยู่ใน Queue
 ↓
get()
 ↓
ประมวลผล
 ↓
task_done()
 ↓
งานเสร็จ
```

เมื่อทุกงานเสร็จ:

```text
queue.join() → ทำงานต่อ
```

จึงเหมาะกับ **Graceful Shutdown**

📌 **หน้า 45–47:** Task Completion และ Lifecycle Tracking

---

# 12. Web Scraper & Image Download

ตัวอย่างในเอกสารใช้:

```text
Producer = Link Scraper
Consumer = Image Downloader
Queue = asyncio.Queue
```

Producer สแกน:

```text
Page 1 → img1, img2
Page 2 → img1, img2
Page 3 → img1, img2
```

แล้วใส่ URL รูปลง Queue

```text
Producer
   ↓
Queue
   ↓
Downloader
```

---

## ลำดับการทำงาน

ทั้ง Producer และ Consumer เริ่มทำงานพร้อมกันด้วย:

```python
asyncio.create_task(...)
```

เมื่อ Producer ใส่รูปแรก:

```python
await queue.put(img_url)
```

Consumer ที่กำลังรอ:

```python
img_url = await queue.get()
```

ก็สามารถนำรูปแรกไปดาวน์โหลดทันที

**ไม่จำเป็นต้องรอ Producer สแกนครบทุกหน้า**

📌 **หน้า 58:** อธิบายการทำงานร่วมกันของ Producer และ Consumer

---

## หน้าที่ของ `await producer_task`

ใน `main()`:

```python
await producer_task
```

มีความหมายว่า:

> รอให้ Producer ผลิตงานครบก่อน จึงค่อยไป `queue.join()` หรือส่ง Sentinel เพื่อปิด Consumer

แต่ระหว่างที่ `main()` รออยู่ Event Loop ยังคงทำงานให้ทั้ง Producer และ Consumer ต่อไป

📌 **หน้า 58 และ 69:** กลไกการทำงานของ Event Loop

---

# 13. Coupon Producer–Consumer

เอกสารมีตัวอย่าง Coupon จำนวน **20 ใบ**

Producer:

```text
สร้าง Coupon 1
สร้าง Coupon 2
สร้าง Coupon 3
...
สร้าง Coupon 20
```

แล้วใส่ลง:

```python
asyncio.Queue()
```

Consumer ดึง Coupon ไปประมวลผล/เก็บสะสม

📌 **หน้า 59–62:** Coupon Producer–Consumer

---

## โครงสร้างหลัก

```python
async def producer(queue, total_coupons):
    for i in range(1, total_coupons + 1):
        coupon = f"COUPON-{i:02d}"
        await queue.put(coupon)
        await asyncio.sleep(...)
```

Consumer:

```python
async def consumer(queue, consumer_name):
    while True:
        coupon = await queue.get()

        if coupon is None:
            queue.task_done()
            break

        # process coupon

        queue.task_done()
```

ใน `main()`:

```python
queue = asyncio.Queue()

prod_task = asyncio.create_task(
    producer(queue, TOTAL_COUPONS)
)

cons_task = asyncio.create_task(
    consumer(queue, "Consumer_01")
)

await prod_task
await queue.join()

await queue.put(None)
await cons_task
```

---

# 14. Multi-Consumer Coupon

กรณีมี Consumer 2 ตัว:

```text
                  ┌─► Consumer_01
Producer → Queue ─┤
                  └─► Consumer_02
```

ทั้ง Producer และ Consumer 2 ตัวใช้ `asyncio.Queue` เดียวกัน

Queue ทำหน้าที่กระจายงานแบบ FIFO

📌 **หน้า 64:** Multi-Consumer Coupon

---

## ทำไม Consumer 2 ตัวถึงทำงานเร็วขึ้น?

Consumer ทั้งสองทำงานแบบ Concurrent บน Event Loop

```text
Queue
 │
 ├──► Consumer_01
 │
 └──► Consumer_02
```

เมื่อ Consumer ตัวหนึ่งทำงานเสร็จ ก็กลับมาดึงงานชิ้นถัดไป

จึงเพิ่มความเร็วในการประมวลผลโดยรวม

---

## `asyncio.sleep()` ไม่ได้ Block ทั้งโปรแกรม

เช่น:

```python
await asyncio.sleep(0.04)
```

ระหว่างที่ Consumer รอ:

```text
Consumer 1
   ↓
await sleep()
   ↓
Event Loop
   ↓
Consumer 2
```

Event Loop สามารถสลับไปทำ Coroutine อื่นได้

📌 **หน้า 64:** การทำงานของ Consumer หลายตัวบน Event Loop

---

## Sentinel Value: `None`

เมื่อ Consumer ต้องหยุด สามารถส่ง:

```python
None
```

เข้า Queue เพื่อเป็นสัญญาณหยุด

ถ้ามี Consumer 2 ตัว:

```python
for _ in range(2):
    await queue.put(None)
```

ต้องส่ง `None` **2 ครั้ง**

เพราะ Consumer แต่ละตัวต้องได้รับสัญญาณหยุดของตัวเอง

```text
None → Consumer_01 → STOP
None → Consumer_02 → STOP
```

ทำให้เกิด **Graceful Shutdown**

📌 **หน้า 64 และ 67:** Sentinel Value และ Multi-Consumer Shutdown

---

# 15. สรุปคำสั่งสำคัญ

| คำสั่ง | ความหมาย |
|---|---|
| `asyncio.Queue()` | สร้าง Async Queue |
| `queue.put(x)` | เพิ่มข้อมูลเข้า Queue |
| `queue.get()` | ดึงข้อมูลจาก Queue |
| `queue.task_done()` | แจ้งว่างานที่ get มาเสร็จแล้ว |
| `queue.join()` | รอจนงานทั้งหมดเสร็จ |
| `asyncio.create_task()` | สร้าง Task ให้ Event Loop ทำงาน |
| `await asyncio.sleep()` | รอแบบไม่ Block Event Loop |
| `maxsize` | จำกัดความจุ Queue |
| `None` | Sentinel สำหรับสั่ง Consumer หยุด |

---

# 16. จุดที่ควรจำก่อนสอบ ⭐

## ⭐ FIFO

```text
First In → First Out
```

เข้า 1 → 2 → 3

ออก:

```text
1 → 2 → 3
```

---

## ⭐ Queue

```text
Enqueue → Tail
Dequeue → Head
```

---

## ⭐ Producer–Consumer

```text
Producer → Queue → Consumer
```

Queue เป็นตัวกลาง ไม่ให้ Producer และ Consumer ผูกกันโดยตรง

---

## ⭐ Queue เป็น Buffer

ถ้า Producer เร็วกว่า Consumer:

```text
Producer เร็ว
     ↓
   Queue
     ↓
Consumer ช้า
```

Queue ช่วยรับงานที่มากระทันหัน

---

## ⭐ `asyncio.Queue`

```text
Coroutine → asyncio.Queue → Coroutine
```

ใช้กับ Async/Event Loop และรักษา FIFO

---

## ⭐ Queue ว่าง

```python
await queue.get()
```

ไม่ได้ทำให้ทั้งโปรแกรมหยุด

แต่ Coroutine นั้นจะรอ และ Event Loop ไปทำงานอื่น

---

## ⭐ Queue เต็ม

```python
await queue.put(item)
```

จะรอจนกว่าจะมีพื้นที่

นี่คือ **Backpressure**

---

## ⭐ `task_done()` + `join()`

จำเป็นต้องจับคู่กัน:

```text
get()
 ↓
process
 ↓
task_done()
```

และ:

```python
await queue.join()
```

ใช้รอจนงานทั้งหมดเสร็จ

---

## ⭐ Multi-Consumer

```text
Queue
 ├── Consumer 1
 ├── Consumer 2
 └── Consumer 3
```

ช่วยเพิ่ม Throughput

---

## ⭐ Sentinel

Consumer ต้องหยุด → ส่ง `None`

ถ้ามี Consumer 2 ตัว:

```text
None × 2
```

---

# 17. Flow รวมทั้งบท

```text
                  ┌──────────────────┐
                  │    Producer      │
                  │   สร้างงาน       │
                  └────────┬─────────┘
                           │
                         put()
                           │
                           ▼
                  ┌──────────────────┐
                  │      Queue       │
                  │      FIFO        │
                  │ Buffer / Decouple│
                  └────────┬─────────┘
                           │
                         get()
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │ Consumer 1  │          │ Consumer 2  │
       └─────────────┘          └─────────────┘
              │                         │
              └────────────┬────────────┘
                           ▼
                     task_done()
                           │
                           ▼
                     queue.join()
                           │
                           ▼
                  Graceful Shutdown
```

---

# 18. จำแบบสั้นที่สุด 🧠

> **Queue = ตัวกลางจัดลำดับงาน**

> **FIFO = เข้าก่อนออกก่อน**

> **Enqueue = เข้า Tail**

> **Dequeue = ออก Head**

> **Producer = สร้างงาน**

> **Consumer = ประมวลผลงาน**

> **asyncio.Queue = Queue สำหรับ Coroutine**

> **get() ตอน Queue ว่าง = await แล้ว Event Loop ไปทำงานอื่น**

> **put() ตอน Queue เต็ม = await → Backpressure**

> **task_done() = งานนี้เสร็จ**

> **join() = รอทุกงานเสร็จ**

> **Multiple Consumers = แบ่งงานเพื่อเพิ่ม Throughput**

> **None = Sentinel สำหรับหยุด Consumer**

---

## อ้างอิงจากเอกสาร

- หน้า 3–4: FIFO, Head/Tail, Enqueue/Dequeue fileciteturn5file0L7-L22
- หน้า 5–11: Circular Buffer, Linked List, Decoupling, Buffer และ Load Leveling fileciteturn5file0L24-L63
- หน้า 13–24: Producer–Consumer, Multiple Consumers, Blocking/Async Queue และ Bounded Queue fileciteturn5file0L68-L114
- หน้า 32–47: asyncio.Queue, `put()`, `get()`, `maxsize`, `task_done()` และ `join()` fileciteturn5file0L146-L211
- หน้า 48–69: Web Scraper, Coupon และ Multi-Consumer Coupon fileciteturn5file0L214-L294
