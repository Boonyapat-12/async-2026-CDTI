# Race Conditions & asyncio.Lock — สรุปเนื้อหาแบบอ่านง่าย

> เรียบเรียงจากเอกสาร **Understanding Race Conditions & asyncio.Lock** จำนวน 31 หน้า โดยยึดแนวคิด คำศัพท์ ตัวอย่าง และโจทย์ในเอกสารเป็นหลัก

---

## สารบัญ

1. [Asynchronous Programming](#1-asynchronous-programming)
2. [asyncio และ Event Loop](#2-asyncio-และ-event-loop)
3. [await และ Task Switching](#3-await-และ-task-switching)
4. [Shared State](#4-shared-state)
5. [Race Condition](#5-race-condition)
6. [ทำไม Single-Thread ก็เกิด Race Condition ได้](#6-ทำไม-single-thread-ก็เกิด-race-condition-ได้)
7. [Read–Modify–Write](#7-readmodifywrite)
8. [ตัวอย่าง Last Coupon](#8-ตัวอย่าง-last-coupon)
9. [Critical Section](#9-critical-section)
10. [asyncio.Lock](#10-asynciolock)
11. [Acquire และ Release](#11-acquire-และ-release)
12. [async with lock](#12-async-with-lock)
13. [เปรียบเทียบมี Lock กับไม่มี Lock](#13-เปรียบเทียบมี-lock-กับไม่มี-lock)
14. [Best Practices](#14-best-practices)
15. [Assignment: Team Coupon Hunting](#15-assignment-team-coupon-hunting)
16. [Dynamic Inventory](#16-dynamic-inventory)
17. [การทดลองที่ 1: Server ไม่มี Lock](#17-การทดลองที่-1-server-ไม่มี-lock)
18. [การทดลองที่ 2: Server มี Lock](#18-การทดลองที่-2-server-มี-lock)
19. [ไฟล์ที่ต้องส่ง](#19-ไฟล์ที่ต้องส่ง)
20. [สรุปจำก่อนสอบ](#20-สรุปจำก่อนสอบ)

---

# 1. Asynchronous Programming

Asynchronous Programming ช่วยให้โปรแกรมสามารถจัดการหลายงานแบบ **Concurrent** ได้ โดยไม่จำเป็นต้องรอให้งานหนึ่งเสร็จทั้งหมดก่อนจึงเริ่มงานถัดไป

แนวคิดหลัก:

```text
Task A ──► ทำงาน ──► รอ
                    │
                    ▼
                Task B ทำงาน
                    │
                    ▼
                Task A ทำต่อ
```

จุดสำคัญคือ **ไม่ได้หมายความว่า CPU หลาย Core กำลังรันโค้ดพร้อมกันจริง ๆ**

📌 **หน้า 3:** ความหมายของ Asynchronous Programming

---

# 2. asyncio และ Event Loop

Python `asyncio` ใช้แนวคิด

> **Single-Threaded Event Loop + Cooperative Multitasking**

หมายความว่าในโมเดลนี้ไม่ได้มีการรันโค้ดหลาย CPU Core พร้อมกันในเวลาเดียวกัน

แต่ Event Loop จะสลับงานระหว่าง Task ตามจุดที่ Task ยอมคืนการควบคุม

```text
             ┌──────────────┐
             │  Event Loop  │
             └──────┬───────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Task A              Task B
```

📌 **หน้า 4:** asyncio Model

---

# 3. await และ Task Switching

เมื่อ Async Function เจอ:

```python
await ...
```

Task สามารถหยุดการทำงานชั่วคราวและคืนการควบคุมให้ Event Loop

ตัวอย่างสถานการณ์ที่อาจเกิดขึ้น:

```python
await asyncio.sleep(...)
```

หรือการรอ Network I/O

ลำดับโดยย่อ:

```text
Task A
  │
  ├── ทำงาน
  │
  ├── await
  │
  ▼
Event Loop
  │
  ▼
Task B
  │
  └── ทำงาน
```

เมื่อ Task A พร้อมทำงานอีกครั้ง Event Loop สามารถกลับมาให้ Task A ทำต่อ

📌 **หน้า 5:** How Task Switching Works

---

# 4. Shared State

**Shared State** คือข้อมูลที่หลาย Concurrent Tasks สามารถเข้าถึงได้ ไม่ว่าจะเป็นการอ่านหรือเขียน

ตัวอย่าง:

```text
ตัวแปร
Dictionary
Database Record
```

ตัวอย่างระบบคูปอง:

```python
company_coupons
```

ถ้า Task หลายตัวเข้าถึง `company_coupons` เดียวกัน นั่นคือ Shared State

📌 **หน้า 6:** ความหมายของ Shared State

---

# 5. Race Condition

## Race Condition คืออะไร?

Race Condition เกิดขึ้นเมื่อ **ผลลัพธ์สุดท้ายขึ้นอยู่กับจังหวะหรือลำดับการทำงานของ Concurrent Tasks ที่เข้าถึง Shared Resource โดยไม่มีการประสานงานที่เหมาะสม**

พูดง่าย ๆ:

> **หลาย Task แย่งข้อมูลเดียวกัน แล้วจังหวะการสลับ Task ทำให้ผลลัพธ์ผิด**

📌 **หน้า 8:** Definition of Race Condition

---

## Shared Resource

คือข้อมูลกลางที่หลาย Task เข้าถึงร่วมกัน เช่น:

- คลังคูปอง
- ยอดเงินในบัญชี
- จำนวนสินค้าใน Stock

---

# 6. ทำไม Single-Thread ก็เกิด Race Condition ได้?

นี่เป็นจุดที่สำคัญมาก

> ❌ Single-Thread ไม่ได้แปลว่าไม่มี Race Condition

ใน `asyncio` Race Condition สามารถเกิดขึ้นได้เมื่อ Task ถูกหยุดที่ `await` **ระหว่างกระบวนการ Read → Modify → Write**

ตัวอย่าง:

```text
Task A
อ่านข้อมูล
   ↓
await
   ↓
Task B เข้ามาทำงาน
```

Task B อาจเข้ามาเปลี่ยนข้อมูลก่อนที่ Task A จะเขียนข้อมูลกลับ

📌 **หน้า 9:** Myth: Single-Threaded Means Race-Condition-Free

---

# 7. Read–Modify–Write

Race Condition มักเกิดกับ Operation แบบ:

```text
Read
 ↓
Modify
 ↓
Write
```

ตัวอย่าง:

```text
1. Read: อ่าน inventory = 1
2. await: หยุดรอ
3. Write: inventory -= 1
```

ปัญหาเกิดเมื่อมี Task อื่นเข้ามาแทรกระหว่างขั้นตอนเหล่านี้

📌 **หน้า 10:** Anatomy of a Vulnerable Operation

---

# 8. ตัวอย่าง Last Coupon

สมมติว่ามีคูปองเหลือเพียง:

```text
count = 1
```

มี Student A และ Student B พยายาม Claim พร้อมกัน

## เหตุการณ์

### ขั้นที่ 1

Student A ตรวจสอบ:

```text
1 > 0
```

จึงคิดว่า:

```text
มีคูปอง → Claim ได้
```

### ขั้นที่ 2

A เจอ:

```python
await ...
```

จึงหยุดชั่วคราว

### ขั้นที่ 3

Student B เข้ามาตรวจสอบก่อน A ทำต่อ:

```text
1 > 0
```

B ก็คิดว่า:

```text
มีคูปอง → Claim ได้
```

### ขั้นที่ 4

ทั้ง A และ B ทำ Claim

ผลที่อาจเกิด:

```text
count = -1
```

หรือ

```text
คูปองถูกแจกซ้ำ
```

นี่คือ Race Condition

📌 **หน้า 11:** Real-World Scenario: The Last Coupon

---

# 9. Critical Section

**Critical Section** คือส่วนของ Code ที่เข้าถึงหรือแก้ไข Shared Resource และไม่ควรให้หลาย Task เข้าไปทำพร้อมกัน

พูดง่าย ๆ:

> **Critical Section = โซนอันตรายที่ต้องป้องกัน**

ตัวอย่าง:

```text
┌──────────────────────────────┐
│       Critical Section       │
│                              │
│  ตรวจสอบคูปอง                │
│  ↓                           │
│  ตัด/นำคูปองออก              │
│                              │
└──────────────────────────────┘
```

ต้องทำให้ Task เข้าไปทีละตัว

📌 **หน้า 12:** What is a Critical Section?

---

# 10. asyncio.Lock

`asyncio.Lock` คือ Synchronization Primitive สำหรับ Async Code

หน้าที่หลักคือบังคับให้เกิด

> **Mutual Exclusion (Mutex)**

หมายความว่า:

```text
Lock มีคนถืออยู่
      ↓
Task อื่นเข้าไม่ได้
      ↓
รอ
      ↓
Task เดิมปล่อย Lock
      ↓
Task ถัดไปเข้าได้
```

เปรียบเทียบง่าย ๆ กับ **กุญแจห้องน้ำ**

```text
มี 1 กุญแจ
     ↓
คน A ถือกุญแจ → เข้าได้
คน B            → ต้องรอ
     ↓
A คืนกุญแจ
     ↓
B ได้กุญแจ → เข้าได้
```

📌 **หน้า 14:** What is asyncio.Lock?

---

# 11. Acquire และ Release

## Acquire

Task ขอ Lock

ถ้า Lock ว่าง:

```text
Acquire → ได้ Lock → ทำงาน
```

ถ้า Lock ถูกใช้อยู่:

```text
Acquire
   ↓
await
   ↓
รอ
```

---

## Release

เมื่อ Task ทำงานใน Critical Section เสร็จ:

```text
Release
   ↓
คืน Lock
   ↓
Task ถัดไปสามารถเข้าได้
```

📌 **หน้า 15:** Acquiring and Releasing Locks

---

# 12. async with lock

วิธีที่แนะนำในการใช้ Lock:

```python
async with coupon_lock:
    # Critical Section
    ...
```

ข้อดีคือ Lock จะถูกจัดการอัตโนมัติ

แม้เกิด Exception/Error ภายใน Block ก็ยังรับประกันว่า Lock จะถูก Release เมื่อออกจาก Context

ตัวอย่างจากเอกสาร:

```python
async with coupon_lock:
    if company_coupons:
        await asyncio.sleep(0.01)
        coupon = company_coupons.pop(0)
```

จุดสำคัญ:

```text
async with
    ↓
Acquire Lock
    ↓
Critical Section
    ↓
ออกจาก Block
    ↓
Release Lock
```

📌 **หน้า 16:** Async Context Manager

---

# 13. เปรียบเทียบมี Lock กับไม่มี Lock

## ❌ ไม่มี Lock

ตัวอย่าง:

```python
if company_coupons:
    await asyncio.sleep(0.01)
    coupon = company_coupons.pop(0)
```

ปัญหา:

```text
Task A ตรวจสอบ
    ↓
await
    ↓
Task B ตรวจสอบ
    ↓
Task A/B อาจแย่งข้อมูลเดียวกัน
```

อาจเกิด:

- Double-pop
- Data corruption
- Crash
- คูปองซ้ำ
- จำนวนคูปองผิด

📌 **หน้า 18:** Without Lock

---

## ✅ มี Lock

```python
async with coupon_lock:
    if company_coupons:
        await asyncio.sleep(0.01)
        coupon = company_coupons.pop(0)
```

เมื่อ A ถือ Lock:

```text
A → Critical Section
B → รอ
C → รอ
```

เมื่อ A เสร็จ:

```text
A → Release
B → ได้ Lock
```

ทำให้การเข้าถึง Critical Section เป็นลำดับ

📌 **หน้า 19:** With Lock

---

# 14. Key Differences

| หัวข้อ | ไม่มี Lock | มี Lock |
|---|---|---|
| Data Integrity | อาจเกิด Data Corruption | ข้อมูลสอดคล้องกัน |
| Critical Section | หลาย Task แทรกกันได้ | เข้าทีละ Task |
| Execution | อาจเร็วกว่า | มีเวลารอ Lock เล็กน้อย |
| ผลลัพธ์ | อาจผิด | ถูกต้องตามการป้องกัน |
| Race Condition | เสี่ยง | ป้องกันใน Critical Section |

เอกสารเน้นว่า **ไม่มี Lock อาจเร็วกว่าแต่ผลลัพธ์ผิดได้** ส่วนการใช้ Lock มีการรอคิวเล็กน้อยเพื่อแลกกับความถูกต้องของข้อมูล

📌 **หน้า 20:** Key Differences

---

# 15. Best Practices

## 15.1 Critical Section ต้องสั้น

ควรใส่เฉพาะ Logic ที่จำเป็นต้องป้องกัน

```python
async with lock:
    # อ่าน/แก้ไข Shared State
```

---

## 15.2 อย่าเอา Heavy I/O เข้า Lock โดยไม่จำเป็น

เอกสารเตือนว่าไม่ควร Lock งาน I/O ที่ใช้เวลานาน เช่น Network Call ถ้าไม่จำเป็น

เพราะจะทำให้ Async Code กลับมีลักษณะคล้ายการ Block

```text
Lock
 ↓
รอ Network นาน
 ↓
Task อื่นต้องรอ Lock
```

---

## 15.3 กฎจำสำหรับนักศึกษา ⭐

> **Identify your shared state → locate the await points → protect the read-modify-write cycle with asyncio.Lock.**

แปลให้จำง่าย:

```text
1. หา Shared State
       ↓
2. หา await ที่อยู่ระหว่างการทำงานกับ State
       ↓
3. หา Critical Section
       ↓
4. ครอบด้วย asyncio.Lock
```

📌 **หน้า 21:** Best Practices

---

# 16. Assignment: Team Coupon Hunting

เอกสารมี Assignment จำลองระบบ Client–Server สำหรับการแย่ง Coupon

แบ่งเป็นกลุ่ม:

```text
5–6 คน / กลุ่ม
```

มี Server 2 เครื่อง

### Server Machine 1

```text
server_vulnerable.py
```

เป็น Server ที่ **ไม่มี Lock**

ใช้เพื่อแสดงปัญหา Race Condition

### Server Machine 2

```text
server.py
```

เป็น Server ที่แก้ปัญหาด้วย:

```python
asyncio.Lock()
```

### Client Hunters

สมาชิกทุกคนใช้:

```text
client.py
```

เพื่อยิง Request `/claim` พร้อมกันไปยัง Server

📌 **หน้า 25:** Team Coupon Hunting

---

# 17. Dynamic Inventory

กติกาของระบบคือ:

> นักเรียน 1 คนสามารถเก็บ Coupon ได้สูงสุด 2 ใบ

จำนวน Coupon รวมถูกกำหนดตามสูตร:

```text
(N × 2) − 1
```

โดย N คือจำนวนสมาชิกในกลุ่ม

### กลุ่ม 5 คน

```text
(5 × 2) − 1 = 9
```

ผลที่ถูกต้อง:

```text
4 คน → คนละ 2 ใบ
1 คน → 1 ใบ
```

รวม:

```text
8 + 1 = 9 ใบ
```

### กลุ่ม 6 คน

```text
(6 × 2) − 1 = 11
```

ผลที่ถูกต้อง:

```text
5 คน → คนละ 2 ใบ
1 คน → 1 ใบ
```

รวม:

```text
10 + 1 = 11 ใบ
```

📌 **หน้า 26:** Dynamic Inventory Constraint

---

# 18. การทดลองที่ 1: Server ไม่มี Lock

ใช้:

```text
server_vulnerable.py
```

## ขั้นตอน

1. Server Machine 1 ตรวจสอบ IP
2. แจ้ง IP ให้สมาชิก
3. สมาชิกปรับ `SERVER_URL` ใน `client.py`
4. ยิง:

```text
POST /claim
```

พร้อมกัน

5. สังเกตผลลัพธ์

สิ่งที่อาจพบ:

```text
IndexError
CRASH_BUG
```

หรือ Client อาจได้รับ:

- Coupon เกินสิทธิ์
- Coupon รหัสซ้ำ
- จำนวน Coupon ติดลบ

นี่คือสิ่งที่การทดลองต้องการแสดงให้เห็นว่า **Race Condition สามารถเกิดขึ้นจริงใน Async Server ได้**

📌 **หน้า 27:** การทดลองกับ `server_vulnerable.py`

---

# 19. การทดลองที่ 2: Server มี Lock

เปลี่ยนไปใช้:

```text
server.py
```

ซึ่งใช้:

```python
asyncio.Lock()
```

ครอบ Critical Section ที่เกี่ยวข้องกับ:

```text
ตรวจสอบ Coupon
        ↓
ตัดจำนวน Coupon
```

จากนั้นยิง Request พร้อมกันอีกครั้ง

ระบบควร:

- แจก Coupon ตามจำนวนที่กำหนด
- ไม่แจก Coupon รหัสซ้ำ
- ผู้ใช้แต่ละคนได้สูงสุด 2 ใบ
- คนที่มาช้าที่สุดอาจได้เพียง 1 ใบ
- คนที่พยายาม Claim ใบที่ 3 ต้องถูกปฏิเสธ
- คนที่มาเมื่อ Coupon หมดต้องถูกปฏิเสธ

📌 **หน้า 28:** การยืนยันผลหลังใช้ `asyncio.Lock`

---

# 20. ไฟล์ที่ต้องส่ง

นักศึกษาทุกคนต้องส่ง Source Code ของตัวเอง โดยเอกสารกำหนด 3 ไฟล์หลัก:

## 1. `server_vulnerable.py`

Server Async ที่:

```text
ไม่มี Lock
```

เพื่อแสดงจุดเสี่ยงของ Race Condition

---

## 2. `server.py`

Server ที่:

```text
แก้ Race Condition ด้วย asyncio.Lock
```

และกำหนดจำนวน Coupon ตาม:

```text
N × 2 − 1
```

---

## 3. `client.py`

Client สำหรับส่ง HTTP Request แบบ Concurrent โดยใช้:

```python
httpx.AsyncClient
```

เพื่อพยายาม Claim Coupon ให้ได้ 2 ใบ

📌 **หน้า 29:** Submission Deliverables

---

# 21. Flow รวมทั้งบท

```text
             Async Tasks
                  │
                  ▼
          ┌───────────────┐
          │  Shared State │
          │    Coupon     │
          └───────┬───────┘
                  │
           หลาย Task เข้าถึง
                  │
                  ▼
           ┌─────────────┐
           │ await point │
           └──────┬──────┘
                  │
                  ▼
          Race Condition
                  │
                  ▼
          Data ผิด / ซ้ำ / Crash
                  │
                  │ แก้ด้วย
                  ▼
        ┌──────────────────┐
        │  asyncio.Lock    │
        │      Mutex       │
        └────────┬─────────┘
                 │
                 ▼
          Critical Section
          เข้าได้ทีละ Task
                 │
                 ▼
          Data Consistency
```

---

# 22. สูตรวิเคราะห์ Code ข้อสอบ 🧠

เวลาเจอ Code Async ให้ไล่ตามนี้:

```text
① มี Shared State ไหม?
        ↓
② มีหลาย Task เข้าถึงไหม?
        ↓
③ มี await อยู่ระหว่าง Read/Modify/Write ไหม?
        ↓
④ ถ้ามี → มีโอกาส Race Condition
        ↓
⑤ Critical Section อยู่ตรงไหน?
        ↓
⑥ มี asyncio.Lock ครอบไหม?
        ↓
⑦ ถ้ามี → Task อื่นต้องรอ Lock
```

---

# 23. จำแบบสั้นที่สุดก่อนสอบ ⭐⭐⭐

> **Asyncio = หลาย Task ทำงาน Concurrent บน Event Loop**

> **Single Thread ≠ ไม่มี Race Condition**

> **await = จุดที่ Task สามารถคืนการควบคุมให้ Event Loop**

> **Shared State = ข้อมูลที่หลาย Task เข้าถึงร่วมกัน**

> **Race Condition = ผลลัพธ์ขึ้นกับจังหวะการสลับ Task**

> **Read → await → Write = จุดเสี่ยงสำคัญ**

> **Critical Section = ส่วนที่ต้องป้องกัน**

> **asyncio.Lock = Mutex สำหรับ Async Code**

> **Acquire = ขอ/ถือ Lock**

> **Release = คืน Lock**

> **async with lock = วิธีจัดการ Lock ที่แนะนำ**

> **Lock ต้องครอบ Critical Section**

> **อย่า Lock Heavy I/O โดยไม่จำเป็น**

> **เป้าหมายของ Lock = Data Consistency**

---

# 24. ตารางจำเร็ว

| คำศัพท์ | จำว่า |
|---|---|
| Async Programming | ทำหลายงานแบบ Concurrent |
| Event Loop | ตัวจัดการ Task |
| `await` | คืนการควบคุมให้ Event Loop |
| Shared State | ข้อมูลที่หลาย Task ใช้ร่วมกัน |
| Race Condition | ผลลัพธ์ขึ้นกับจังหวะ |
| Read–Modify–Write | รูปแบบที่เสี่ยง |
| Critical Section | โซนที่ต้องป้องกัน |
| `asyncio.Lock` | ตัวป้องกันการเข้าพร้อมกัน |
| Acquire | ขอ/รับ Lock |
| Release | คืน Lock |
| `async with lock` | ใช้ Lock อย่างปลอดภัย |
| Mutex | Mutual Exclusion |
| `server_vulnerable.py` | ไม่มี Lock |
| `server.py` | มี `asyncio.Lock` |
| `client.py` | ยิง Request Concurrent |

---

# 25. จุดสำคัญที่สุดที่ควรเข้าใจ

ถ้าต้องจำเพียงภาพเดียว ให้จำ:

```text
Shared State
     │
     ▼
Task A ──────┐
             │
             ▼
           await
             │
             ▼
Task B ──────┤
             │
             ▼
     แก้ Shared State
             │
             ▼
      Race Condition
```

วิธีแก้:

```text
             asyncio.Lock
                  │
                  ▼
Task A → [ Critical Section ] → Release
                  │
                  ▼
Task B → [ Critical Section ] → Release
```

ดังนั้นแก่นของบทนี้คือ:

> **ปัญหาไม่ได้เกิดเพราะมีหลาย Thread แต่เกิดเพราะหลาย Async Task สามารถสลับกันที่ `await` ระหว่างการทำงานกับ Shared State ได้**

---

## อ้างอิงจากเอกสาร

- หน้า 3–6: Asynchronous Programming, Event Loop, `await` และ Shared State fileciteturn6file0L7-L28
- หน้า 8–12: Race Condition, Read–Modify–Write และ Critical Section fileciteturn6file0L30-L62
- หน้า 14–16: `asyncio.Lock`, Acquire/Release และ `async with` fileciteturn6file0L64-L85
- หน้า 18–21: เปรียบเทียบ Code มี/ไม่มี Lock และ Best Practices fileciteturn6file0L89-L111
- หน้า 25–29: Assignment, Dynamic Inventory, การทดลอง และไฟล์ที่ต้องส่ง fileciteturn6file0L122-L162
