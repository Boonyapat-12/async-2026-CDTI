# Redis — สรุปเนื้อหาแบบอ่านง่าย

> เรียบเรียงจากเอกสาร **Introduction to Redis, In-Memory Data Structure Stores** จำนวน 23 หน้า โดยคงแนวคิด คำศัพท์ ตัวอย่าง และกรอบเนื้อหาตามเอกสารต้นฉบับ

---

## สารบัญ

1. [Redis คืออะไร](#1-redis-คืออะไร)
2. [ทำไม Redis ถึงเร็ว](#2-ทำไม-redis-ถึงเร็ว)
3. [Data Structures ของ Redis](#3-data-structures-ของ-redis)
4. [Single-Thread Architecture](#4-single-thread-architecture)
5. [I/O Multiplexing](#5-io-multiplexing)
6. [Performance](#6-performance)
7. [Production Use Cases](#7-production-use-cases)
8. [Caching Layer](#8-caching-layer)
9. [Pub/Sub และ Queues](#9-pubsub-และ-queues)
10. [Rate Limiting](#10-rate-limiting)
11. [RDB vs AOF](#11-rdb-vs-aof)
12. [Redis ในฐานะ Messaging Engine](#12-redis-ในฐานะ-messaging-engine)
13. [Redis Pub/Sub](#13-redis-pubsub)
14. [Redis Streams](#14-redis-streams)
15. [Consumer Groups](#15-consumer-groups)
16. [เปรียบเทียบ Pub/Sub กับ Streams](#16-เปรียบเทียบ-pubsub-กับ-streams)
17. [Real-World Use Cases](#17-real-world-use-cases)
18. [Telemetry Pipeline](#18-telemetry-pipeline)
19. [F1 Telemetry & Grand Prix Architecture](#19-f1-telemetry--grand-prix-architecture)
20. [สรุปจำก่อนสอบ](#20-สรุปจำก่อนสอบ)

---

# 1. Redis คืออะไร

Redis คือระบบ **In-Memory Data Structure Store**

แนวคิดหลักคือ Redis เก็บ Active Data ไว้ใน:

```text
RAM (Main Memory)
```

แทนการทำงานกับข้อมูลจาก Disk เป็นหลักเหมือนฐานข้อมูลแบบดั้งเดิม

### ผลที่ได้

- Latency ต่ำมาก
- ประมวลผลข้อมูลได้เร็ว
- รองรับ Operations จำนวนมาก
- เหมาะกับระบบ Real-Time

📌 **หน้า 2–3:** Core Fundamentals และ In-Memory Speed

---

# 2. ทำไม Redis ถึงเร็ว

## 2.1 เก็บข้อมูลใน RAM

RAM มีความเร็วสูงกว่า Disk และไม่ต้องรอ Disk Seek / Heavy I/O

เอกสารระบุว่า RAM Operations สามารถทำงานในระดับ:

```text
Microseconds
(< 1 ms)
```

จึงทำให้ Redis มี **Sub-Millisecond Latency**

---

## 2.2 High Throughput

Redis สามารถรองรับ:

```text
100,000+ Operations / Second
```

บน Hardware ระดับหนึ่งได้ตาม Benchmark ที่ระบุในเอกสาร

---

## 2.3 Volatile แต่ทำ Persistence ได้

โดยธรรมชาติ RAM เป็น Memory แบบ Volatile

แต่ Redis มีระบบ Persistence ที่สามารถบันทึกข้อมูลลง Disk ได้ เช่น:

```text
RDB
AOF
```

ดังนั้น Redis ไม่ได้หมายความว่า:

> ข้อมูลจะอยู่เฉพาะใน RAM และหายทั้งหมดเสมอไป

แต่สามารถกำหนดวิธีเก็บข้อมูลลง Disk ได้

📌 **หน้า 3:** Storage Medium, Sub-Millisecond Latency, High Throughput และ Persistence

---

# 3. Data Structures ของ Redis

Redis ไม่ได้เก็บข้อมูลแบบ Key-Value ธรรมดาเพียงอย่างเดียว แต่รองรับ Data Structures หลายชนิด

## 3.1 Strings

เก็บได้ เช่น:

- Text
- Numbers
- Binary Blobs
- Atomic Counters

ตัวอย่างแนวคิด:

```text
key → value
```

---

## 3.2 Hashes

เป็นโครงสร้างแบบ:

```text
Field → Value
```

เหมาะกับการแทน Object

ตัวอย่าง:

```text
user
 ├── name
 ├── age
 └── email
```

---

## 3.3 Lists

เป็น Linked List

สามารถใช้ทำ:

- Message Queue
- Stack

---

## 3.4 Sets

เป็น Collection ที่:

```text
ไม่เรียงลำดับ
+
ข้อมูลไม่ซ้ำกัน
```

รองรับ Set Operations เช่น:

```text
Union
Intersection
```

---

## 3.5 Sorted Sets

ข้อมูลถูกจัดเรียงด้วย:

```text
Score
```

เหมาะกับงานอย่าง:

```text
Real-Time Leaderboard
```

---

## 3.6 Streams

เป็นโครงสร้างแบบ:

```text
Append-Only Log
```

เหมาะกับ:

```text
Event Streaming
```

📌 **หน้า 4:** Core Data Structures

---

# 4. Single-Thread Architecture

Redis ใช้แนวคิด **Single-Threaded Execution Core**

หมายถึงการประมวลผล Command หลักทำงานบน Thread เดียว

ข้อดีตามเอกสาร:

```text
ไม่ต้องจัดการ
Race Conditions
Locks
Context Switching
```

ในส่วน Command Processing

📌 **หน้า 5:** Single-Thread Architecture

---

# 5. I/O Multiplexing

แม้ Redis ใช้ Single Thread แต่สามารถดูแล Client Connections จำนวนมากได้ด้วย:

```text
I/O Multiplexing
```

โดยใช้กลไก เช่น:

```text
epoll
kqueue
```

แนวคิดคือใช้ Non-Blocking System Calls เพื่อ Monitor Client Sockets จำนวนมากพร้อมกัน

```text
Client 1 ─┐
Client 2 ─┤
Client 3 ─┤
Client 4 ─┼──► Redis Event Loop / I/O
Client N ─┘
```

ดังนั้น Single Thread ไม่ได้หมายความว่า Redis รองรับ Client ได้เพียงคนเดียว

📌 **หน้า 5:** ภาพ Architecture แสดง Event Loop และการจัดการ Requests/Connections

---

# 6. Performance

Redis สามารถทำ:

```text
100K+ Operations / Second
```

ตาม Benchmark ในเอกสาร

ผลดีเมื่อใช้เป็น Cache Layer:

```text
Application
     │
     ▼
  Redis Cache
     │
     ▼
Primary Database
```

Redis ช่วยลด:

- CPU Load
- Memory Load

ของ Primary Database

และให้ Response Time ระดับ Microseconds ตามที่เอกสารระบุ

📌 **หน้า 6:** High Performance Benchmarks

---

# 7. Production Use Cases

เอกสารยกตัวอย่างการใช้งาน Redis ใน Production ได้แก่:

```text
1. Caching Layer
2. Pub/Sub & Queues
3. Rate Limiting
4. Real-Time Systems
5. Messaging / Event Streaming
```

📌 **หน้า 8–10:** Common Production Use Cases

---

# 8. Caching Layer

Redis สามารถใช้เป็น Cache สำหรับข้อมูลที่ถูกเรียกใช้งานบ่อย หรือ **Hot Data**

Pattern ที่เอกสารกล่าวถึง:

```text
Cache-Aside
Write-Through
```

เป้าหมายคือ:

> ลดเวลาในการตอบสนองของระบบ

ตัวอย่างแนวคิด:

```text
Client
  │
  ▼
Application
  │
  ├──► Redis Cache
  │
  └──► Database
```

ถ้าข้อมูลอยู่ใน Redis ก็สามารถตอบกลับได้เร็วโดยไม่ต้องไปอ่าน Primary Database ทุกครั้ง

📌 **หน้า 8:** Caching Layer

---

# 9. Pub/Sub และ Queues

Redis สามารถใช้สำหรับการส่ง Message และช่วย **Decouple Microservices**

รูปแบบหลัก:

```text
Producer
    │
    ▼
 Redis
    │
    ├──► Subscriber
    └──► Subscriber
```

เอกสารกล่าวถึงทั้ง:

```text
Redis Pub/Sub
Redis Streams
Redis Lists
```

สำหรับการทำ Messaging / Queue

📌 **หน้า 9:** Pub/Sub & Queues

---

# 10. Rate Limiting

Redis สามารถใช้ทำ:

```text
Rate Limiting
```

โดยเอกสารยกตัวอย่าง:

```text
Sliding Window Algorithm
```

สำหรับ:

- API Gateway Protection
- Live Leaderboards

แนวคิดคือจำกัดจำนวน Request/Operation ที่ User สามารถทำได้ภายในช่วงเวลาหนึ่ง

📌 **หน้า 10:** Rate Limiting

---

# 11. RDB vs AOF

Redis มี Persistence หลักที่เอกสารเน้น 2 แบบ:

```text
RDB
AOF
```

---

## 11.1 RDB — Redis Database

RDB สร้าง:

```text
Point-in-Time Snapshot
```

เป็น Compact Binary Snapshot

ข้อดีตามเอกสาร:

- Recovery เร็ว
- Runtime Performance Impact ต่ำ

ภาพรวม:

```text
Redis Memory
     │
     ▼
 Snapshot
     │
     ▼
   Disk
```

---

## 11.2 AOF — Append-Only File

AOF บันทึก:

```text
ทุก Write Operation
```

แบบ Sequential Log

ข้อดี:

- Data Durability สูง
- กำหนด Sync Interval ได้

ภาพรวม:

```text
WRITE 1 ─┐
WRITE 2 ─┤
WRITE 3 ─┼──► AOF
WRITE 4 ─┘
```

---

## RDB vs AOF จำง่าย

| หัวข้อ | RDB | AOF |
|---|---|---|
| รูปแบบ | Snapshot | Log ทุก Write |
| Recovery | เร็ว | เน้นความทนทานของข้อมูล |
| File | Compact Binary | Append-Only Log |
| จุดเด่น | Runtime Impact ต่ำ | Durability สูง |

📌 **หน้า 11:** Data Persistence Options

---

# 12. Redis ในฐานะ Messaging Engine

Redis เหมาะกับ Messaging เพราะ:

```text
In-Memory
+
Ultra-Low Latency
+
High Throughput
```

เอกสารระบุรูปแบบ Messaging สำคัญ 3 แบบ:

```text
1. Pub/Sub
2. Redis Streams
3. Lists
```

### Pub/Sub

```text
Fire-and-Forget
```

### Streams

```text
Persistent Event Streams
```

### Lists

สามารถใช้ทำ:

```text
Message Queue
```

เช่น:

```text
LPUSH
BRPOP
```

📌 **หน้า 13:** Why Redis for Messaging?

---

# 13. Redis Pub/Sub

## Publish–Subscribe Pattern

มี:

```text
Publisher
    │
    ▼
 Channel
    │
    ├──► Subscriber A
    ├──► Subscriber B
    └──► Subscriber C
```

Publisher ไม่จำเป็นต้องรู้ว่า Subscriber คือใคร

คำสั่งสำคัญ:

```text
PUBLISH channel message

SUBSCRIBE channel

PSUBSCRIBE pattern*
```

---

## จุดสำคัญที่สุด: At-Most-Once

Redis Pub/Sub เป็น:

> **At-most-once delivery**

หรือในเอกสารเรียกว่า:

> **Fire-and-Forget**

ถ้า Subscriber Offline ตอนที่ Message ถูก Publish:

```text
Message
   ↓
Subscriber Offline
   ↓
❌ Message หาย
```

ไม่มี Message History ให้ย้อนกลับมาอ่าน

📌 **หน้า 14:** Redis Pub/Sub

---

# 14. Redis Streams

Redis Streams เป็น:

> **Append-Only Log Data Structure**

เริ่มมีใน Redis 5.0 ตามเอกสาร

โครงสร้าง:

```text
Stream
 │
 ├── Event 1
 ├── Event 2
 ├── Event 3
 ├── Event 4
 └── Event 5
```

---

## 14.1 Persistence

Message สามารถ:

```text
อยู่ใน Memory
+
บันทึกลง Disk
```

---

## 14.2 Unique ID

แต่ละ Message จะมี ID ที่ Redis สร้างให้อัตโนมัติ เช่น:

```text
1690000000000-0
```

ลักษณะ ID ประกอบด้วย Timestamp และ Sequence

---

## 14.3 Replayability

Consumer สามารถอ่าน Message เก่าได้

เช่น:

```text
Event 1
Event 2
Event 3
Event 4
```

ถ้า Consumer พลาด Event 2 ก็สามารถอ่านย้อนหลังจากจุดที่ต้องการได้

📌 **หน้า 16:** Pattern 2 — Redis Streams

---

# 15. Consumer Groups

Consumer Groups ใช้เมื่อมี Consumer หลายตัวช่วยกันประมวลผล Stream

```text
             Redis Stream
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Consumer 1          Consumer 2
```

แต่ละ Message สามารถถูกส่งไปยัง Consumer ที่แตกต่างกันภายใน Group

---

## Load Balancing

Consumer หลายตัว:

```text
Consumer 1 → งาน A
Consumer 2 → งาน B
Consumer 3 → งาน C
```

ช่วยแบ่งภาระการประมวลผล

---

## At-Least-Once Delivery

Consumer ต้อง Acknowledge Message ด้วย:

```text
XACK
```

แนวคิด:

```text
รับ Message
     ↓
ประมวลผล
     ↓
XACK
     ↓
ถือว่างานถูก Acknowledge
```

---

## Pending Entries List — PEL

Redis จะติดตาม Message ที่ยังไม่ได้รับการ Acknowledge

เรียกว่า:

```text
Pending Entries List (PEL)
```

มีประโยชน์เมื่อ Consumer Crash เพราะสามารถติดตามงานที่ยังค้างอยู่ได้

📌 **หน้า 17:** Advanced Streams — Consumer Groups

---

# 16. เปรียบเทียบ Pub/Sub กับ Streams

นี่คือหัวข้อที่ควรจำมากที่สุด ⭐

| หัวข้อ | Redis Pub/Sub | Redis Streams |
|---|---|---|
| แนวคิด | Fire-and-Forget | Persistent Event Stream |
| การเก็บ Message | ❌ ไม่มี History | ✅ เก็บ Message |
| Offline Consumer | ❌ พลาดแล้วหาย | ✅ อ่านย้อนหลังได้ |
| Replay | ❌ ไม่ได้ | ✅ ได้ |
| Delivery | At-Most-Once | รองรับ At-Least-Once ผ่าน Consumer Groups |
| Consumer Groups | ❌ | ✅ |
| Acknowledge | ❌ | ✅ `XACK` |
| เหมาะกับ | Real-Time Broadcast | Event Processing |

### จำสั้น ๆ

```text
Pub/Sub
= เร็ว + สด + ไม่เก็บ

Streams
= เก็บ + ย้อนอ่าน + ประมวลผลเป็นระบบ
```

📌 **หน้า 14–17:** Pub/Sub และ Streams

---

# 17. Real-World Use Cases

## Use Case 1 — Real-Time Dashboard & Chat

ใช้:

```text
Redis Pub/Sub
```

เหมาะกับ:

- Instant WebSocket Broadcasting
- Live Audio/Video Chat Signaling
- Real-Time Notifications

เหตุผลคือไม่จำเป็นต้องเก็บ Message History ทุกข้อความ

📌 **หน้า 19 และ 21:** Real-Time Dashboard & Chat

---

## Use Case 2 — Order Processing Pipeline

ใช้:

```text
Redis Streams
```

ตัวอย่าง:

```text
Order Service
     │
     ▼
Redis Stream
     │
     ├──► Payment Service
     │
     └──► Inventory Service
```

เหมาะกับระบบ E-Commerce Checkout

📌 **หน้า 19:** Order Processing Pipeline

---

## Use Case 3 — Rate Limiting & Event Sourcing

ใช้:

```text
Redis Streams
```

สามารถเก็บ User Activity Events พร้อม Timestamp เพื่อใช้กับ:

```text
Audit Logs
```

📌 **หน้า 19:** Rate Limiting & Event Sourcing

---

# 18. Telemetry Pipeline

เอกสารยกตัวอย่าง Redis Streams กับ IoT Telemetry

Sensor ส่งข้อมูลความถี่สูง:

```text
IoT Sensor
    │
    │ High-Frequency Data
    ▼
Redis Stream
    │
    ├──► Worker 1
    ├──► Worker 2
    └──► Worker 3
```

Redis Stream ทำหน้าที่เป็น Buffer ระหว่าง:

```text
High-Frequency Sensors
          ↓
     Redis Stream
          ↓
Backend / Database
```

ช่วยป้องกัน Backend Database ถูกโหลดหนักเกินไป

---

## จุดเด่นจากเอกสาร

ข้อมูลถูกเก็บเป็น:

```text
Immutable
+
Ordered
+
Time-Series Entries
```

และมี Unique IDs อัตโนมัติ

Consumer สามารถ:

```text
อ่านข้อมูลเก่า
Replay Event
```

และ Worker หลายตัวสามารถแบ่งงานกันประมวลผล พร้อมใช้:

```text
XACK
```

📌 **หน้า 20:** Telemetry Data Pipeline

---

# 19. F1 Telemetry & Grand Prix Architecture

หน้า 23 เป็นตัวอย่างการรวม:

```text
Redis Streams
+
Consumer Groups
+
Live Pub/Sub
```

เข้าด้วยกันในระบบ F1

---

## Teacher Race Control

กำหนดสถานะการแข่งขัน:

```text
SET f1:race:status = "GREEN"
```

จากนั้นส่ง Start Signal Broadcast

---

## Student 1 — F1 Car

รถสร้าง Telemetry ต่อเนื่อง:

```text
20 Hz
```

ตัวอย่างข้อมูล:

```text
speed = 280
gear = 7
rpm = 13500
dist = 2450.5m
```

ข้อมูลถูกส่งเข้า:

```text
Redis Stream
```

---

## Student 2 — Pit Strategy

อ่านข้อมูล Telemetry เพื่อดู:

```text
Tire Wear
```

และตัดสินใจ:

```text
BOX BOX BOX
```

---

## Student 3 — Race Safety

ตรวจสอบ:

```text
Engine Temperature
RPM
```

---

## Student 4 — DRS Control

ควบคุม:

```text
DRS
OPEN / CLOSE
```

---

## Student 5 — Broadcaster

ส่งข้อมูล Live Dashboard ผ่าน:

```text
PUB/SUB
```

Channel:

```text
f1:dashboard:g01
```

Dashboard แสดงข้อมูล เช่น:

```text
Speed: 285 km/h
Gear: 7
RPM: 13,500
Distance
Leaderboard Telemetry
```

📌 **หน้า 23:** F1 Telemetry Data Pipeline & Grand Prix Architecture

---

# 20. Flow รวมทั้งบท

```text
                     ┌────────────────────┐
                     │       Redis        │
                     │  In-Memory Store   │
                     └─────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
         Cache              Pub/Sub          Streams
             │                 │                 │
             │                 │                 ├──► Consumer
             │                 │                 ├──► Consumer
             │                 │                 └──► Consumer
             │                 │
             │                 └──► Subscribers
             │
             ▼
         Database
```

---

# 21. จุดที่ควรจำก่อนสอบ ⭐⭐⭐

## ⭐ Redis คืออะไร?

> **In-Memory Data Structure Store**

---

## ⭐ Redis เร็วเพราะอะไร?

```text
RAM
 ↓
ไม่ต้องรอ Disk I/O
 ↓
Sub-Millisecond Latency
 ↓
High Throughput
```

---

## ⭐ Redis Data Structures

จำ:

```text
String
Hash
List
Set
Sorted Set
Stream
```

---

## ⭐ Redis Single Thread

```text
Command Processing
        ↓
   Single Thread
```

แต่สามารถรองรับ Client จำนวนมากด้วย:

```text
I/O Multiplexing
(epoll / kqueue)
```

---

## ⭐ Redis Pub/Sub

จำว่า:

```text
Fire-and-Forget
At-Most-Once
No History
No Replay
```

ถ้า Subscriber Offline:

```text
❌ Message หาย
```

---

## ⭐ Redis Streams

จำว่า:

```text
Append-Only Log
Persistent
Replayable
Unique ID
```

เหมาะกับ:

```text
Event Processing
Telemetry
Order Pipeline
```

---

## ⭐ Consumer Groups

จำว่า:

```text
หลาย Consumer
      ↓
แบ่งงานกัน
      ↓
Load Balancing
```

และมี:

```text
XACK
PEL
At-Least-Once
```

---

## ⭐ RDB vs AOF

```text
RDB
= Snapshot
= Recovery เร็ว
= Runtime Impact ต่ำ

AOF
= Log ทุก Write
= Durability สูง
```

---

# 22. ตารางจำเร็ว

| คำศัพท์ | จำว่า |
|---|---|
| Redis | In-Memory Data Structure Store |
| RAM | Storage หลักของ Active Data |
| Sub-Millisecond | Latency ต่ำกว่า 1 ms |
| String | Text / Number / Binary / Counter |
| Hash | Field–Value |
| List | Linked List / Queue / Stack |
| Set | Unique / Unordered |
| Sorted Set | Sort ตาม Score |
| Stream | Append-Only Log |
| Pub/Sub | Fire-and-Forget |
| At-Most-Once | พลาดแล้วไม่ส่งซ้ำ |
| Stream | Persistent / Replayable |
| Consumer Group | แบ่งงานหลาย Consumer |
| XACK | Acknowledge Message |
| PEL | Pending Entries List |
| RDB | Snapshot |
| AOF | Append-Only Write Log |
| Cache | เก็บ Hot Data |
| Rate Limiting | จำกัด Request |
| I/O Multiplexing | จัดการ Socket จำนวนมาก |

---

# 23. จำแบบสั้นที่สุด 🧠

> **Redis = RAM + Data Structures + Speed**

> **Redis เร็วเพราะ Active Data อยู่ใน RAM**

> **Single Thread ไม่ได้แปลว่ารับ Client ได้คนเดียว**

> **I/O Multiplexing = จัดการ Connections จำนวนมาก**

> **Pub/Sub = ส่งทันที แต่ไม่เก็บ**

> **Pub/Sub = At-Most-Once**

> **Streams = เก็บ Event และ Replay ได้**

> **Consumer Groups = แบ่งงานกันประมวลผล**

> **XACK = ยืนยันว่า Process แล้ว**

> **PEL = ติดตาม Message ที่ยังไม่ Acknowledge**

> **RDB = Snapshot**

> **AOF = Log ทุก Write**

> **Cache = ลดภาระ Database**

---

# 24. จุดที่มักเอาไปออกข้อสอบ ⭐

## ถ้าถามว่า “ต้องการ Real-Time Notification และไม่สนใจ History”

ตอบ:

```text
Redis Pub/Sub
```

เพราะเป็น Fire-and-Forget และส่งให้ Subscriber ที่กำลัง Online

---

## ถ้าถามว่า “ต้องการเก็บ Event และอ่านย้อนหลัง”

ตอบ:

```text
Redis Streams
```

เพราะมี Persistence และ Replayability

---

## ถ้าถามว่า “Consumer หลายตัวช่วยกันทำงาน”

ตอบ:

```text
Consumer Groups
```

และเกี่ยวข้องกับ:

```text
Load Balancing
XACK
PEL
```

---

## ถ้าถามว่า “ทำไม Redis เร็ว”

ตอบประเด็นหลัก:

```text
In-Memory / RAM
+
Sub-Millisecond Latency
+
Single-Thread Command Processing
+
I/O Multiplexing
```

---

## ถ้าถามว่า “RDB กับ AOF ต่างกันอย่างไร”

จำ:

```text
RDB → Snapshot
AOF → Log ทุก Write
```

---

## ถ้าถามว่า “Redis Streams เหมาะกับอะไร”

ตัวอย่างจากเอกสาร:

```text
Order Processing
IoT Telemetry
Event Sourcing
Rate Limiting
```

---

# 25. ภาพรวมทั้งบทในประโยคเดียว

> **Redis คือ In-Memory Data Structure Store ที่เน้นความเร็วสูง และสามารถนำไปใช้ได้ทั้ง Cache, Pub/Sub, Message Queue และ Persistent Event Streaming โดย Pub/Sub เน้น Real-Time แบบ Fire-and-Forget ส่วน Streams เน้นการเก็บ Event, Replay และการประมวลผลร่วมกันผ่าน Consumer Groups**

---

## อ้างอิงจากเอกสาร

- หน้า 3–6: In-Memory Speed, Data Structures, Single-Thread Architecture และ Performance fileciteturn7file0L8-L48
- หน้า 8–11: Caching, Pub/Sub/Queues, Rate Limiting และ RDB/AOF fileciteturn7file0L53-L79
- หน้า 13–17: Redis Messaging, Pub/Sub, Streams และ Consumer Groups fileciteturn7file0L85-L117
- หน้า 19–21: Real-World Use Cases, Telemetry และ Pub/Sub Monitoring fileciteturn7file0L120-L155
- หน้า 23: F1 Telemetry Data Pipeline & Grand Prix Architecture fileciteturn7file0L161-L197
