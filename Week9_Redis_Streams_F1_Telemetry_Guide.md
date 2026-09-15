# Week 9 — Redis Streams & F1 Telemetry Pipeline Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงปัจจุบันทุกไฟล์ใน `Week9/`** เพื่อให้เริ่มเรียนได้ตั้งแต่ศูนย์ เข้าใจสถาปัตยกรรมของระบบ และใช้ทบทวนก่อนสอบหรือก่อนลง Lab จริงได้ค่ะ

> **เป้าหมายหลัก:** อ่านจบแล้วควรอธิบายได้ว่า Redis Stream, Consumer Group, Consumer, Pending Entry, ACK, Redis Pub/Sub และ Race Control Key ทำงานร่วมกันอย่างไร รวมถึงมองเห็นข้อจำกัดสำคัญของโค้ดปัจจุบันที่ใช้ Consumer Group ชื่อเดียวกันทุกบทบาท

ไฟล์ที่ใช้อ้างอิง:

1. `Week9/f1_telemetry.md`
2. `Week9/docker-compose.yaml`
3. `Week9/student1_telemetry_producer.py`
4. `Week9/student2_pit_strategy_engineer.py`
5. `Week9/student3_race_control_engine_safety.py`
6. `Week9/student4_DRS_automation_controller.py`
7. `Week9/student5_dashboard_broadcaster.py`
8. `Week9/dashboard_listener.py`
9. `Week9/teacher_race_control.py`

สถานะการตรวจ ณ ตอนเขียนคู่มือ:

- ตรวจ syntax ของ Python ทั้ง Week 9 ด้วย `python -m py_compile Week9/*.py` แล้วผ่าน
- อ่านและเทียบค่าคงที่ ชื่อ key/channel เงื่อนไข และ flow จาก source ปัจจุบันแล้ว
- **ยังไม่ได้อ้างว่าได้รันการแข่งขัน end-to-end กับ Redis จริงในรอบการเขียนคู่มือนี้**
- ตัวอย่าง output ในคู่มือจึงระบุเป็น “พฤติกรรมที่คาดจากโค้ด” ไม่ใช่ log ที่สร้างขึ้นมาแทนการรันจริง

---

## สารบัญ

1. ภาพรวมบทเรียน
2. Use case และสิ่งที่ได้ฝึก
3. คำศัพท์สำคัญ
4. สถาปัตยกรรมภาพใหญ่
5. Redis data type ทั้งสามแบบที่ใช้
6. Namespace และค่าคงที่จริง
7. Telemetry schema
8. Redis Stream ID
9. Producer และอัตรา 20 Hz
10. การคำนวณระยะทางและเวลาจบโดยประมาณ
11. `student1_telemetry_producer.py`
12. Race Start Barrier
13. `XADD` และการ trim Stream
14. Consumer Group model
15. `$`, `>` และความหมายที่ต้องจำ
16. Pending Entries และ `XACK`
17. `student2_pit_strategy_engineer.py`
18. `student3_race_control_engine_safety.py`
19. `student4_DRS_automation_controller.py`
20. `student5_dashboard_broadcaster.py`
21. Stream-to-Pub/Sub bridge
22. `dashboard_listener.py`
23. `teacher_race_control.py`
24. การเรียงอันดับและเส้นชัย
25. Shared Consumer Group: ประเด็นใหญ่ที่สุด
26. Load balancing vs fan-out
27. วิธีออกแบบ fan-out หากโจทย์ต้องการทุกบทบาทเห็นทุก packet
28. End-to-end data journey
29. ลำดับรันที่ถูกต้องสำหรับ local practice
30. การติดตั้ง dependency
31. การเปิด Redis ด้วย Docker Compose
32. คำสั่งรันทุก component
33. การตรวจสุขภาพ Redis และ Stream
34. การตรวจ Pending/Lag
35. Expected behavior
36. การหยุดและ cleanup
37. Local vs classroom configuration
38. ความไม่ตรงกันระหว่างใบงานกับไฟล์จริง
39. Docker Compose แบบละเอียด
40. Current-code caveats
41. Reliability และ message recovery
42. Performance และ bottleneck
43. Security และ operational safety
44. Troubleshooting matrix
45. Debug checklist ตามลำดับ
46. แบบฝึกหัด
47. เฉลยแบบฝึกหัด
48. คำถามแนวสอบพร้อมคำตอบ
49. Exam checklist
50. Cheat sheet
51. สรุปสุดท้าย

---

# Part A — เข้าใจระบบจากภาพใหญ่

## 1. Week 9 กำลังเรียนเรื่องอะไร

Week 9 เปลี่ยนจาก Queue ที่อยู่ภายใน Python process เดียว ไปสู่ระบบส่งข้อมูลผ่าน **Redis Server** ซึ่งโปรแกรมหลายตัวและหลายเครื่องสามารถเชื่อมต่อร่วมกันได้

โจทย์จำลองรถ F1 ที่ส่งข้อมูล telemetry แบบต่อเนื่อง:

```text
รถจำลองสร้างข้อมูล 20 ครั้ง/วินาที
              |
              v
Redis Stream: f1:telemetry:g04
              |
              +--> Consumer Group: f1_pitwall
                        |
                        +--> Pit Strategy วิเคราะห์ยาง
                        +--> Engine Safety วิเคราะห์อุณหภูมิ/RPM
                        +--> DRS Controller วิเคราะห์ความเร็ว/เกียร์
                        +--> Dashboard Broadcaster แปลงเป็น JSON
                                           |
                                           v
                              Redis Pub/Sub: f1:dashboard:g04
                                           |
                              +------------+-------------+
                              |                          |
                              v                          v
                       Team Dashboard             Teacher Leaderboard
```

ลูกศรจาก Consumer Group ด้านบนแสดง **ปลายทางที่เป็นไปได้** ของแต่ละ entry ไม่ได้หมายความว่า Redis สำเนา entry เดียวให้ครบทั้งสี่บทบาท โค้ดปัจจุบันเป็น load balancing: entry หนึ่งถูกส่งให้ consumer หนึ่งตัวใน `f1_pitwall` ซึ่งจะวิเคราะห์เชิงลึกอีกครั้งใน Part G

มีช่องทางควบคุมเพิ่มอีกสองส่วน:

```text
String key: f1:race:status
    STOPPED -> รถรอ
    GREEN   -> รถออกตัว

Pub/Sub channel: f1:race:finish
    รถส่ง {"group_id": "g04"} เมื่อครบ 10,000 เมตร
```

หัวใจของบทเรียนมีมากกว่า “ส่งข้อความได้” ได้แก่:

- ข้อมูลแบบต่อเนื่องควรเก็บอย่างไร
- หลาย worker แบ่งงานกันอย่างไร
- message จะได้รับการยืนยันเมื่อใด
- Stream ต่างจาก Pub/Sub อย่างไร
- จะสั่งให้หลาย producer เริ่มพร้อมกันอย่างไร
- namespace ป้องกันข้อมูลแต่ละกลุ่มชนกันอย่างไร
- throughput, latency และ terminal overhead เกี่ยวข้องกันอย่างไร
- ถ้า process ล้มก่อน ACK จะเกิดอะไรขึ้น

---

## 2. Use case — เรียนแล้วนำไปใช้อะไรได้

แนวคิดเดียวกันประยุกต์กับระบบจริงได้ เช่น:

- IoT sensor telemetry
- log processing pipeline
- vehicle tracking
- clickstream analytics
- order/event processing
- monitoring และ alerting
- fraud detection
- dashboard แบบ real-time
- pipeline ที่ต้องมี worker หลายตัว
- การกระจายงานให้ consumer pool

สิ่งที่ควรทำได้หลังเรียน:

1. สร้าง producer ที่เขียน event เข้า Redis Stream
2. สร้าง Consumer Group และอ่าน event ใหม่
3. ตั้งชื่อ consumer ให้แต่ละ worker ไม่ชนกัน
4. ACK message หลังประมวลผลสำเร็จ
5. ตรวจ pending และ lag ของ group
6. แปลง Stream event เป็น Pub/Sub update
7. แยก data plane ออกจาก control plane
8. อธิบาย load balancing กับ fan-out ได้
9. รัน component หลายตัวตามลำดับโดยไม่ติด stale state
10. Debug ระบบที่ “ดูเหมือนค้าง” แต่จริง ๆ กำลัง block รอข้อมูล

---

## 3. คำศัพท์สำคัญ

| คำ | ความหมายแบบง่าย | ตัวอย่างใน Week 9 |
|---|---|---|
| Telemetry | ข้อมูลวัดสถานะที่ส่งต่อเนื่อง | speed, temperature, RPM |
| Producer | ผู้สร้างและส่ง event | Student 1 |
| Consumer | ผู้รับ event ไปประมวลผล | Student 2–5 |
| Redis Stream | log ของ event ที่มีลำดับและ ID | `f1:telemetry:g04` |
| Entry | หนึ่ง message ใน Stream | telemetry หนึ่ง packet |
| Stream ID | ID ที่ Redis สร้างให้ entry | เช่น `1720000000000-0` |
| Consumer Group | กลุ่ม worker ที่ช่วยกันอ่าน Stream | `f1_pitwall` |
| Consumer Name | ชื่อสมาชิกภายใน group | `engineer_pit_strategy_...` |
| Pending Entry | message ที่ส่งให้ consumer แล้วแต่ยังไม่ ACK | ตรวจด้วย `XPENDING` |
| ACK | ยืนยันว่าประมวลผล message เสร็จ | `XACK` |
| Pub/Sub | ส่งสดจาก publisher ไป subscriber ที่ออนไลน์อยู่ | dashboard channel |
| Channel | ชื่อช่อง Pub/Sub | `f1:dashboard:g04` |
| String key | key-value ธรรมดาใน Redis | `f1:race:status` |
| Namespace | prefix ที่ช่วยแยกข้อมูลแต่ละระบบ/กลุ่ม | `f1:*` |
| Throughput | จำนวน event ที่จัดการต่อช่วงเวลา | 20 messages/second |
| Latency | เวลาจากส่งจนผู้รับเห็น/ตอบสนอง | ควรต่ำสำหรับ telemetry |
| Polling | ตรวจสถานะซ้ำเป็นระยะ | producer อ่าน race status |
| Blocking read | รอข้อมูลโดยไม่วนยิง request ถี่ตลอด | `block=1000` |
| Load balancing | message หนึ่งถูกมอบให้ consumer หนึ่งตัวใน group | โค้ดปัจจุบัน Student 2–5 |
| Fan-out | ผู้รับแต่ละบทบาทเห็นสำเนาของทุก event | ต้องใช้ group แยกต่อบทบาท |
| Backlog/Lag | event ใหม่ที่ group ยังไม่ได้ส่งให้ consumer | `XINFO GROUPS` |
| At-least-once | message อาจถูกประมวลผลซ้ำได้เมื่อ retry/reclaim | ต้องออกแบบ recovery เพิ่ม |
| Idempotent | ทำซ้ำแล้วไม่สร้างผลเสียซ้ำ | สำคัญเมื่อ reclaim pending |

---

## 4. สถาปัตยกรรมภาพใหญ่

### 4.1 แบ่งเป็น Control Plane และ Data Plane

```text
CONTROL PLANE
Teacher/Operator
      |
      | SET f1:race:status STOPPED/GREEN
      v
Redis String Key
      |
      v
Student 1 waits before producing

DATA PLANE
Student 1
      |
      | XADD telemetry fields
      v
Redis Stream
      |
      | XREADGROUP + XACK
      v
Student 2/3/4/5 worker pool
      |
      | Student 5 only: PUBLISH JSON
      v
Redis Pub/Sub
      |
      +--> dashboard_listener.py
      +--> teacher_race_control.py

FINISH SIGNAL
Student 1 -- PUBLISH group_id --> f1:race:finish
```

### 4.2 ทำไมแยกช่องทาง

- `f1:race:status` ต้องอ่านค่าล่าสุดเมื่อ producer เปิดทีหลัง จึงใช้ String key
- telemetry ต้องเก็บ entry และมี Consumer Group/ACK จึงใช้ Stream
- dashboard ต้องการข้อมูลสดล่าสุดและไม่เน้น replay จึงใช้ Pub/Sub
- finish signal เป็น notification สด จึงใช้ Pub/Sub เช่นกัน

นี่คือตัวอย่างการเลือก data structure ให้ตรง semantics ไม่ได้ใช้ Redis แบบเดียวกับทุกงาน

---

# Part B — Redis Data Model

## 5. Redis data type ทั้งสามแบบที่ใช้

### 5.1 String — เก็บสถานะการแข่งขัน

```text
Key:   f1:race:status
Value: STOPPED หรือ GREEN
```

คำสั่งเชิงแนวคิด:

```bash
SET f1:race:status STOPPED
GET f1:race:status
SET f1:race:status GREEN
```

String มีค่าล่าสุดเพียงค่าเดียว ผู้เปิดโปรแกรมทีหลังยังอ่านค่าได้

### 5.2 Stream — เก็บ telemetry entries

```text
Key: f1:telemetry:g04

ID-1 -> speed, engine_temp, tire_wear, rpm, gear, distance, timestamp
ID-2 -> speed, engine_temp, tire_wear, rpm, gear, distance, timestamp
ID-3 -> ...
```

คุณสมบัติสำคัญ:

- entry มีลำดับ
- entry มี ID
- เก็บอยู่จนถูก trim/delete
- Consumer Group ติดตามการส่งและ ACK ได้
- เปิด consumer หลัง message ถูกสร้างแล้วอาจอ่านย้อนหลังได้ ขึ้นกับ group position และ read ID

### 5.3 Pub/Sub — ส่ง dashboard แบบสด

```text
Channel: f1:dashboard:g04
Payload: JSON string
```

คุณสมบัติสำคัญ:

- subscriber ที่ออนไลน์ได้รับ message
- subscriber ที่ยังไม่เปิดจะไม่ได้ message เก่า
- ไม่มี ACK และ pending list
- เหมาะกับ UI ที่สนใจข้อมูลสด
- ไม่ควรใช้แทน durable job queue เมื่อต้องรับประกันงานไม่หาย

### 5.4 เปรียบเทียบ

| ประเด็น | String | Stream | Pub/Sub |
|---|---|---|---|
| เก็บค่าหลังส่ง | เก็บค่าล่าสุด | เก็บ entries | ไม่เก็บเพื่อ replay |
| มีลำดับ event | ไม่ใช่ log | มี | เฉพาะลำดับสดที่รับทัน |
| Consumer Group | ไม่มี | มี | ไม่มี |
| ACK/Pending | ไม่มี | มี | ไม่มี |
| ผู้เปิดทีหลัง | อ่านค่าปัจจุบัน | อาจอ่านตาม group/read position | พลาดอดีต |
| ใช้ใน Week 9 | race status | telemetry | dashboard/finish |

---

## 6. Namespace และค่าคงที่จริง

### 6.1 ค่าฝั่ง Student ปัจจุบัน

| ค่า | ค่าจริง |
|---|---|
| `REDIS_HOST` | `'172.16.46.79'` |
| `GROUP_ID` | `'g04'` |
| `STUDENT_ID` | `'6710301033'` |
| Redis port | `6379` |
| Redis database | `0` |
| `STREAM_KEY` | `f1:telemetry:g04` |
| `GROUP_NAME` | `f1_pitwall` |
| `PUBSUB_CHANNEL` | `f1:dashboard:g04` |
| race status key | `f1:race:status` |
| finish channel | `f1:race:finish` |
| finish distance | `10000.0` เมตร |

ค่าข้างต้นถูก hard-code อยู่ใน source ปัจจุบัน ไม่ได้อ่านจาก `.env`

### 6.2 ค่าฝั่ง Teacher

| ค่า | ค่าจริง |
|---|---|
| `REDIS_HOST` | `'localhost'` |
| `TOTAL_GROUPS` | `8` |
| groups | `g01` ถึง `g08` |
| `FINISH_DISTANCE` | `10000.0` |
| dashboard pattern | `f1:dashboard:*` |

### 6.3 ทำไม Namespace สำคัญ

ถ้าทุกกลุ่มเขียน key ชื่อ `telemetry` เดียวกัน:

```text
g01 ----+
g02 ----+--> telemetry  # ข้อมูลชนกัน
```

เมื่อใส่ group ID:

```text
g01 -> f1:telemetry:g01
g02 -> f1:telemetry:g02
g03 -> f1:telemetry:g03
...
```

แต่ race status และ finish channelตั้งใจเป็น shared namespace กลาง:

```text
f1:race:status
f1:race:finish
```

---

## 7. Telemetry schema

Student 1 สร้าง payload หนึ่ง packet ดังนี้:

| Field | Python type ก่อนส่ง | ช่วง/ที่มา | ความหมาย |
|---|---|---|---|
| `timestamp` | float | `time.time()` | Unix timestamp |
| `speed` | float | triangular 180–330, mode 300 | km/h |
| `engine_temp` | float | uniform 90–125 | °C |
| `tire_wear` | float | uniform 5–95 | % |
| `rpm` | int | 10000–15000 | รอบ/นาที |
| `gear` | int | 3–8 | เกียร์ |
| `distance` | float | สะสมและปัด 2 ตำแหน่ง | เมตร |

Redis Stream เก็บ field/value ในรูปแบบที่ client อ่านกลับเป็น string เมื่อใช้:

```python
decode_responses=True
```

ดังนั้น consumer ต้องแปลงชนิด:

```python
speed = float(data['speed'])
rpm = int(data['rpm'])
```

ถ้า field หาย:

- Student 2–4 ใช้ `data['field']` จึงเกิด `KeyError`
- Student 5 ใช้ `data.get(..., default)` จึงมี fallback

---

## 8. Redis Stream ID

`XADD` คืน `msg_id` ที่มีรูปแบบโดยทั่วไป:

```text
<milliseconds-time>-<sequence>
```

ตัวอย่างรูปแบบ:

```text
1720000000000-0
1720000000000-1
1720000000001-0
```

ส่วนแรกมักสัมพันธ์กับเวลาเป็น millisecond ส่วนหลังแยกหลาย entry ที่เกิดใน millisecond เดียวกัน

ในโค้ด:

```python
msg_id = await r.xadd(...)
```

ID ใช้เพื่อ:

- ระบุ telemetry packet
- ACK message ที่ถูกต้อง
- แสดงบน dashboard
- ตรวจ pending entries
- debug ลำดับ event

อย่าสับสน Stream ID กับ `timestamp` ใน payload:

```text
Stream ID  = Redis กำหนดลำดับ entry
 timestamp = Producer ใส่เป็น telemetry field
```

---

# Part C — Student 1: Producer

## 9. Producer และอัตรา 20 Hz

ค่าจริง:

```python
dt = 0.05
```

อัตราที่ตั้งใจ:

```text
1 / 0.05 = 20 รอบต่อวินาที = 20 Hz
```

แต่การเขียนแบบนี้:

```python
await r.xadd(...)
await asyncio.sleep(0.05)
```

จะทำให้หนึ่งรอบกินเวลา:

```text
เวลา XADD + เวลาโค้ด + 0.05 วินาที
```

จึงต่ำกว่า 20 Hz เมื่อมี overhead

โค้ดปัจจุบันชดเชยด้วย monotonic schedule:

```text
กำหนดเวลาที่รอบถัดไปควรเริ่ม
-
หักเวลาที่ใช้ทำ XADD และงานอื่น
=
เวลาที่เหลือสำหรับ sleep
```

---

## 10. การคำนวณระยะทางและเวลาจบโดยประมาณ

สูตรในโค้ด:

```text
speed_mps = speed_kmh × 1000 / 3600
distance_delta = speed_mps × 0.05
```

ตัวอย่างที่ 270 km/h:

```text
270 × 1000 / 3600 = 75 m/s
75 × 0.05 = 3.75 m ต่อ packet
```

`random.triangular(180, 330, 300)` มีค่าเฉลี่ยเชิงทฤษฎี:

```text
(180 + 330 + 300) / 3 = 270 km/h
```

เมื่อใช้ค่าเฉลี่ยนี้:

```text
10,000 / 75 ≈ 133.33 วินาที
จำนวน packet ≈ 133.33 × 20 ≈ 2,667 packets
```

ขอบเขตหยาบหากความเร็วคงที่ตลอด:

| ความเร็ว | เวลา 10,000 m โดยประมาณ |
|---:|---:|
| 330 km/h | 109.09 s |
| 270 km/h | 133.33 s |
| 180 km/h | 200.00 s |

การแข่งขันจริงสุ่มทุก packet จึงไม่คงที่ และเวลา network/scheduler เพิ่ม overhead

ถ้ามี 8 กลุ่มที่ 20 Hz พร้อมกัน:

```text
8 × 20 = 160 telemetry messages/second
```

นี่เป็นเฉพาะ producer telemetry ยังไม่รวม Redis reads, ACKs และ Pub/Sub

---

## 11. `student1_telemetry_producer.py` แบบทีละส่วน

### 11.1 Imports

```python
import asyncio
import random
import time
import json
import redis.asyncio as redis
```

- `asyncio` — event loop และ non-blocking sleep
- `random` — สุ่ม sensor values
- `time.time()` — timestamp ใน payload
- `time.monotonic()` — scheduling interval
- `json` — encode finish signal
- `redis.asyncio` — Redis client แบบ async

### 11.2 รอ GREEN ก่อนสร้างข้อมูล

```python
await wait_for_new_green_light(r)
```

Telemetry ยังไม่เริ่มจนฟังก์ชันนี้ return

### 11.3 State ภายใน producer

```python
total_distance_m = 0.0
dt = 0.05
next_tick = time.monotonic()
packet_count = 0
```

- `total_distance_m` สะสมระยะทางใน process นี้
- `dt` เป็น simulation step และ target interval
- `next_tick` เป็น target clock ของรอบถัดไป
- `packet_count` ใช้ลดความถี่ของ log

### 11.4 สุ่มความเร็วแบบ triangular

```python
random.triangular(180.0, 330.0, 300.0)
```

ต่างจาก uniform เพราะค่าใกล้ mode `300` มีแนวโน้มมากกว่า ค่า 180 และ 330 ยังเป็นขอบเขต

### 11.5 ส่ง Stream

```python
await r.xadd(
    STREAM_KEY,
    payload,
    maxlen=1000,
    approximate=True
)
```

ความหมาย:

- append entry ใหม่
- จำกัด Stream โดยประมาณราว 1,000 entries
- Redis สามารถ trim เป็นช่วงเพื่อประสิทธิภาพ ไม่รับประกันเท่ากับ 1,000 พอดี

### 11.6 ลด terminal overhead

```python
if packet_count % 20 == 0:
    print(...)
```

ข้อมูลยังถูกส่งทุก packet แต่พิมพ์ประมาณทุก 20 packet หรือราวหนึ่งครั้ง/วินาที

การ print 20 ครั้ง/วินาทีอาจเพิ่ม overhead และทำให้ timing แย่ โดยเฉพาะ terminal ช้า

### 11.7 เช็กเส้นชัย

หลัง XADD แล้วจึงตรวจ:

```python
if total_distance_m >= FINISH_DISTANCE:
```

packet ที่ทำให้ระยะถึง/เกิน 10,000 เมตรจึงถูกส่งเข้า Stream ก่อน break

จากนั้น publish:

```json
{"group_id": "g04"}
```

ไป channel:

```text
f1:race:finish
```

### 11.8 การจัดเวลา

```python
next_tick += dt
sleep_time = next_tick - time.monotonic()
```

กรณีทำงานทัน:

```python
if sleep_time > 0:
    await asyncio.sleep(sleep_time)
```

กรณีช้ากว่า schedule:

```python
else:
    next_tick = time.monotonic()
```

การ reset ป้องกันไม่ให้ loop พยายาม “ไล่หนี้เวลา” ด้วยการวิ่งหลายรอบติดกันโดยไม่พัก

---

## 12. Race Start Barrier

ฟังก์ชัน `wait_for_new_green_light()` ป้องกัน producer ออกตัวจาก GREEN เก่าที่ค้างจากการแข่งขันก่อนหน้า

### 12.1 กรณีเปิดมาแล้วพบ `GREEN`

```text
Producer เปิด
   |
GET status -> GREEN
   |
ถือว่าอาจเป็น GREEN เก่าจากรอบก่อน
   |
รอจน status != GREEN
```

### 12.2 หลังเห็น reset แล้ว

```text
status = STOPPED/RED/อื่นที่ไม่ใช่ GREEN
   |
พิมพ์ Ready on Grid
   |
poll ทุก 0.05s
   |
พบ GREEN -> เริ่มแข่ง
```

### 12.3 เหตุผลที่ลำดับในใบงานเดิมมีปัญหา

ใบงานบอกโดยสรุปให้ set `GREEN` แล้วค่อยเปิด producer แต่ producer ปัจจุบันตีความ GREEN ที่มีอยู่ก่อนเปิดว่าเป็น stale state และจะรอให้ reset ก่อน

ดังนั้นลำดับที่ถูกกับ **โค้ดปัจจุบัน** คือ:

```text
1. SET STOPPED
2. เปิด worker/dashboard
3. เปิด producer ให้ขึ้น Ready on Grid
4. SET GREEN
```

ไม่ใช่:

```text
SET GREEN -> เปิด producer
```

เพราะแบบหลัง producer จะรอ transition:

```text
GREEN -> non-GREEN -> GREEN
```

---

## 13. `XADD` และการ trim Stream

`maxlen=1000, approximate=True` ควบคุมหน่วยความจำและความยาว log

ที่ 20 Hz:

```text
1000 / 20 = ประมาณ 50 วินาทีของ telemetry ต่อกลุ่ม
```

แต่การแข่งขันคาดราว 133 วินาทีที่ความเร็วเฉลี่ยเชิงทฤษฎี ดังนั้น Stream ไม่ได้เก็บประวัติการแข่งขันครบตั้งแต่ต้นตลอดเวลา

ผลที่ต้องเข้าใจ:

- dashboard สดยังทำงานได้ถ้าอ่านทัน
- consumer ที่ lag มากอาจพบ entry เก่าถูก trim
- post-race analysis จาก Stream อาจเห็นเฉพาะช่วงท้าย
- approximate trim อาจเหลือมากกว่า target ชั่วคราว

ถ้าต้องการเก็บทั้ง race ต้องออกแบบ retention ใหม่โดยพิจารณา:

- expected duration
- events/second
- จำนวนกลุ่ม
- ขนาดแต่ละ entry
- memory budget
- recovery lag

คู่มือนี้ไม่แก้ค่า source เพราะต้องอธิบายโค้ดที่มีอยู่

---

# Part D — Consumer Groups

## 14. Consumer Group model

ทั้ง Student 2–5 ใช้:

```python
GROUP_NAME = "f1_pitwall"
```

แต่มี `CONSUMER_NAME` ต่างกัน

มองเป็น worker pool:

```text
Redis Stream
     |
Consumer Group: f1_pitwall
     |
     +--> pit strategy consumer
     +--> safety consumer
     +--> DRS consumer
     +--> dashboard consumer
```

**กฎสำคัญ:** ภายใน Consumer Group เดียวกัน entry ใหม่หนึ่ง entry จะถูกส่งให้ consumer สมาชิกหนึ่งตัว ไม่ได้ broadcast ให้ทุกตัว

Consumer Group เหมาะกับ:

- แบ่ง workload
- scale worker งานชนิดเดียวกัน
- track pending/ACK
- ไม่ให้ worker ใน group ประมวลผล entry เดียวกันซ้ำโดยปกติ

แต่ถ้าแต่ละ consumer ทำ “คนละหน้าที่” และทุกหน้าที่ต้องเห็นทุก packet การใช้ group เดียวไม่ตรง fan-out semantics

---

## 15. `$`, `>` และความหมายที่ต้องจำ

### 15.1 ตอนสร้าง Group ใช้ `$`

```python
await r.xgroup_create(
    STREAM_KEY,
    GROUP_NAME,
    id="$",
    mkstream=True
)
```

`$` หมายถึงตั้งจุดเริ่มของ group ที่ท้าย Stream ณ เวลาสร้าง

ผล:

- entry ที่มีอยู่ก่อน group ถูกสร้างจะไม่ถูกส่งเป็น “new message” ให้ group นี้
- entry ที่เกิดหลังจากนั้นจึงเป็นงานใหม่
- ถ้า Stream ยังไม่มี `mkstream=True` จะสร้าง Stream ว่างให้

### 15.2 ตอนอ่านใช้ `>`

```python
{STREAM_KEY: '>'}
```

`>` ใน `XREADGROUP` หมายถึงขอ entry ใหม่ที่ยังไม่เคยมอบให้ consumer ใดใน group

ไม่ได้หมายถึง:

- อ่านทุก entry ตั้งแต่ต้น
- อ่าน pending ของ consumer นี้ซ้ำ
- reclaim pending จาก consumer ที่ตาย

### 15.3 จำเป็นประโยค

```text
$ ตอน create group = เริ่มจากท้าย ณ ตอนสร้าง
> ตอน read group   = ขอ message ใหม่สำหรับ group
```

---

## 16. Pending Entries และ `XACK`

Flow ของ message ใน group:

```text
Stream entry ใหม่
      |
      | XREADGROUP
      v
ถูกส่งให้ consumer
      |
      v
Pending Entries List (PEL)
      |
      | ประมวลผลสำเร็จ + XACK
      v
ออกจาก pending
```

ทุก worker เรียก:

```python
await r.xack(STREAM_KEY, GROUP_NAME, msg_id)
```

### 16.1 ถ้า process ล้มก่อน ACK

message ยังอยู่ใน pending ของ consumer เดิม

แต่โค้ดปัจจุบันอ่านด้วย `>` อย่างเดียวและไม่มี:

- read pending history
- `XAUTOCLAIM`
- `XCLAIM`
- retry count
- dead-letter stream

ดังนั้น message pending อาจค้างโดยไม่มี worker มารับต่อ

### 16.2 Processing guarantee

Stream + Consumer Group สามารถสร้าง at-least-once processing ได้เมื่อมี recovery/reclaim ที่ถูกต้อง แต่โค้ดปัจจุบันยังเป็น classroom skeleton ที่ไม่มี recovery path ครบ

ถ้าเพิ่ม reclaim ภายหลัง handler ควร idempotent เพราะ message อาจถูกทำซ้ำ

### 16.3 ACK เวลาใด

หลักทั่วไป:

```text
อ่าน -> validate/parse -> ทำ side effect ให้สำเร็จ -> ACK
```

ถ้า ACK ก่อน side effect แล้ว process ล้ม งานอาจหายทางตรรกะ

---

# Part E — Student 2–5 Workers

## 17. `student2_pit_strategy_engineer.py`

### 17.1 ตัวตน

```text
Role: Pit Strategy Engineer
Consumer: engineer_pit_strategy_6710301033
Group: f1_pitwall
```

### 17.2 Threshold

| เงื่อนไข | ผลที่คาด |
|---|---|
| `tire_wear > 75.0` | `BOX BOX BOX!` critical warning |
| `50.0 < tire_wear <= 75.0` | เตรียม Soft Compound |
| `tire_wear <= 50.0` | ไม่พิมพ์ alert |

ค่าพอดี `75.0` ไม่เข้า critical เพราะใช้ `>` ไม่ใช่ `>=`

ค่าพอดี `50.0` ไม่เข้า warning เช่นกัน

### 17.3 Flow

```text
init_group
  -> Ready
  -> XREADGROUP count=1 block=1000
  -> parse tire_wear
  -> threshold check
  -> XACK
  -> sleep 0.01
  -> loop
```

`block=1000` ทำให้ Redis read รอได้สูงสุดประมาณ 1,000 ms เมื่อไม่มีข้อมูล แล้วคืนผลว่างเพื่อวนใหม่

### 17.4 Error behavior

Exception ถูกจับและพิมพ์ `Error: ...` จากนั้น sleep และ retry

ถ้า exception เกิดหลังรับ message แต่ก่อน ACK entry จะค้าง pending

---

## 18. `student3_race_control_engine_safety.py`

### 18.1 ตัวตน

```text
Role: Engine Safety Monitor
Consumer: engineer_safety_alert_6710301033
Group: f1_pitwall
```

### 18.2 Threshold

| Field | เงื่อนไข | Alert |
|---|---|---|
| `engine_temp` | `> 115.0` | Overheating / Reduce Power |
| `rpm` | `> 14500` | Over-revving / Shift Up |

ใช้ `if` สองตัวแยกกัน ดังนั้น packet เดียวสามารถพิมพ์ทั้งสอง alert

### 18.3 Current-code detail

ไฟล์ประกาศ:

```python
STUDENT_ID = '6710301033'
```

แต่ `CONSUMER_NAME` เขียน ID ตรง ๆ:

```python
CONSUMER_NAME = f"engineer_safety_alert_{6710301033}"
```

จึงได้ string ที่ถูกสำหรับค่าปัจจุบัน แต่ถ้าเปลี่ยน `STUDENT_ID` เพียงบรรทัดเดียว consumer name จะไม่เปลี่ยนตาม

นี่เป็น **configuration consistency caveat** ไม่ใช่ syntax error

### 18.4 Boundary cases

```text
engine_temp = 115.0 -> ไม่ alert
engine_temp = 115.1 -> alert
rpm = 14500         -> ไม่ alert
rpm = 14501         -> alert
```

---

## 19. `student4_DRS_automation_controller.py`

### 19.1 ตัวตน

```text
Role: DRS Controller
Consumer: engineer_drs_controller_6710301033
Group: f1_pitwall
```

### 19.2 เงื่อนไข DRS

```python
speed > 250.0 and gear >= 7
```

ต้องผ่านทั้งสองเงื่อนไข

| Speed | Gear | Result |
|---:|---:|---|
| 251 | 7 | ENABLED |
| 251 | 6 | Disabled |
| 250 | 8 | Disabled |
| 300 | 8 | ENABLED |

### 19.3 Log volume

ไฟล์นี้พิมพ์ทั้งกรณี enabled และ disabled ทุก packet ที่ตนได้รับ จึงสร้าง terminal output มากกว่า worker ที่พิมพ์เฉพาะ alert

แต่เพราะ shared Consumer Group ไฟล์นี้ไม่ได้รับทุก producer packet ในโค้ดปัจจุบัน

---

## 20. `student5_dashboard_broadcaster.py`

### 20.1 บทบาท

Student 5 เป็น adapter ระหว่างสอง communication models:

```text
Redis Stream entry
   -> parse/normalize
   -> JSON encode
   -> Redis Pub/Sub publish
   -> XACK Stream entry
```

### 20.2 Dashboard packet schema

```json
{
  "speed": 287.4,
  "gear": "7",
  "rpm": 14320,
  "distance": 5432.1,
  "stream_id": "..."
}
```

ชนิดหลัง `json.loads()` ที่ปลายทาง:

| Field | Type โดยตั้งใจ |
|---|---|
| `speed` | number/float |
| `gear` | string จาก Stream หรือ `"-"` |
| `rpm` | integer |
| `distance` | number/float |
| `stream_id` | string |

### 20.3 Fallback

Student 5 ใช้ `data.get()`:

```text
speed missing    -> 0.0
gear missing     -> '-'
rpm missing      -> 0
distance missing -> 0.0
```

ช่วยไม่ให้ `KeyError` แต่ข้อมูลผิด schema อาจถูกแสดงเป็นศูนย์แทนที่จะถูกปฏิเสธ

### 20.4 Publish ก่อน ACK

ลำดับปัจจุบัน:

```text
PUBLISH dashboard
XACK stream
print log
```

ถ้า publish สำเร็จแต่ process ล้มก่อน ACK และมี recovery ในอนาคต packet อาจถูก publish ซ้ำ นี่คือเหตุผลที่ dashboard ควรทน duplicate ได้

---

## 21. Stream-to-Pub/Sub bridge

ทำไมไม่ให้ dashboard อ่าน Stream ตรง ๆ เสมอ:

- Stream เหมาะกับ durable processing/worker coordination
- Pub/Sub เหมาะกับ live subscribers หลายจอ
- adapter สามารถเลือก field และเปลี่ยน schema
- UI ไม่ต้องจัดการ group, pending และ ACK

แต่ bridge ปัจจุบันมีข้อจำกัด:

```text
Student 5 อยู่ group เดียวกับ Student 2–4
```

จึงได้รับเพียงบาง Stream entries และ publish เฉพาะ subset นั้น Dashboard ไม่ได้รับ telemetry ทุก packet

ถ้าต้องการ dashboard ทุก packet Student 5 ควรอยู่ consumer group ของ dashboard เอง เช่น:

```text
f1_pit_strategy
f1_engine_safety
f1_drs_controller
f1_dashboard
```

นี่เป็นแนวออกแบบ ไม่ใช่สิ่งที่ source ปัจจุบันทำ

---

# Part F — Dashboard และ Race Control

## 22. `dashboard_listener.py`

### 22.1 Subscription

```python
await pubsub.subscribe(PUBSUB_CHANNEL)
```

ค่าปัจจุบัน:

```text
f1:dashboard:g04
```

### 22.2 Initial state

ก่อนมี message UI ใช้:

```json
{
  "speed": 0,
  "gear": 1,
  "rpm": 0,
  "distance": 0.0,
  "stream_id": "Waiting..."
}
```

### 22.3 Race progress

```text
dist_pct = min(100, distance / 10000 × 100)
```

progress bar ยาว 30 ตัวอักษร

`min(100.0, ...)` ป้องกัน bar ยาวเกิน 100% เมื่อ packet สุดท้ายมีระยะเกิน 10,000 เล็กน้อย

### 22.4 Speed gauge

ใช้ 350 km/h เป็น scale สูงสุดเชิงภาพ:

```text
speed_bar_len = int(speed / 350 × 30)
```

สี:

| Speed | Color |
|---:|---|
| `< 250` | bright green |
| `250–<300` | bright yellow |
| `>= 300` | bright red |

### 22.5 Live rendering

`rich.live.Live` refresh ได้สูงสุด 10 ครั้ง/วินาที แต่ update เกิดเมื่อได้รับ Pub/Sub message

ถ้า redirect output ไปไฟล์ Rich Live อาจไม่บันทึกทุก frame เหมือนหน้าจอ interactive

---

## 23. `teacher_race_control.py`

### 23.1 หน้าที่สองด้าน

1. Controller — reset และปล่อย GREEN
2. Observer — รับ dashboard ของทุกกลุ่มและ finish events

### 23.2 Pattern subscription

```python
await pubsub.psubscribe(
    "f1:dashboard:*",
    "f1:race:finish"
)
```

โค้ดตรวจ message type เป็น `pmessage` เพราะใช้ pattern subscription

### 23.3 Race state ใน memory

```python
race_data = {
    "g01": {"distance": 0.0, "speed": 0.0, "finished": False},
    ...,
    "g08": {...}
}
```

และ:

```python
leaderboard = []
```

`race_data` เก็บ live snapshot ส่วน `leaderboard` เก็บลำดับ finish

### 23.4 Reset

ทุก loop ก่อนรอ Enter:

```python
await r.set("f1:race:status", "STOPPED")
reset_race_state()
```

จึงสร้าง transition ที่ producer ต้องการ

### 23.5 Start sequence

```text
กด Enter
  -> 3
  -> 2
  -> 1
  -> SET GREEN
  -> Live leaderboard
```

### 23.6 Subscribe ก่อน reset/start

`listen_to_pubsub()` ถูกสร้างเป็น background task ก่อนเข้า race loop จึงพร้อมรับ telemetry/finish ระหว่างการแข่งขัน

---

## 24. การเรียงอันดับและเส้นชัย

### 24.1 ระหว่างแข่ง

กลุ่มถูก sort ตาม distance จากมากไปน้อย:

```python
sorted(
    race_data.items(),
    key=lambda x: x[1]['distance'],
    reverse=True
)
```

rank ระหว่างแข่งคืออันดับจาก snapshot ล่าสุด ไม่ใช่ finish order

### 24.2 เมื่อ finish

เมื่อ channel `f1:race:finish` ส่ง group ID:

```text
ถ้ายังไม่ marked finished
  -> finished = True
  -> append group_id ลง leaderboard
```

ลำดับใน `leaderboard` จึงขึ้นกับลำดับ finish messages ที่ Race Control รับ

### 24.3 Duplicate finish signal

มี guard:

```python
not race_data[gid]['finished']
```

จึงไม่ append กลุ่มเดิมซ้ำ

### 24.4 Unknown group

ถ้า payload มี group ที่ไม่อยู่ g01–g08 จะไม่ update เพราะตรวจ `gid in race_data`

---

# Part G — ประเด็น Consumer Group ที่ต้องเข้าใจที่สุด

## 25. Shared Consumer Group: ประเด็นใหญ่ที่สุด

Student 2, 3, 4 และ 5 ใช้พร้อมกัน:

```text
GROUP_NAME = f1_pitwall
STREAM_KEY = f1:telemetry:g04
```

Redis จึงมองทั้งหมดเป็นสมาชิกของ worker group เดียว

สมมติมี entries A–H:

```text
A -> Student 2
B -> Student 3
C -> Student 4
D -> Student 5
E -> Student 2
F -> Student 3
G -> Student 4
H -> Student 5
```

การแบ่งจริงไม่จำเป็นต้อง round-robin เป๊ะ ขึ้นกับเวลาที่แต่ละ consumer block/read และ scheduler

ผลทางธุรกิจ:

- Pit Strategy ตรวจเฉพาะ subset ของ tire data
- Engine Safety ตรวจเฉพาะ subset ของ engine data
- DRS ตรวจเฉพาะ subset ของ speed/gear
- Dashboard ส่งต่อเฉพาะ subset

จึงอาจพลาด critical packet ที่ถูกส่งให้บทบาทอื่น

---

## 26. Load balancing vs fan-out

### 26.1 Load balancing

```text
                shared group
Entry 1 ----------------------> Worker A เท่านั้น
Entry 2 ----------------------> Worker B เท่านั้น
Entry 3 ----------------------> Worker C เท่านั้น
```

เหมาะเมื่อ worker ทำหน้าที่ชนิดเดียวกัน เช่น image processors 4 ตัว

### 26.2 Fan-out

```text
Entry 1 -> Pit Strategy
        -> Engine Safety
        -> DRS
        -> Dashboard
```

เหมาะเมื่อแต่ละ role วิเคราะห์คนละมิติและต้องเห็น event เดียวกันทั้งหมด

### 26.3 สรุปจากโจทย์นี้

ข้อความในใบงานสื่อว่าทุกระบบย่อยวิเคราะห์ telemetry ตามหน้าที่ของตน ซึ่งมีลักษณะ fan-out แต่ implementation ปัจจุบันกำหนด shared group จึงให้ load balancing

คู่มือนี้บันทึกความต่างอย่างตรงไปตรงมาและ **ไม่แก้ source โดยพลการ**

---

## 27. วิธีออกแบบ fan-out หากโจทย์ต้องการทุกบทบาทเห็นทุก packet

แนวทางหนึ่งคือ group แยกต่อ role:

```text
Stream: f1:telemetry:g04

Group: f1_pit_strategy
  Consumer: engineer_pit_strategy_6710301033

Group: f1_engine_safety
  Consumer: engineer_safety_alert_6710301033

Group: f1_drs
  Consumer: engineer_drs_controller_6710301033

Group: f1_dashboard
  Consumer: engineer_dashboard_6710301033
```

แต่ละ group มี cursor/pending แยกกัน จึงเห็นทุก entry หนึ่งครั้งต่อ group

Trade-offs:

| ประเด็น | Shared group | Group แยก role |
|---|---|---|
| งานต่อ entry รวม | 1 role | ทุก role |
| Load | ต่ำกว่า | สูงกว่า |
| ทุก role เห็น packet | ไม่ | ใช่ |
| Pending tracking | ชุดเดียว | แยก role |
| เหมาะกับ | worker pool | event fan-out |

อีกแนวทางคือ consumer อ่าน Stream แบบไม่ใช้ group แต่ต้องจัดการ offset เอง หรือแยก Streams/ใช้ message broker design อื่น

---

# Part H — End-to-End Flow

## 28. End-to-end data journey

### 28.1 ตั้งแต่ STOPPED ถึง GREEN

```text
Race Control SET STOPPED
       |
Producer GET -> STOPPED
       |
Producer enters Ready on Grid loop
       |
Race Control countdown
       |
Race Control SET GREEN
       |
Producer detects GREEN
```

### 28.2 หนึ่ง telemetry packet

```text
1. Producer สุ่ม speed/temp/wear/rpm/gear
2. คำนวณ distance_delta
3. เพิ่ม total_distance
4. XADD เข้า f1:telemetry:g04
5. Redis กำหนด Stream ID
6. Consumer หนึ่งตัวใน f1_pitwall ได้ packet
7. Consumer ประมวลผล
8. Consumer XACK
9. ถ้าผู้รับคือ Student 5:
      - แปลงเป็น dashboard JSON
      - PUBLISH f1:dashboard:g04
10. dashboard subscribers ที่ออนไลน์รับข้อมูล
```

### 28.3 Finish

```text
Producer XADD final packet
       |
distance >= 10000
       |
PUBLISH f1:race:finish {group_id:g04}
       |
Teacher marks finished + appends leaderboard
       |
Producer exits loop
```

Student 2–5 และ dashboards ยังคงเป็น long-running processes ไม่หยุดอัตโนมัติเมื่อ producer จบ

---

## 29. ลำดับรันที่ถูกต้องสำหรับ Local Practice

ลำดับที่ปลอดภัยกับ producer ปัจจุบัน:

```text
1. เปิด Redis
2. ตรวจ PING
3. SET f1:race:status STOPPED
4. ปรับ REDIS_HOST ของ client ทุกไฟล์ให้ตรง Redis
5. เปิด Student 2, 3, 4, 5
6. เปิด dashboard_listener.py
7. ยืนยันทุกตัวขึ้น Ready/Subscribed
8. เปิด Student 1
9. ยืนยัน Student 1 ขึ้น Ready on Grid
10. SET f1:race:status GREEN
11. สังเกต pipeline จน producer finish
12. ตรวจ Stream/group/pending/lag
13. หยุด long-running processes
14. SET STOPPED สำหรับรอบถัดไป
```

ถ้าใช้ `teacher_race_control.py`:

```text
1. เปิด Teacher Race Control ก่อน
2. Teacher ตั้ง STOPPED ใน loop
3. เปิด workers/listener/producer
4. กด Enter ที่ Teacher
5. Teacher countdown และ SET GREEN
```

---

# Part I — Setup และคำสั่งรัน

## 30. การติดตั้ง dependency

`asyncio`, `json`, `random` และ `time` เป็น standard library ไม่ต้อง `pip install asyncio`

package ภายนอกที่ source ใช้:

```bash
python -m pip install redis rich
```

ตรวจ import:

```bash
python -c "import redis.asyncio; import rich; print('dependencies ok')"
```

แนะนำให้ใช้ virtual environment ของ project ตาม environment ที่เรียนกำหนด

---

## 31. การเปิด Redis ด้วย Docker Compose

จาก repo root:

```bash
docker compose -f Week9/docker-compose.yaml up -d
```

ตรวจ container:

```bash
docker compose -f Week9/docker-compose.yaml ps
```

ตรวจ Redis:

```bash
docker exec f1-redis redis-cli PING
```

ผลที่คาด:

```text
PONG
```

ตั้ง STOPPED:

```bash
docker exec f1-redis redis-cli SET f1:race:status STOPPED
```

ตรวจ:

```bash
docker exec f1-redis redis-cli GET f1:race:status
```

ถ้าใช้ `redis-cli` ที่ติดตั้งใน host อยู่แล้ว:

```bash
redis-cli -h localhost -p 6379 PING
```

---

## 32. คำสั่งรันทุก component

### 32.1 จาก repo root

เปิดคนละ terminal:

```bash
python Week9/student2_pit_strategy_engineer.py
```

```bash
python Week9/student3_race_control_engine_safety.py
```

```bash
python Week9/student4_DRS_automation_controller.py
```

```bash
python Week9/student5_dashboard_broadcaster.py
```

```bash
python Week9/dashboard_listener.py
```

จากนั้น producer:

```bash
python Week9/student1_telemetry_producer.py
```

ปล่อย GREEN หลัง producer พร้อม:

```bash
docker exec f1-redis redis-cli SET f1:race:status GREEN
```

หรือเปิด teacher controller:

```bash
python Week9/teacher_race_control.py
```

### 32.2 จากภายใน `Week9`

```bash
cd Week9
python student2_pit_strategy_engineer.py
python student3_race_control_engine_safety.py
python student4_DRS_automation_controller.py
python student5_dashboard_broadcaster.py
python dashboard_listener.py
python student1_telemetry_producer.py
```

ต้องเปิดหลาย terminal ไม่ใช่รันทุกคำสั่งเรียงใน terminal เดียว เพราะ workers/listeners ไม่จบเอง

---

## 33. การตรวจสุขภาพ Redis และ Stream

ดูชนิด key:

```bash
docker exec f1-redis redis-cli TYPE f1:telemetry:g04
```

ดูความยาว:

```bash
docker exec f1-redis redis-cli XLEN f1:telemetry:g04
```

ดู entry ล่าสุด:

```bash
docker exec f1-redis redis-cli XREVRANGE f1:telemetry:g04 + - COUNT 1
```

ดู groups:

```bash
docker exec f1-redis redis-cli XINFO GROUPS f1:telemetry:g04
```

ดู consumers:

```bash
docker exec f1-redis redis-cli XINFO CONSUMERS f1:telemetry:g04 f1_pitwall
```

ดู status:

```bash
docker exec f1-redis redis-cli GET f1:race:status
```

---

## 34. การตรวจ Pending/Lag

```bash
docker exec f1-redis redis-cli XPENDING f1:telemetry:g04 f1_pitwall
```

สุขภาพหลัง processing สงบควรพิจารณา:

```text
pending = 0
lag = 0
```

แต่ต้องตีความ:

- pending > 0: มี entries ส่งแล้วแต่ยังไม่ ACK
- lag > 0: มี entries ใหม่ที่ group ยังไม่ได้มอบให้ consumer
- pending = 0 แต่ dashboard ไม่ขยับ: Student 5 อาจไม่ได้รับ entries เพราะถูก role อื่นแบ่งไป
- XLEN ใกล้ 1000: เป็นผลจาก `maxlen=1000` โดยประมาณ

การดู startup log อย่างเดียวไม่พิสูจน์ว่า pipeline ทำงานครบ ต้องตรวจ data boundaries ด้วย

---

## 35. Expected behavior

### 35.1 Producer

ลำดับที่คาด:

```text
Checking Race Status
Ready on Grid
LIGHTS OUT...
ส่ง telemetry และพิมพ์ทุกประมาณ 20 packet
CHEQUERED FLAG เมื่อ distance >= 10000
```

### 35.2 Workers

- Student 2 พิมพ์เฉพาะ tire warnings ที่ตนได้รับ
- Student 3 พิมพ์ temperature/RPM alerts ที่ตนได้รับ
- Student 4 พิมพ์ DRS enabled/disabled สำหรับ packet ที่ตนได้รับ
- Student 5 พิมพ์ broadcast log สำหรับ packet ที่ตนได้รับ

### 35.3 Dashboard

- subscribe แล้วรอ Student 5
- update speed/gear/RPM/distance เมื่อมี dashboard packet
- progress อาจข้ามเป็นช่วง ๆ เพราะ Student 5 ไม่ได้ทุก Stream entryใน shared group

### 35.4 Teacher dashboard

- เริ่มทุกกลุ่มที่ GRID
- update เฉพาะ group ที่มี dashboard packet
- mark finished จาก finish channel แม้ dashboard distance ล่าสุดอาจยังไม่ถึง 10,000 เพราะ final Stream packetอาจถูก role อื่นรับ

---

## 36. การหยุดและ Cleanup

หยุด Python processes ด้วย `Ctrl+C`

reset status:

```bash
docker exec f1-redis redis-cli SET f1:race:status STOPPED
```

ถ้าต้องการล้างเฉพาะข้อมูลกลุ่มเพื่อเริ่มใหม่:

```bash
docker exec f1-redis redis-cli DEL f1:telemetry:g04
```

ระวัง: การลบ Stream ลบ group ที่ผูกกับ Stream ด้วย เมื่อ worker เริ่มใหม่ `mkstream=True` จะสร้างใหม่

หลีกเลี่ยง `FLUSHDB` บน Redis ที่แชร์กับระบบอื่น เพราะลบทุก key ใน database

หยุด Redis container:

```bash
docker compose -f Week9/docker-compose.yaml down
```

สถานะที่ควรส่งมอบหลังทดสอบ:

- Python long-running processes หยุดแล้วหรือยัง
- race status เป็น STOPPED หรือไม่
- Redis container ยังรันหรือถูกปิด
- pending/lag สุดท้ายเท่าไร
- Stream ถูกเก็บหรือล้าง

---

# Part J — Configuration และข้อไม่ตรงกัน

## 37. Local vs Classroom Configuration

### 37.1 Source ปัจจุบัน

| Component | Redis host |
|---|---|
| Student 1 | `172.16.46.79` |
| Student 2 | `172.16.46.79` |
| Student 3 | `172.16.46.79` |
| Student 4 | `172.16.46.79` |
| Student 5 | `172.16.46.79` |
| Team dashboard | `172.16.46.79` |
| Teacher race control | `localhost` |

ดังนั้นการเปิด Docker Redis ที่ local ไม่ทำให้ Student scripts ชี้ local โดยอัตโนมัติ

ทุก process ที่ต้องคุยกันต้องใช้ Redis instance เดียวกัน

### 37.2 Local practice

ต้องปรับ `REDIS_HOST` ของ Student 1–5 และ dashboard listener เป็น:

```python
REDIS_HOST = 'localhost'
```

หรือใช้ IP host ที่ทุกเครื่องเข้าถึงได้

### 37.3 Classroom race

ใช้ IP เครื่องอาจารย์ที่แจ้งในห้อง และตรวจ firewall/network ก่อน

อย่าสมมติว่า IP ใน source ยังถูกทุกครั้ง เพราะ DHCP/network ห้องเรียนอาจเปลี่ยน

---

## 38. ความไม่ตรงกันระหว่างใบงานกับไฟล์จริง

ใบงานยกคำสั่งชื่อย่อ:

```text
student2_pit_strategy.py
student3_engine_safety.py
student4_drs_controller.py
```

แต่ชื่อจริงคือ:

```text
student2_pit_strategy_engineer.py
student3_race_control_engine_safety.py
student4_DRS_automation_controller.py
```

ต้องใช้ชื่อจริงบน filesystem รวมถึงตัวพิมพ์ใหญ่ `DRS`

อีกจุดคือใบงานวางขั้นตอน GREEN ก่อน producer แต่ producer ปัจจุบันต้องการ reset transition ตามที่อธิบายใน Part C

ใบงานบอก `pip install redis asyncio rich` แต่ `asyncio` เป็น standard library ของ Python สมัยใหม่ จึงไม่ต้องติดตั้งแยก

---

## 39. Docker Compose แบบละเอียด

Active configuration:

| Flag | ค่า | ผล |
|---|---|---|
| image | `redis:alpine` | Redis บน Alpine |
| container | `f1-redis` | ชื่อ container |
| restart | `always` | Docker พยายาม restart |
| port | `6379:6379` | เปิด Redis บน host |
| `--save ""` | ปิด RDB snapshots | ไม่มี snapshot persistence |
| `--appendonly no` | ปิด AOF | ไม่มี AOF persistence |
| `--maxmemory 512mb` | จำกัด memory | สูงสุด 512 MB ตาม config |
| policy | `noeviction` | เมื่อเต็ม write ใหม่อาจ error แทนลบ key |
| normal output buffer | `0 0 0` | ปิด limit สำหรับ normal clients |
| backlog | `512` | queue connection requests |
| loglevel | `notice` | log ระดับ notice |

### 39.1 Data durability

ไม่มี volume และปิด RDB/AOF ดังนั้นข้อมูลเหมาะกับ lab/real-time session แต่ไม่ใช่ durable storage

เมื่อ container ถูกลบ ข้อมูลหาย

### 39.2 Comment drift ในไฟล์

ช่วง comment ท้าย Compose กล่าวถึง:

- video stream
- 30 FPS + 40 คน
- key `teachers_stream`
- `maxmemory 128mb`
- `allkeys-lru`

แต่ active config จริงคือ:

- F1 telemetry lab
- `maxmemory 512mb`
- `noeviction`

comment ช่วงท้ายจึงดูเป็นคำอธิบายที่คัดลอกจากอีก use case และไม่ควรใช้แทน active YAML

หลักสำคัญ:

```text
ค่าที่ Redis ใช้จริง = active YAML/command
comment = เอกสารประกอบที่อาจล้าสมัย
```

---

# Part K — Current-Code Caveats

## 40. Current-code caveats แบบรวม

### 40.1 Shared group ทำให้ไม่ fan-out

เป็นข้อจำกัดด้าน semantics สำคัญที่สุด

### 40.2 Group เริ่มที่ `$`

ถ้า producer ส่งก่อน group ถูกสร้าง messages เก่าจะถูกข้ามสำหรับ new delivery

### 40.3 อ่านเฉพาะ `>`

ไม่มี recovery ของ pending message

### 40.4 Exception loop อาจหมุนซ้ำ

เมื่อ Redis เข้าไม่ได้ worker จะพิมพ์ error, sleep 0.01 แล้ว retry ทำให้ log ถี่ได้

### 40.5 Connections ไม่ได้ปิดครบทุก normal path

workers เป็น long-running อยู่แล้ว แต่ graceful shutdown/`aclose()` ไม่ได้ออกแบบครบ

Producer ปิด client เฉพาะใน `CancelledError`; เมื่อ finish ตามปกติไม่มี explicit close ใน source ปัจจุบัน

### 40.6 `CancelledError` ใน producer ถูกกิน

producer catch แล้ว close แต่ไม่ re-raise จึงเปลี่ยน cancellation semantics ของ coroutine

### 40.7 Student 3 consumer name ไม่อิงตัวแปรจริง

เปลี่ยน `STUDENT_ID` แล้วต้องระวัง hard-coded ID ใน f-string

### 40.8 ไม่มี schema validation

ค่าที่ malformed อาจเกิด conversion error และ pending ค้าง

### 40.9 ไม่มี authentication/TLS

Redis client ต่อ host/port โดยไม่มี password หรือ TLS เหมาะกับ trusted lab network มากกว่าการเปิด internet

### 40.10 Stream retention สั้นกว่าระยะ race โดยประมาณ

1000 entries ที่ 20 Hz ≈ 50 วินาที ขณะที่ race เชิงทฤษฎีเฉลี่ย ≈ 133 วินาที

### 40.11 Finish signal เป็น Pub/Sub

Teacher ที่ยังไม่ subscribe ตอน finish จะพลาด signal ไม่มี replay

### 40.12 Teacher state อยู่ใน memory

restart teacher process ทำให้ leaderboard หาย แม้ Redis Stream ยังอยู่

### 40.13 JSON parsing ไม่มี guard เฉพาะ

malformed Pub/Sub payload อาจทำให้ listener task errorและหยุด

### 40.14 ไม่มี correlation ของ race round

finish payload มีเฉพาะ `group_id` ไม่มี `race_id`; stale/delayed message อาจแยกจากรอบใหม่ไม่ได้ในระบบที่ซับซ้อนกว่า

---

## 41. Reliability และ Message Recovery

### 41.1 Failure windows

| จุดล้ม | ผลที่เป็นไปได้ |
|---|---|
| ก่อน XADD | packet ไม่เข้า Stream |
| หลัง XADD ก่อน log | packetอยู่ แม้ terminal ไม่พิมพ์ |
| หลัง XREADGROUP ก่อน process | entry pending |
| หลัง process ก่อน ACK | side effectอาจเกิดแล้ว แต่ entry pending |
| หลัง dashboard PUBLISH ก่อน ACK | UI ได้แล้ว แต่อาจ duplicate เมื่อ reclaim |
| หลัง ACK ก่อน log | งานสำเร็จ แม้ logไม่ออก |
| finish publish ตอน teacher offline | finish signalหาย |

### 41.2 Recovery ที่ production system มักเพิ่ม

- `XAUTOCLAIM` pending ที่ idle นาน
- retry counter
- dead-letter Stream
- schema validation
- idempotency keyจาก Stream ID
- monitoring pending/lag
- reconnect/backoff
- graceful shutdown
- persistent finish record นอกจาก Pub/Sub
- race/session ID

สิ่งเหล่านี้เป็นการต่อยอด ไม่ใช่สิ่งที่ source ปัจจุบัน implement แล้ว

---

## 42. Performance และ Bottleneck

### 42.1 Producer

- network round trip ของ `XADD`
- terminal print
- event-loop scheduling
- Redis load

### 42.2 Consumers

- `count=1` รับทีละ message
- แต่ละรอบมี sleep 0.01 เพิ่ม
- terminal printing อาจช้า
- shared groupแบ่ง throughput แต่เปลี่ยน semantics

### 42.3 Student 5

ทำทั้ง Stream read, JSON encode, Pub/Sub publish, ACK และ print จึงมีงานต่อ messageมากกว่า role อื่น

### 42.4 Teacher

Rich UI refresh 10 Hz และรับได้หลายกลุ่ม หากมี 8 กลุ่ม producer รวม 160 Hz แต่ Teacher เห็นเฉพาะ dashboard subset จาก Student 5

### 42.5 Scaling ที่ต้องระวัง

เพิ่ม consumer ใน group เดิมช่วย throughput งานชนิดเดียวกัน แต่ยิ่งเพิ่ม role ใน shared group ยิ่งทำให้แต่ละ roleเห็นสัดส่วนน้อยลง

---

## 43. Security และ Operational Safety

- อย่าเปิด port 6379 สู่ public internet โดยไม่มี network restriction/authentication
- `decode_responses=True` สะดวก แต่ยังต้อง validate content
- จำกัดสิทธิ์ Redis user ด้วย ACL ในระบบจริง
- ใช้ TLS เมื่อข้าม network ที่ไม่ไว้ใจ
- อย่า hard-code production credentials ใน source
- อย่าใช้ `FLUSHDB` บน shared Redis
- Namespace ลด collision แต่ไม่ใช่ access control
- `noeviction` เมื่อ memory เต็มอาจทำให้ XADD/PUBLISH ที่ต้อง allocate memory error
- ปิด persistence หมายถึงยอมรับ data loss เมื่อ restart
- ตรวจ clock/time assumptions หากใช้ timestamp ข้ามเครื่อง
- sanitize/validate group ID หากอนาคตรับจาก user input

---

# Part L — Troubleshooting

## 44. Troubleshooting Matrix

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ |
|---|---|---|
| `Connection refused` | Redisไม่รัน/hostผิด/firewall | PING host/port และเทียบ `REDIS_HOST` |
| Producer รอ reset | เปิดตอน statusเป็น GREENเก่า | SET STOPPED แล้วรอให้เห็น Ready ก่อน SET GREEN |
| Producer Ready แต่ไม่ออก | ไม่มีใคร SET GREEN หรือใช้ Redis คนละเครื่อง | GET status จาก instance เดียวกัน |
| Worker Ready แต่ไม่มี log | ไม่มี producer, groupแบ่ง message, thresholdไม่ผ่าน | XLEN/XINFO และดูผู้รับแต่ละ consumer |
| Dashboardไม่ขยับ | Student 5ไม่รันหรือไม่ได้ entry | ดู broadcaster log และ subscribe channel |
| บาง alertไม่เกิด | packetถูก consumer roleอื่นรับ | เข้าใจ shared group load balancing |
| Pendingเพิ่ม | exception/crashก่อน ACK | XPENDING/XINFO CONSUMERS |
| Lagเพิ่ม | consumersช้าหรือไม่รัน | XINFO GROUPS |
| `BUSYGROUP` | groupมีอยู่แล้ว | expected; code ignore เฉพาะ BUSYGROUP |
| `NOGROUP` | Stream/groupถูกลบหลัง init หรือชื่อไม่ตรง | ตรวจ TYPE/XINFO และ restart worker |
| conversion error | fieldหายหรือชนิดผิด | XREVRANGE ดู payloadจริง |
| Dashboard progressกระโดด | Student 5ได้เพียง subset | shared group semantics |
| Teacherไม่เห็น finish | teacher offlineตอน Pub/Sub หรือ hostไม่ตรง | เปิด subscriberก่อน race และตรวจ Redis instance |
| Streamมีแค่ช่วงท้าย | approximate maxlen trimming | XLEN และเข้าใจ 1000-entry retention |
| memoryเต็มแล้ว write error | `noeviction` | INFO memory และ Redis logs |
| คำสั่งจากใบงานหาไฟล์ไม่เจอ | filenameในใบงานสั้นกว่าของจริง | ใช้ชื่อ actual files |

---

## 45. Debug Checklist ตามลำดับ

1. Python ใช้ environment ที่มี `redis` และ `rich` หรือไม่
2. Redis process/container รันหรือไม่
3. `PING` ได้ `PONG` หรือไม่
4. ทุก component ชี้ `REDIS_HOST`/port/db เดียวกันหรือไม่
5. `GROUP_ID` ตรงกันหรือไม่
6. race status เป็นอะไร
7. Producerอยู่ Ready หรือส่งแล้ว
8. `XLEN` เพิ่มหรือไม่
9. `XINFO GROUPS` เห็น `f1_pitwall` หรือไม่
10. `lag` ลดหรือเพิ่ม
11. `pending` เป็นศูนย์หรือไม่
12. `XINFO CONSUMERS` เห็น consumerใด active
13. Student 5ได้รับ entryหรือไม่
14. Pub/Sub channelตรง `f1:dashboard:g04` หรือไม่
15. Dashboard subscribeก่อน publishหรือไม่
16. มี malformed data/conversion errorหรือไม่
17. Streamถูก trimจน entryเก่าหายหรือไม่
18. Finish subscriberออนไลน์ก่อน publishหรือไม่
19. cleanup/resetรอบก่อนสมบูรณ์หรือไม่
20. กำลังคาดหวัง fan-outจาก shared groupผิดหรือไม่

---

# Part M — แบบฝึกหัด

## 46. แบบฝึกหัด

### Exercise 1 — เลือก Redis data type

จับคู่ requirement กับ String, Stream หรือ Pub/Sub:

1. ต้องอ่านสถานะล่าสุดแม้เปิด process ทีหลัง
2. ต้องเก็บ event มี ID และ ACK
3. ต้อง broadcast update สดให้จอที่ออนไลน์
4. ต้องตรวจ messageที่ workerรับแล้วแต่ยังไม่เสร็จ

### Exercise 2 — Namespace

ถ้าเปลี่ยน `GROUP_ID` เป็น `g07` ให้เขียนชื่อ:

1. Stream key
2. Dashboard channel
3. Race status key
4. Finish channel

ข้อใดเปลี่ยนตาม group และข้อใดเป็น global

### Exercise 3 — 20 Hz

ตอบจาก `dt = 0.05`:

1. target messages/second เท่าไร
2. ที่ 270 km/h เพิ่มระยะต่อ tick เท่าไร
3. 1000 entriesแทนเวลาประมาณกี่วินาที

### Exercise 4 — Threshold boundaries

ทำนายผล:

| tire_wear | temp | rpm | speed | gear |
|---:|---:|---:|---:|---:|
| 75.0 | 115.0 | 14500 | 250.0 | 7 |
| 75.1 | 115.1 | 14501 | 250.1 | 7 |
| 60.0 | 110.0 | 14000 | 300.0 | 6 |

### Exercise 5 — `$`

ถ้ามี 100 entries อยู่ใน Stream แล้ว worker ตัวแรกเพิ่งสร้าง group ด้วย `id="$"` จากนั้น producerส่ง entryที่ 101 จะเกิดอะไรกับ entries 1–100 และ 101 เมื่ออ่าน `>`

### Exercise 6 — Pending

workerอ่าน message A แล้ว crash ก่อน `XACK`:

1. A อยู่ที่ไหน
2. workerอื่นที่อ่าน `>` จะรับ A เป็น new messageหรือไม่
3. ต้องเพิ่มกลไกอะไรเพื่อกู้ A

### Exercise 7 — Shared Group

มี messages M1–M4 และ consumers S2–S5 ใน groupเดียวกัน แต่ละ messageจะถูกส่งให้ทุกคนหรือคนเดียว

### Exercise 8 — Fan-out

ออกแบบ group names เพื่อให้ Pit, Safety, DRS และ Dashboard เห็นทุก telemetry packet

### Exercise 9 — Start Order

อธิบายว่าทำไม `SET GREEN` ก่อนเปิด producerทำให้ producerปัจจุบันไม่ออกทันที

### Exercise 10 — Failure Window

Student 5 publish dashboardสำเร็จแล้ว crash ก่อน ACK ถ้ามี recovery/reclaimภายหลัง dashboardอาจเห็นอะไร

### Exercise 11 — Retention

ทำไม `maxlen=1000` อาจไม่เก็บ raceครบ 10 km และการเพิ่มเป็น 5000 มี trade-offอะไร

### Exercise 12 — Observability

เลือก Redis commandsที่ใช้ตรวจ:

1. Stream length
2. Group lag
3. Pending count
4. Last Stream entry
5. Current race status

### Exercise 13 — Data validation

ถ้า `rpm="fast"` Student 3 และ Student 5 มี behaviorต่างกันอย่างไรจาก source

### Exercise 14 — Pub/Sub offline

ถ้า dashboard listenerเปิดหลัง Student 5 publishไปแล้ว 300 messages จะได้รับ 300 messagesย้อนหลังหรือไม่

### Exercise 15 — End-to-End Proof

เขียนรายการหลักฐานขั้นต่ำที่พิสูจน์ว่าการแข่ง localทำงานจริง ไม่ใช้เพียง startup log

---

## 47. เฉลยแบบฝึกหัด

### Answer 1

1. String
2. Stream
3. Pub/Sub
4. Stream Consumer Group pending list

### Answer 2

```text
f1:telemetry:g07
f1:dashboard:g07
f1:race:status
f1:race:finish
```

สองชื่อแรกเปลี่ยนตามกลุ่ม สองชื่อหลังเป็น global

### Answer 3

```text
20 Hz
3.75 m/tick ที่ 270 km/h
ประมาณ 50 วินาทีสำหรับ 1000 entries ที่ 20 Hz
```

### Answer 4

แถวแรก:

- tire 75.0 ไม่ critical แต่เข้า warningเพราะ >50
- temp 115.0 ไม่ alert
- rpm 14500 ไม่ alert
- speed 250.0 ไม่เปิด DRS แม้ gear 7

แถวสอง:

- critical tire
- temp alert
- rpm alert
- DRS enabled

แถวสาม:

- tire warning
- ไม่มี safety alert
- DRS disabledเพราะ gear 6

หมายเหตุ shared groupทำให้ใน runtimeจริง roleหนึ่งไม่ได้เห็น packetเดียวกันทั้งหมด

### Answer 5

Groupตั้ง cursorที่ท้ายหลัง entry 100 ดังนั้น `>` จะส่ง entry 101 เป็น new message ส่วน 1–100 ไม่ถูกส่งย้อนหลังผ่าน flowนี้

### Answer 6

A อยู่ pendingของ consumerเดิม, `>` ไม่ได้กู้ pendingนั้น และควรเพิ่ม pending read/`XAUTOCLAIM` หรือ `XCLAIM` พร้อม retry policy

### Answer 7

คนเดียวต่อ messageภายใน groupเดียว การแบ่งไม่รับประกัน round-robin exact

### Answer 8

ตัวอย่าง:

```text
f1_pit_strategy
f1_engine_safety
f1_drs
f1_dashboard
```

แต่ละ groupมี consumerของตนเอง

### Answer 9

producerมอง GREENที่มีอยู่ก่อนเปิดว่าอาจเป็นสถานะเก่าจากรอบก่อน จึงรอให้เปลี่ยนเป็น non-GREEN ก่อน แล้วค่อยรอ GREENรอบใหม่

### Answer 10

messageยัง pending และเมื่อ reclaim อาจ publishซ้ำ Dashboardควรรับ duplicateได้หรือ deduplicateด้วย Stream ID

### Answer 11

raceเฉลี่ยเชิงทฤษฎีใช้ราว 2,667 packets แต่ retentionเป้าหมายประมาณ 1,000 การเพิ่มเป็น 5,000เก็บย้อนหลังมากขึ้นแต่ใช้ memoryมากขึ้น

### Answer 12

```text
XLEN
XINFO GROUPS
XPENDING
XREVRANGE ... COUNT 1
GET f1:race:status
```

### Answer 13

ทั้งสองเรียก `int(...)` จึงเกิด conversion exception Student 3พิมพ์ `Error:` ส่วน Student 5พิมพ์ `❌ Error:` และ messageไม่ถึง ACK

### Answer 14

ไม่ได้ Pub/Subไม่ replay messagesเก่า จะรับเฉพาะหลัง subscribeสำเร็จ

### Answer 15

อย่างน้อย:

- Redis PING
- status transition STOPPED→GREEN
- Stream length/last packetเพิ่มจริง
- producerถึง finishและส่งระยะ >= 10,000
- workerมี processing/ACK
- Student 5มี publishจริง
- listener subscribeและรับ live data
- group pending/lagถูกตรวจ
- finish groupถูก Race Controlรับ
- cleanup/resetถูกยืนยัน

---

# Part N — คำถามแนวสอบ

## 48. คำถามแนวสอบพร้อมคำตอบสั้น

### 48.1 Redis Stream ต่างจาก Pub/Sub อย่างไร

Streamเก็บ entriesพร้อม IDและรองรับ Consumer Group/ACK ส่วน Pub/Subส่งสดและไม่เก็บย้อนหลังให้ subscriberที่ offline

### 48.2 `XADD` ทำอะไร

append field-value entryใหม่เข้า Streamและคืน Stream ID

### 48.3 `mkstream=True` ทำอะไร

สร้าง Streamให้อัตโนมัติเมื่อยังไม่มีตอนสร้าง Consumer Group

### 48.4 `id="$"` ตอนสร้าง groupหมายถึงอะไร

เริ่มรับ new messagesหลังท้าย Stream ณ เวลาสร้าง ไม่อ่าน entriesเก่าเป็น new delivery

### 48.5 `>` ใน `XREADGROUP` หมายถึงอะไร

ขอ messagesใหม่ที่ยังไม่เคยมอบให้ consumerใน group

### 48.6 ทำไมต้อง `XACK`

ยืนยันว่า consumerประมวลผล messageเสร็จแล้วและเอาออกจาก pending list

### 48.7 ถ้าลืม ACK จะเกิดอะไร

messageค้าง pending แม้ถูกอ่านออกไปแล้ว

### 48.8 `block=1000` คืออะไร

ให้ readรอข้อมูลได้สูงสุดประมาณ 1,000 ms แทน busy loopตลอดเวลา

### 48.9 `count=1` คืออะไร

ขอส่งกลับสูงสุดหนึ่ง entryต่อการอ่านรอบนั้นใน flowนี้

### 48.10 Consumer Group แจก messageให้ทุก consumerหรือไม่

ไม่ ภายใน groupเดียว messageหนึ่งถูกส่งให้ consumerหนึ่งตัวเพื่อแบ่งงาน

### 48.11 ถ้าต้องการทุก roleเห็นทุก packetทำอย่างไร

ใช้ Consumer Groupแยกต่อ roleหรือออกแบบ fan-outอื่น

### 48.12 ทำไม Student 5เป็น bridge

อ่าน durable Stream eventแล้ว publish live JSONให้ dashboardsผ่าน Pub/Sub

### 48.13 ทำไม race statusใช้ String

producerที่เปิดทีหลังต้องอ่านสถานะปัจจุบันได้

### 48.14 ทำไม finishผ่าน Pub/Subเสี่ยงหาย

ถ้า subscriberไม่ออนไลน์ตอน publishจะไม่มี replay

### 48.15 `decode_responses=True` ช่วยอะไร

decode Redis bytesเป็น Python strings ทำให้เทียบ/parseง่ายขึ้น

### 48.16 ทำไมใช้ `time.monotonic()` จับ interval

monotonic clockไม่ย้อนจากการปรับ system wall clock จึงเหมาะกับวัดช่วงเวลา

### 48.17 ทำไมยังใช้ `time.time()` ใน payload

เพื่อบันทึก wall-clock Unix timestampที่สื่อสารข้ามระบบได้

### 48.18 ทำไม printทุก packetไม่ดี

terminal I/Oเพิ่ม overheadและทำให้ target 20 Hzคลาดเคลื่อน

### 48.19 `approximate=True` หมายถึงอะไร

Redis trim Streamอย่างมีประสิทธิภาพโดยความยาวอาจไม่เท่ากับ targetพอดี

### 48.20 `noeviction` เมื่อ memoryเต็มมีผลอย่างไร

Redisไม่ลบ keyให้อัตโนมัติ writeที่ต้องใช้ memoryเพิ่มอาจ error

### 48.21 Namespaceป้องกันอะไร

ลด key/channel collisionระหว่างกลุ่ม แต่ไม่ใช่ระบบสิทธิ์

### 48.22 Pendingต่างจาก lagอย่างไร

pendingคือส่งให้ consumerแล้วแต่ยังไม่ ACK; lagคือ entriesใหม่ที่ groupยังไม่ได้ deliver

### 48.23 ทำไม worker Readyแต่ไม่มี alertอาจไม่ใช่ bug

ไม่มี thresholdผ่าน หรือ packetถูกแบ่งให้ consumer roleอื่นใน shared group

### 48.24 ทำไม dashboard distanceอาจไม่ถึง 10,000แต่ teacher mark finished

final packetอาจถูก consumerอื่นรับ จึงไม่ได้ broadcast แต่ producerส่ง finish channelแยกโดยตรง

### 48.25 ใช้ startup logsพิสูจน์ระบบครบได้หรือไม่

ไม่ได้ ต้องตรวจ Redis data, final producer state, worker ACK/pending, broadcaster และ subscriber boundary

---

## 49. Exam Checklist

ก่อนสอบควรตอบได้โดยไม่เปิดคู่มือ:

- [ ] อธิบาย String, Stream และ Pub/Subต่างกันได้
- [ ] วาด flow Producer→Stream→Consumer→Pub/Sub→Dashboardได้
- [ ] จำ Stream key `f1:telemetry:g04` ได้
- [ ] จำ dashboard channel `f1:dashboard:g04` ได้
- [ ] จำ race status keyและfinish channelได้
- [ ] บอก telemetry fieldsทั้ง 7 ได้
- [ ] อธิบาย 20 Hzจาก `dt=0.05` ได้
- [ ] คำนวณ distance deltaจาก km/hได้
- [ ] อธิบาย monotonic schedulingได้
- [ ] อธิบาย `XADD` และ maxlenได้
- [ ] อธิบาย Stream IDได้
- [ ] อธิบาย `XGROUP CREATE ... $ MKSTREAM` ได้
- [ ] อธิบาย `XREADGROUP ... >` ได้
- [ ] อธิบาย pendingและACKได้
- [ ] รู้ว่าโค้ดยังไม่มี pending recovery
- [ ] จำ thresholdของ Student 2–4ได้
- [ ] อธิบาย Student 5 bridgeได้
- [ ] แยก load balancingจาก fan-outได้
- [ ] รู้ว่า shared `f1_pitwall`ทำให้แต่ละ roleไม่ได้ทุก packet
- [ ] อธิบาย groupแยกต่อ roleได้
- [ ] จำลำดับ STOPPED→Ready→GREENได้
- [ ] รู้ว่าตั้ง GREENก่อน producerทำให้รอ stale reset
- [ ] แยก local hostกับ classroom IPได้
- [ ] ใช้ XLEN/XINFO/XPENDING/XREVRANGEได้
- [ ] อธิบาย Stream retention 1000 entries≈50sได้
- [ ] รู้ว่า Pub/Sub subscriber offlineพลาด message
- [ ] รู้ว่า active Compose configชนะ commentเก่า
- [ ] บอกได้ว่าคำสั่งชื่อไฟล์ในใบงานบางชื่อไม่ตรงไฟล์จริง
- [ ] วาง cleanupโดยไม่ใช้ FLUSHDBบน shared Redisได้

---

## 50. Cheat Sheet

```text
DATA TYPES
String   = เก็บค่าล่าสุด
Stream   = เก็บ ordered entries + ID + group + pending + ACK
Pub/Sub  = ส่งสด ไม่มี replay/ACK

KEYS
f1:race:status      -> STOPPED/GREEN
f1:telemetry:g04    -> telemetry Stream
f1:dashboard:g04    -> dashboard Pub/Sub
f1:race:finish      -> finish Pub/Sub

CURRENT CONFIG
REDIS_HOST = 172.16.46.79   (student files)
GROUP_ID   = g04
STUDENT_ID = 6710301033
GROUP_NAME = f1_pitwall
DISTANCE   = 10000 m
RATE       = 20 Hz

STREAM
XADD                -> append event
MAXLEN ~ 1000       -> retentionประมาณ 50sที่20Hz
XGROUP CREATE ... $ -> เริ่มจากท้ายตอนสร้าง
XREADGROUP ... >    -> ขอ new entries
XACK                -> เอาออกจาก pending
XPENDING             -> ดูงานส่งแล้วแต่ยังไม่ ACK
XINFO GROUPS         -> ดู lag/pending/group state

THRESHOLDS
Tire critical       > 75
Tire prepare        > 50
Engine temp alert   > 115
RPM alert           > 14500
DRS enabled         speed > 250 AND gear >= 7

START ORDER
Redis -> STOPPED -> workers/listener -> producer Ready -> GREEN

BIGGEST CAVEAT
Student 2–5 share f1_pitwall
=> load balancing
=> one role per entry
=> NOT every role sees every packet

FAN-OUT
one independent consumer group per role

RECOVERY GAP
Current code reads only > and has no XAUTOCLAIM/XCLAIM

PUB/SUB GAP
Offline subscriber misses dashboard/finish events
```

---

## 51. สรุปสุดท้าย

Week 9 สร้างระบบ telemetry ที่มี communication สามรูปแบบทำงานร่วมกัน:

1. `f1:race:status` เป็น String key สำหรับควบคุมการเริ่ม
2. `f1:telemetry:<GROUP_ID>` เป็น Redis Stream สำหรับข้อมูลที่มีลำดับ, ID และ ACK
3. `f1:dashboard:<GROUP_ID>` กับ `f1:race:finish` เป็น Pub/Sub สำหรับ live update

Student 1 รอ transition จาก STOPPED ไป GREEN แล้วส่งข้อมูลที่ target 20 Hz พร้อมคำนวณระยะทางจนถึง 10,000 เมตร Student 2–4 ตรวจ threshold และ Student 5 แปลง Stream entry เป็น dashboard JSON ส่วน Team Dashboard และ Teacher Race Control แสดงผลสด

ประเด็นที่ต้องจำที่สุดคือ:

> **Consumer Group เดียวกันหมายถึงช่วยกันแบ่ง message ไม่ใช่ทุก consumer ได้สำเนา**

เพราะ Student 2–5 ใช้ group `f1_pitwall` ร่วมกัน โค้ดปัจจุบันจึงเป็น load-balanced worker pool แม้บทบาททางโจทย์ดูเหมือนต้องการ fan-out การออกแบบให้ทุก role ตรวจทุก telemetry packetต้องใช้ group แยกต่อ roleหรือ architectureอื่น

อีกประโยคจำก่อนลง Lab:

> **เปิด Redis → ตั้ง STOPPED → เปิด workers/dashboard → เปิด producerให้ Ready → ค่อยตั้ง GREEN**

และก่อนสรุปว่าระบบทำงาน ต้องตรวจข้อมูลจริงที่ boundary ได้แก่ Stream entry, worker ACK/pending, dashboard publish, finish signal และ cleanup ไม่ใช่ดูเพียงข้อความ “Ready” ค่ะ
