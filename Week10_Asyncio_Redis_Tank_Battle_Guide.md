# Week 10 — Asyncio, Redis Pub/Sub & Multiplayer Tank Battle Study Guide

คู่มือนี้อธิบายจาก **โค้ดจริงปัจจุบันทุกไฟล์ใน `Week10/`** เพื่อให้เข้าใจระบบเกมหลายโปรแกรมตั้งแต่การส่งคำสั่ง การจำลองเกมบน server การ broadcast state ไปจนถึง Terminal/Web Dashboard ค่ะ

> **เป้าหมายหลัก:** อ่านจบแล้วควรวาดสถาปัตยกรรมได้ อธิบาย lifecycle `WAITING → COUNTDOWN → IN_GAME → GAME_OVER` ได้ เข้าใจว่า server เป็น authoritative state อย่างไร และมองเห็นข้อจำกัดของ Redis Pub/Sub, action buffering, collision logic, restart flow และ dashboard ปัจจุบันได้

ไฟล์ที่ใช้อ้างอิง:

1. `Week10/Readme.md`
2. `Week10/docker-compose.yaml`
3. `Week10/server.py`
4. `Week10/tank.py`
5. `Week10/bot.py`
6. `Week10/dashboard.py`
7. `Week10/web_dashboard.py`

สถานะการตรวจ ณ ตอนเขียนคู่มือ:

- ตรวจ syntax ของ Python ทั้ง Week 10 ด้วย `python -m py_compile Week10/*.py` แล้วผ่าน
- อ่าน source ทั้ง 7 ไฟล์และเทียบ schema/channel/config แล้ว
- **ยังไม่ได้อ้างว่าได้เล่นเกม end-to-end ผ่าน Redis, keyboard และ browser จริงในรอบการเขียนคู่มือนี้**
- ข้อความ “expected behavior” จึงเป็นผลที่คาดจาก control flow ไม่ใช่ runtime log ที่แต่งขึ้นแทนการทดสอบ
- คู่มือนี้ไม่แก้ source code และบันทึก current-code caveats แยกอย่างชัดเจน

---

## สารบัญ

1. ภาพรวม Week 10
2. Use case และทักษะที่ได้
3. คำศัพท์สำคัญ
4. Architecture ภาพใหญ่
5. Data plane และ control flow
6. Redis Pub/Sub semantics
7. Channels จริง
8. Command schema
9. Game-state schema
10. Player schema
11. Bullet schema
12. Constants และตัวเลขสำคัญ
13. `server.py` ภาพรวม
14. Server initialization
15. Registration protocol
16. Command validation
17. Single-slot action buffer
18. Movement logic
19. Fire validation
20. Bullet spawning
21. Bullet movement/collision
22. Winner logic
23. Timer logic
24. Match lifecycle
25. Host input และ concurrency
26. Game loop และ tick rate
27. `tank.py` human controller
28. Keyboard listener และ rate limit
29. Human client lifecycle
30. `bot.py` AI client
31. Bot concurrency
32. Bot action policy
33. `dashboard.py`
34. Terminal rendering
35. Terminal dashboard schema mismatch
36. `web_dashboard.py` backend
37. FastAPI lifespan
38. Redis-to-WebSocket bridge
39. Connection manager
40. Browser-side WebSocket
41. Canvas rendering
42. Web status/scoreboard/event log
43. `docker-compose.yaml`
44. `Readme.md` เทียบ sourceจริง
45. End-to-end journey
46. Setup และ dependency
47. คำสั่งรันจาก repo root
48. คำสั่งรันจาก `Week10`
49. ลำดับเริ่มเกมที่ถูกต้อง
50. Expected behavior
51. Restart และ cleanup
52. Current-code caveats
53. Timing และ concurrency analysis
54. Game-rule edge cases
55. Reliability และ message loss
56. Security และ abuse cases
57. Performance และ scaling
58. Troubleshooting matrix
59. Debug checklist
60. แบบฝึกหัด
61. เฉลย
62. คำถามแนวสอบ
63. Exam checklist
64. Cheat sheet
65. สรุปสุดท้าย

---

# Part A — ภาพใหญ่ของระบบ

## 1. Week 10 กำลังเรียนเรื่องอะไร

Week 10 นำหลายแนวคิดจากสัปดาห์ก่อนมารวมเป็นระบบเดียว:

- `asyncio` สำหรับรันงานหลาย loop
- Redis Pub/Sub สำหรับ command และ state broadcast
- server-authoritative simulation
- client แบบ synchronous สำหรับ keyboard
- client แบบ asynchronous สำหรับ bot
- Terminal dashboard
- FastAPI + WebSocket bridge
- HTML5 Canvas สำหรับ UI ใน browser

ระบบไม่ได้เป็นไฟล์เดียว แต่เป็น distributed application ขนาดเล็กที่แต่ละ process มีหน้าที่ต่างกัน

```text
Human Tank ─────┐
                | PUBLISH game:commands
AI Bot ─────────┘
                         |
                         v
                 SecureTankGameServer
                 - players
                 - bullets
                 - timer
                 - collision
                 - winner
                         |
                         | PUBLISH game:state ทุก 0.2s
                         v
              Redis Pub/Sub Channel
                 /                 \
                v                   v
       Terminal Dashboard     Web Dashboard Backend
                                      |
                                      | WebSocket /ws
                                      v
                               Browser Canvas UI
```

หลักคิดสำคัญ:

> Client ส่งเพียง “คำขอ action” แต่ server เป็นผู้ตรวจสอบกฎ เปลี่ยน state คำนวณ collision และประกาศผล

---

## 2. Use case และทักษะที่ได้

แนวคิดใน Week 10 ใช้กับ:

- multiplayer game server
- collaborative real-time app
- telemetry/live dashboard
- chat/notification systems
- IoT command/control
- simulation loop
- WebSocket gateway
- event-driven architecture

หลังเรียนควรทำได้:

1. แยก authoritative server ออกจาก input clients
2. ออกแบบ command/state schema
3. ใช้ Redis Pub/Sub เชื่อมหลาย process
4. รันหลาย coroutine ด้วย `create_task()`/`gather()`
5. ทำ fixed-ish tick game loop
6. buffer input แล้วประมวลผลเป็นรอบ
7. บังคับ cooldown และ active-object limit ฝั่ง server
8. bridge Redis event ไป browser ผ่าน WebSocket
9. render state บน terminal และ canvas
10. วิเคราะห์ message loss, ordering, overwrite และ security gap

---

## 3. คำศัพท์สำคัญ

| คำ | ความหมายแบบง่าย | ตัวอย่างใน Week 10 |
|---|---|---|
| Authoritative Server | server เป็นแหล่งความจริงและตัดสินกฎ | `server.py` |
| Client | ผู้ส่ง input/แสดงผล แต่ไม่ตัดสิน stateหลัก | `tank.py`, `bot.py` |
| Game State | snapshot ของสนาม ณ tickหนึ่ง | JSON บน `game:state` |
| Command | คำขอจากผู้เล่น | `{"team":"A","action":"UP"}` |
| Pub/Sub | ส่ง messageสดผ่าน channel | Redis channels |
| Publisher | ผู้ส่ง message | clients/server |
| Subscriber | ผู้ฟัง channel | server/dashboards |
| Ephemeral | ไม่เก็บ replay ให้ผู้ที่ offline | Pub/Sub messages |
| Tick | รอบอัปเดต simulation | ทุก `0.2` วินาที |
| Tick Rate | จำนวนรอบต่อวินาที | 5 Hz |
| Input Buffer | ที่พัก action ก่อน tick | `next_action` |
| Last-write-wins | ค่าใหม่เขียนทับค่าเดิม | actionล่าสุดก่อน tick |
| Cooldown | เวลาขั้นต่ำระหว่างการยิง | `0.5` วินาที |
| Collision | การตรวจวัตถุชนกัน | bullet coordinateเท่ากับ tank |
| Hit Points | พลังชีวิต | เริ่ม `100`, ลดทีละ `20` |
| Lobby | ช่วงรอผู้เล่น | `WAITING` |
| Countdown | ช่วงนับ 3–2–1 | `COUNTDOWN` |
| WebSocket | connectionสองทางระยะยาว browser/server | `/ws` |
| Lifespan | startup/shutdown lifecycle ของ FastAPI | `@asynccontextmanager` |
| Canvas | พื้นที่วาดเกมใน browser | `<canvas>` |
| Backpressure | กลไกชะลอเมื่อผู้รับช้า | โค้ดนี้ไม่มี queue/backpressureตรง ๆ |
| Authentication | การพิสูจน์ตัวตน | ยังไม่มีใน current code |
| Impersonation | แอบส่ง command ในนามทีมอื่น | เป็นไปได้จาก schemaปัจจุบัน |

---

## 4. Architecture ภาพใหญ่

### 4.1 Process topology

```text
Terminal A: server.py
  subscribe game:commands
  publish   game:state

Terminal B: tank.py Player_1
  publish   game:commands
  subscribe game:state
  listen    keyboard

Terminal C: bot.py Bot_1
  publish   game:commands
  subscribe game:state

Terminal D: dashboard.py
  subscribe game:state

Terminal E: web_dashboard.py
  subscribe game:state
  serve HTTP :8000
  serve WS   /ws

Browser:
  GET /
  connect ws://localhost:8000/ws
  render state

Redis:
  route Pub/Sub messages between all processes
```

### 4.2 Redis ไม่ได้เก็บ authoritative state

แม้ Redis เป็นตัวกลาง แต่ stateหลักอยู่ใน memory ของ `server.py`:

```text
self.players
self.bullets
self.status
self.winner
self.start_time
self.time_left
self.countdown
```

Redis channelมีเพียง messagesสด

ถ้า server process restart:

- stateใน memoryหาย
- subscribersไม่ได้ replay snapshotเก่า
- serverเริ่ม gameใหม่หลัง `flushdb()`

---

## 5. Data Plane และ Control Flow

### 5.1 Command path

```text
Keyboard/Bot
    |
    | JSON PUBLISH
    v
game:commands
    |
    v
server.listen_commands()
    |
    | validate basic shape/action
    v
players[team]["next_action"]
```

### 5.2 Simulation path

```text
game_loop tick
    |
    +-> process_buffered_actions()
    +-> update_bullets()
    +-> check_winner_and_timer()
    +-> build game_state
    +-> PUBLISH game:state
    +-> sleep 0.2
```

### 5.3 Display path

```text
game:state
   +-> tank.py      : ดู GAME_OVER
   +-> bot.py       : ตัดสิน actionถัดไป
   +-> dashboard.py : terminal grid
   +-> web_dashboard.py
          -> manager.broadcast()
          -> browser WebSocket
          -> Canvas/scoreboard/log
```

---

## 6. Redis Pub/Sub Semantics

Redis Pub/Sub ในระบบนี้มีคุณสมบัติ:

- publisherไม่รู้ว่า subscriberประมวลผลสำเร็จหรือไม่
- ไม่มี ACK
- ไม่มี pending list
- ไม่มี replay
- subscriberต้องออนไลน์ก่อน messageมา
- channelไม่ได้เก็บ stateล่าสุด
- deliveryเป็น live fan-outให้ subscribersที่เชื่อมอยู่

ผลในเกม:

- REGISTER อาจหายถ้า serverยังไม่ subscribe
- action อาจหายเมื่อ connectionมีปัญหา
- dashboardที่เปิดทีหลังรอ state tickถัดไป ไม่ได้ snapshotย้อนหลัง
- browserที่ disconnectแล้ว reconnectจะรอ stateใหม่
- GAME_OVER stateมีโอกาสได้รับซ้ำหลาย tick เพราะ serverยัง publishต่อ

Pub/Sub เหมาะกับเกม lab ที่ stateส่งซ้ำบ่อย แต่ commandสำคัญอย่าง registrationอาจต้อง protocolยืนยันในระบบจริง

---

## 7. Channels จริง

| Channel | Publisher | Subscriber | Payload |
|---|---|---|---|
| `game:commands` | human/bot clients | game server | command JSON |
| `game:state` | game server | clients/dashboards/web bridge | state JSON |

ชื่อ channelเป็น global ไม่มี match ID หรือ namespaceต่อห้อง

ถ้าเปิด serverสองตัวบน Redisเดียวกัน:

- ทั้งคู่รับ commandsเดียวกัน
- ทั้งคู่ publish statesลง channelเดียวกัน
- dashboardsเห็น snapshotsสลับจากสอง servers

จึงควรมีเพียง authoritative serverหนึ่งตัวสำหรับ current namespace

---

# Part B — Message Schemas

## 8. Command Schema

รูปแบบ:

```json
{
  "team": "Player_1",
  "action": "UP"
}
```

### 8.1 Fields

| Field | Typeที่คาด | การ normalizeฝั่ง server |
|---|---|---|
| `team` | string | `str(...).strip()` |
| `action` | string | `str(...).strip().upper()` |

ถ้า `team` ว่าง server `continue`

### 8.2 Actions

Registration actions:

```text
REGISTER
JOIN
```

In-game actions:

```text
UP
DOWN
LEFT
RIGHT
FIRE
```

คำอื่นถูก ignoreเมื่อไม่ได้เข้า branch registration

### 8.3 Normalize example

```json
{"team":"  Alpha  ","action":"left"}
```

ถูกตีความเป็น:

```text
team   = Alpha
action = LEFT
```

---

## 9. Game-State Schema

server publish:

```json
{
  "grid_size": 50,
  "players": {},
  "bullets": [],
  "status": "WAITING",
  "winner": null,
  "time_left": 180,
  "countdown": 0
}
```

| Field | Type | ความหมาย |
|---|---|---|
| `grid_size` | int | ความกว้าง/สูงของ grid |
| `players` | object/dict | stateแต่ละทีม |
| `bullets` | array/list | กระสุนที่ยัง active |
| `status` | string | lifecycle state |
| `winner` | string/null | ชนะ, `DRAW`, หรือ null |
| `time_left` | int | เวลาที่เหลือโดยประมาณ |
| `countdown` | int | 3,2,1 หรือ 0 |

**ไม่มี field `is_over` ใน stateที่ serverสร้าง**

---

## 10. Player Schema

เมื่อ register:

```json
{
  "x": 12,
  "y": 34,
  "hp": 100,
  "dir": "UP",
  "last_fire_time": 0.0,
  "next_action": null
}
```

| Field | ใช้ทำอะไร |
|---|---|
| `x`, `y` | ตำแหน่ง grid |
| `hp` | พลังชีวิต |
| `dir` | ทิศที่หันและทิศยิง |
| `last_fire_time` | ตรวจ fire cooldown |
| `next_action` | actionล่าสุดที่รอ tickประมวลผล |

`next_action` ถูกส่งไป dashboardด้วย แม้เป็น internal buffer state

---

## 11. Bullet Schema

```json
{
  "x": 10,
  "y": 9,
  "dx": 0,
  "dy": -1,
  "owner": "Player_1"
}
```

| Direction | `dx` | `dy` |
|---|---:|---:|
| UP | 0 | -1 |
| DOWN | 0 | 1 |
| LEFT | -1 | 0 |
| RIGHT | 1 | 0 |

กระสุนไม่มี:

- unique bullet ID
- creation timestamp
- damage field
- speed field
- TTL field

กฎทั้งหมดจึงมาจาก constants และ update loop

---

## 12. Constants และตัวเลขสำคัญ

| Constant | ค่า | ความหมาย |
|---|---:|---|
| `GRID_SIZE` | 50 | สนาม 50×50 cells |
| `TICK_RATE` | 0.2 s | target 5 ticks/s |
| `FIRE_COOLDOWN` | 0.5 s | ยิงห่างอย่างน้อยครึ่งวินาที |
| `MAX_ACTIVE_BULLETS` | 2 | กระสุนในสนามสูงสุดต่อทีม |
| `GAME_DURATION` | 180 s | 3 นาที |
| initial HP | 100 | พลังชีวิตเริ่มต้น |
| damage/hit | 20 | ลด HP ต่อ hit |
| hits to zero | 5 | 100 / 20 |
| web canvas | 600×600 px | พื้นที่วาด |
| cell size at grid 50 | 12 px | 600 / 50 |
| human send cooldown | 0.05 s | สูงสุดเชิงทฤษฎี 20 commands/s |
| bot loop delay | 0.1 s | สูงสุดเชิงทฤษฎี 10 actions/s |
| server state rate | 5/s | targetจาก 0.2 s |
| max match ticks | 900 | 180 / 0.2 โดยไม่รวม drift |

`FIRE_COOLDOWN / TICK_RATE = 2.5 ticks` หมายถึงการยิงที่ผ่าน cooldownขึ้นกับ wall-clock ไม่ได้ล็อกเป็นจำนวน tickเต็ม ๆ

---

# Part C — `server.py`

## 13. `server.py` ภาพรวม

Class หลัก:

```python
class SecureTankGameServer:
```

ชื่อ “Secure” สื่อว่า serverบังคับกฎยิง แต่ไม่ได้หมายถึงมี authentication/encryptionครบ

หน้าที่หลัก:

| Method | หน้าที่ |
|---|---|
| `init_game()` | ล้าง Redis DB และพิมพ์ banner |
| `reset_game()` | reset in-memory state |
| `start_countdown()` | 3–2–1 และเข้า IN_GAME |
| `listen_commands()` | subscribe/parse/register/buffer actions |
| `process_buffered_actions()` | ทำ movement/fire |
| `update_bullets()` | collisionและ movementของ bullet |
| `check_winner_and_timer()` | ตัดสิน elimination/timeout |
| `wait_for_host_input()` | รอ Enterเพื่อ start/reset |
| `game_loop()` | simulation + publish state |
| `run()` | startทุก loop |

---

## 14. Server Initialization

Constructor สร้าง Redis client:

```python
redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
```

initial state:

```text
players    = {}
bullets    = []
status     = WAITING
winner     = None
start_time = None
time_left  = 180
countdown  = 0
```

### 14.1 `flushdb()`

`init_game()` เรียก:

```python
await self.r.flushdb()
```

หมายถึงลบ **ทุก key ใน Redis database 0** ไม่ใช่เฉพาะ `game:*`

ผล:

- lab Redisเฉพาะเกม: สะดวกสำหรับเริ่มสะอาด
- shared Redis: อันตราย เพราะลบข้อมูลแอปอื่นใน DB 0

Namespaceไม่ช่วยเมื่อใช้ `FLUSHDB`

ระบบที่ปลอดภัยกว่าควรล้างเฉพาะ keysของเกมหรือใช้ dedicated database/container แต่ sourceปัจจุบันใช้ `flushdb()` จริง

---

## 15. Registration Protocol

ใน `listen_commands()`:

```python
if action in ["REGISTER", "JOIN"] and team not in self.players:
```

serverสร้าง player:

```text
x = random 0..49
y = random 0..49
hp = 100
dir = UP
last_fire_time = 0
next_action = None
```

### 15.1 Registration เป็น first branch

registrationไม่ได้ตรวจ `self.status == "WAITING"`

ดังนั้นทีมใหม่สามารถ registerระหว่าง:

- WAITING
- COUNTDOWN
- IN_GAME
- GAME_OVER

ถ้าชื่อยังไม่อยู่ใน `players`

นี่เป็น current-code behavior ที่อาจไม่ตรงกฎ multiplayerจริงซึ่งมัก lock rosterเมื่อ matchเริ่ม

### 15.2 Duplicate registration

ถ้าทีมมีอยู่แล้ว branchแรกไม่เข้า

- ระหว่าง IN_GAME จะไป `elif`
- แต่ `REGISTER/JOIN` ไม่อยู่ `ALLOWED_ACTIONS`
- จึงถูก ignore

### 15.3 Random spawn

ไม่มี collision checkตอน spawn สองทีมจึงสุ่มได้ตำแหน่งเดียวกัน

---

## 16. Command Validation

ก่อนประมวลผล:

```text
JSON decode
str(team).strip()
str(action).strip().upper()
teamว่าง -> ignore
```

ระหว่างเกม actionต้องอยู่:

```text
UP DOWN LEFT RIGHT FIRE
```

และ teamต้อง:

- อยู่ใน `players`
- HP > 0
- statusเป็น `IN_GAME`

### 16.1 Exception policy

catch `Exception` รอบ messageหนึ่งก้อนและพิมพ์ warning จากนั้น listenerทำต่อ

ข้อดี:

- malformed commandหนึ่งตัวไม่ทำให้ serverหยุดทั้งหมด

ข้อจำกัด:

- ไม่มี structured error replyให้ client
- clientไม่รู้ว่า commandถูก reject
- ไม่มี schema library/size limit/authentication

---

## 17. Single-Slot Action Buffer

แต่ละ playerมี:

```python
p["next_action"]
```

เมื่อ commandใหม่มา:

```python
self.players[team]["next_action"] = action
```

ถ้ามีหลาย commandsก่อน game tick:

```text
UP -> LEFT -> FIRE
```

bufferสุดท้ายเป็น:

```text
FIRE
```

UP และ LEFT ถูกเขียนทับโดยไม่ประมวลผล

นี่คือ **last-write-wins single-slot buffer** ไม่ใช่ queue

### 17.1 Rate comparison

- human clientส่งได้เชิงทฤษฎีสูงสุด 20 Hz
- botตัดสินใจ 10 Hz
- serverประมวลผล buffer 5 Hz

จึงมีโอกาสสูงที่ inputหลายตัวถูก overwriteในช่วง 0.2 วินาที

### 17.2 ข้อดี

- จำกัดงานสูงสุดหนึ่ง actionต่อ playerต่อ tick
- ป้องกัน input backlogโตไม่จำกัด
- implementationอ่านง่าย

### 17.3 ข้อเสีย

- inputหายโดยตั้งใจ
- latencyและผลลัพธ์ขึ้นกับ timing
- FIREอาจถูก movementที่มาทีหลังเขียนทับ หรือกลับกัน
- ไม่มี sequence number

---

## 18. Movement Logic

เมื่อ actionเป็นทิศ:

```text
1. เปลี่ยน dirเป็น action
2. ขยับหนึ่ง cellถ้าไม่ชนขอบ
```

กฎขอบ:

| Action | Condition | Update |
|---|---|---|
| UP | `y > 0` | `y -= 1` |
| DOWN | `y < 49` | `y += 1` |
| LEFT | `x > 0` | `x -= 1` |
| RIGHT | `x < 49` | `x += 1` |

แม้ชนขอบ `dir` ก็เปลี่ยนก่อน ดังนั้นรถถังหันได้แต่ไม่ขยับ

### 18.1 Movement กับ turret

โค้ดไม่มี body direction แยกจาก turret direction

`dir` ตัวเดียวใช้ทั้ง:

- ทิศที่ actionขยับ
- ทิศวาดปืน
- ทิศสร้างกระสุน

ดังนั้นปุ่มลูกศรคือ “หันและพยายามขยับหนึ่ง cell” ไม่ใช่ rotate turretอย่างอิสระ

### 18.2 Player collision

ไม่มีการตรวจ tankชนกัน ผู้เล่นจึงอยู่ cellเดียวกันได้

---

## 19. Fire Validation

ก่อนยิง serverตรวจสองกฎ:

```python
team_bullet_count < MAX_ACTIVE_BULLETS
current_time - last_fire_time >= FIRE_COOLDOWN
```

ต้องผ่านทั้งคู่

### 19.1 Cooldown

`last_fire_time` updateเฉพาะเมื่อสร้าง bulletสำเร็จ

ถ้ายิงติด limit:

- ไม่สร้าง bullet
- ไม่ updateเวลา
- เมื่อ bulletเก่าหายและ cooldownเดิมผ่านแล้ว ยิงรอบถัดไปได้ทันที

### 19.2 Active bullet count

นับจาก:

```python
sum(1 for b in self.bullets if b["owner"] == team)
```

กระสุนถูกเอาออกเมื่อ:

- hit player
- เคลื่อนออกนอก grid

### 19.3 Silent rejection

ถ้า cooldownไม่ผ่านหรือมี 2 bulletsแล้ว serverไม่ส่ง error/feedback clientจึงไม่รู้โดยตรง

---

## 20. Bullet Spawning

bulletเกิดหนึ่ง cellด้านหน้ารถถัง:

```text
UP    -> (x, y-1)
DOWN  -> (x, y+1)
LEFT  -> (x-1, y)
RIGHT -> (x+1, y)
```

ถ้าตำแหน่ง spawnอยู่นอกสนาม จะไม่ append bullet

ตัวอย่างรถถังอยู่มุมบน `(0,0)` และหัน UP:

```text
spawn = (0,-1)
```

invalid จึงไม่มีกระสุน แต่ `last_fire_time` ถูกตั้งก่อนตรวจ in-bounds ใน sourceปัจจุบัน

ลำดับจริง:

```text
ผ่าน cooldown/limit
-> set last_fire_time
-> คำนวณ spawn
-> ถ้า in-boundsจึง append
```

ดังนั้นยิงออกนอกขอบไม่สร้าง bulletแต่ยังเสีย cooldown

---

## 21. Bullet Movement และ Collision

`update_bullets()` ทำต่อ bullet:

```text
1. ตรวจ hit ณตำแหน่งปัจจุบัน
2. ถ้า hit: ลด HP และไม่เก็บ bullet
3. ถ้าไม่ hit: x += dx, y += dy
4. ถ้ายังอยู่ในสนาม: เก็บไว้รอบถัดไป
```

### 21.1 Damage

```python
p["hp"] = max(0, p["hp"] - 20)
```

HP ไม่ติดลบ

จาก 100 ต้องโดน 5 ครั้งจึงเหลือ 0

### 21.2 Friendly/self fire

ตรวจ:

```python
b["owner"] != team
```

bulletไม่ยิง ownerตัวเอง แต่ไม่มี conceptพันธมิตร ทีมแต่ละชื่อเป็นศัตรูกันทั้งหมด

### 21.3 Newly spawned bullet ถูก updateใน tickเดียวกัน

`game_loop()` เรียก:

```text
process_buffered_actions()
update_bullets()
```

ดังนั้น bulletที่เพิ่ง appendจะถูกตรวจ collisionที่ cellด้านหน้าและถ้าไม่ hit จะขยับอีกหนึ่ง cellก่อน stateถูก publish

ผล:

- ถ้ามี enemyอยู่ cellติดกัน จะ hitได้ทันที
- ถ้า cellติดกันว่าง bulletจะถูก publishครั้งแรกที่ระยะสอง cellsจาก shooter

นี่เป็น subtle ordering consequence ของ current code

### 21.4 Crossing/Skipping

collisionตรวจเฉพาะ coordinateก่อน movementในแต่ละ tick

ไม่มี:

- swept collisionระหว่าง cell
- bullet-vs-bullet collision
- simultaneous path intersection
- wall/obstacle

### 21.5 Order dependence

players dictและbullets listมี iteration order ถ้ามีหลายเหตุการณ์ใน tickเดียว ผลบางกรณีขึ้นกับลำดับข้อมูล

---

## 22. Winner Logic

ทำงานเมื่อ statusเป็น `IN_GAME`

### 22.1 Last standing

```text
มี playersทั้งหมดอย่างน้อย 2
และ aliveเหลือ 1
-> winner = ทีมที่รอด
-> GAME_OVER
```

### 22.2 All eliminated

```text
มี playersอย่างน้อย 2
และ aliveเหลือ 0
-> DRAW
-> GAME_OVER
```

### 22.3 One-player match

ถ้าเริ่มด้วยผู้เล่นหนึ่งคน:

```text
len(players) >= 2 เป็น false
```

จึงไม่ชนะทันทีและเกมเดินจน timeout

### 22.4 Late registration effect

เพราะ registerระหว่าง IN_GAMEได้ `len(players)` และ alive setเปลี่ยนกลาง matchได้ ซึ่งกระทบ winner logic

---

## 23. Timer Logic

เริ่มเวลาเมื่อ countdownจบ:

```python
self.start_time = time.time()
```

แต่ละ tick:

```python
elapsed_time = time.time() - self.start_time
self.time_left = max(0, int(180 - elapsed_time))
```

`int()` ตัดเศษลง ดังนั้นหลังผ่านเพียงเล็กน้อยอาจแสดง 179 แทน 180

### 23.1 Timeout winner

เมื่อ `time_left <= 0`:

1. ถ้าไม่มีผู้รอด -> DRAW
2. หา HPสูงสุดของผู้รอด
3. ถ้ามีทีมเดียวที่ HPสูงสุด -> ทีมนั้นชนะ
4. ถ้าเสมอ HPสูงสุด -> DRAW

ตำแหน่ง จำนวน hitที่ยิง และจำนวน bulletsไม่ใช้ตัดสิน tie

### 23.2 Wall-clock caveat

ใช้ `time.time()` ซึ่งอาจถูกปรับจาก system clock ต่างจาก `time.monotonic()` ที่เหมาะกับ durationมากกว่า

sourceปัจจุบันใช้ `time.time()` จริง

---

## 24. Match Lifecycle

```text
Server starts
   |
   v
WAITING
   | players REGISTER/JOIN
   | host presses ENTER
   v
COUNTDOWN
   | 3 -> 2 -> 1
   v
IN_GAME
   | movement/fire/collision/timer
   | last standing OR timeout
   v
GAME_OVER
   | host presses ENTER
   v
reset_game()
   |
   v
WAITING (players cleared)
```

### 24.1 State reset

`reset_game()` ตั้ง:

```text
status = WAITING
winner = None
time_left = 180
bullets = []
players = {}
start_time = None
countdown = 0
```

clientsเดิมต้อง registerใหม่เพราะ serverลบ playersทั้งหมด

### 24.2 Countdown state publish

`game_loop()` ยังทำงานและ publish stateระหว่าง countdown แม้ไม่ process movement

browserสามารถเห็น `status="COUNTDOWN"` และ `countdown` value แต่ UIปัจจุบันไม่ได้ render countdownเฉพาะทาง

---

## 25. Host Input และ Concurrency

`wait_for_host_input()` ใช้:

```python
await loop.run_in_executor(None, sys.stdin.readline)
```

เหตุผล:

- `sys.stdin.readline()` เป็น blocking call
- ย้ายไป executor threadเพื่อไม่ block event loop
- command listenerและgame loopยังทำงานระหว่างรอ Enter

### 25.1 Unused prompt variable

methodสร้างตัวแปร:

```python
prompt = "..."
```

แต่ไม่ `print(prompt)` และไม่ได้ส่งให้ `input(prompt)`

ดังนั้นข้อความ promptที่กำหนดไว้ไม่ถูกแสดงจากบรรทัดนี้ใน current code ผู้ใช้เห็น banner/logอื่นแต่ไม่มี promptนี้ตามที่ตัวแปรสื่อ

### 25.2 ENTER behavior

- status GAME_OVER -> reset
- status WAITING และ players=0 -> warning
- status WAITING และมี player -> countdown/start
- statusอื่น: Enterถูกอ่านแต่ไม่มี branchทำงาน

---

## 26. Game Loop และ Tick Rate

```python
while True:
    if self.status == "IN_GAME":
        process actions
        update bullets
        check winner/timer

    publish game_state
    await asyncio.sleep(0.2)
```

### 26.1 Target rate

```text
1 / 0.2 = 5 states/second
```

180 วินาทีเชิงอุดมคติ:

```text
180 / 0.2 = 900 ticks/states
```

### 26.2 Drift

เวลาจริงต่อ loopคือ:

```text
processing + JSON encode + Redis publish + sleep 0.2
```

จึงต่ำกว่า 5 Hzเล็กน้อยเมื่อมี overhead เพราะไม่ได้ชดเชยด้วย monotonic deadline

### 26.3 Publish ในทุก state

แม้ WAITING, COUNTDOWN หรือ GAME_OVER serverยัง publishทุก loop

ข้อดี:

- subscriberที่พลาด stateหนึ่งมี snapshotใหม่ตามมา

ข้อเสีย:

- ใช้ trafficต่อเนื่อง
- GAME_OVER notificationซ้ำ
- Pub/Subยังไม่รับประกัน subscriber offline

---

# Part D — Human Client (`tank.py`)

## 27. `tank.py` ภาพรวม

`KeyboardTankController` เป็น synchronous client ไม่ได้ใช้ `asyncio`

ใช้:

- `redis` synchronous client
- `pynput.keyboard` จับ global keyboard events
- Pub/Sub loopฟัง state
- command-line argumentเป็นชื่อทีม

ค่าปัจจุบัน:

```python
host='172.20.56.216'
```

ซึ่งต่างจาก server/bot/dashboard/web dashboardที่ใช้ `localhost`

---

## 28. Keyboard Listener และ Rate Limit

key mapping:

| Key | Action |
|---|---|
| Arrow Up | `UP` |
| Arrow Down | `DOWN` |
| Arrow Left | `LEFT` |
| Arrow Right | `RIGHT` |
| Space | `FIRE` |

client-side cooldown:

```python
self.send_cooldown = 0.05
```

ถ้ากด eventsถี่กว่านั้นจะไม่ publish

### 28.1 สองชั้นของ rate control

- client cooldown 0.05 ใช้กับ **ทุก action**
- server fire cooldown 0.5 ใช้กับ **FIRE เท่านั้น**
- server tick 0.2 ทำให้ movementสูงสุดเชิง simulationประมาณหนึ่ง cell/tick

client cooldownไม่ใช่ security boundary เพราะ clientอื่นสามารถข้ามได้ Serverยังต้องเป็นผู้บังคับกฎสำคัญ

### 28.2 Threading

`keyboard.Listener` ทำงาน background ส่วน main threadอยู่ใน Redis Pub/Sub `listen()`

`send_action()` ถูกเรียกจาก listener callback ขณะที่ main threadอ่าน state โดย callbackใช้ Redis clientหลักเพื่อ `publish()` ส่วน Pub/Sub objectถูกสร้างและใช้อยู่ใน main thread โครงสร้างนี้จึงมี concurrencyคนละส่วนกัน และเมื่อนำไปต่อยอดควรตรวจ thread-safety contractของ redis-py versionที่ใช้อยู่แทนการสมมติว่า object Redisทุกชนิดใช้ข้าม threadได้เหมือนกัน

---

## 29. Human Client Lifecycle

```text
เริ่ม process
 -> เลือก team name
 -> publish REGISTERหนึ่งครั้ง
 -> start keyboard listener
 -> subscribe game:state
 -> รอ messages
 -> เมื่อ GAME_OVER พิมพ์ผลและ break
 -> stop keyboard listener
 -> run() จบ
```

ผลสำคัญ:

- clientออกจาก state loopเมื่อ GAME_OVER
- ไม่วนรอ WAITINGรอบใหม่
- ไม่ publish REGISTERอัตโนมัติหลัง server reset

จึงไม่ตรงกับ READMEที่ระบุว่า existing clientsจะ auto re-registerโดยไม่ restart scripts

### 29.1 Registration race

`register()` ถูกเรียกก่อนสร้าง Pub/Sub state listener แต่สำคัญกว่าคือ ถ้า server command subscriberยังไม่พร้อม REGISTERอาจหาย เพราะ Redis Pub/Subไม่มี persistence

ไม่มี retry/ACK registration

---

# Part E — Bot Client (`bot.py`)

## 30. `bot.py` ภาพรวม

`TankBot` ใช้ `redis.asyncio`

stateหลัก:

```text
team_name
Redis client localhost
current_state = None
```

สอง coroutine:

```text
listen_game_state()
brain_loop()
```

รันพร้อมกันด้วย:

```python
await asyncio.gather(...)
```

---

## 31. Bot Concurrency

### 31.1 Listener

```text
subscribe game:state
loop forever
  -> receive message
  -> json.loads
  -> current_state = snapshot
```

### 31.2 Brain

```text
sleep 0.5
publish REGISTER
loop every 0.1s
  -> read current_state
  -> if IN_GAME and alive: choose/send random action
  -> if GAME_OVER: print and break
```

`current_state` ถูกแชร์ระหว่าง coroutinesใน event loopเดียว ไม่มี lock แต่ assignmentsไม่มี `await`ระหว่างอ่านง่าย ๆ ใน codeช่วงนั้น

### 31.3 Startup timing

botรอ 0.5 วินาทีก่อน registerเพื่อให้มีโอกาส subscribeก่อน แต่ไม่รับประกัน serverพร้อม

---

## 32. Bot Action Policy

สุ่มเท่ากันจาก:

```text
UP DOWN LEFT RIGHT FIRE
```

ไม่มี:

- pathfinding
- target tracking
- dodge logic
- boundary awareness
- cooldown awareness
- enemy state reasoning

botอาจส่ง FIREถี่ แต่ serverเป็นผู้ rejectตาม cooldownและbullet limit

### 32.1 Brain exitsแต่ processไม่จบ

เมื่อ GAME_OVER:

```python
break
```

ทำให้ `brain_loop()` จบ แต่ `listen_game_state()` ยัง `async for` ตลอดไป

`asyncio.gather()` รอทั้งสอง coroutine จึงยังไม่ return

ผล:

- bot processอาจยังค้างฟัง stateหลัง Game Over
- brainไม่กลับไป registerหรือเลือก action
- botไม่ได้ auto re-registerหลัง reset

นี่คือ current-code lifecycle gap สำคัญ

### 32.2 Action overwrite

brainส่งได้ราว 10 Hz แต่ server tickราว 5 Hz จึงอาจมีสอง actionsในหนึ่ง tickและ actionก่อนถูกเขียนทับ

---

# Part F — Terminal Dashboard (`dashboard.py`)

## 33. `dashboard.py` ภาพรวม

`GameDashboard`:

1. subscribe `game:state`
2. parse JSON
3. สร้าง grid listขนาด `grid_size × grid_size`
4. วาด bulletsก่อน
5. วาด alive playersทับ
6. clear screen
7. พิมพ์ boardและ HP

ใช้ async Redis clientและ `asyncio.run()`

---

## 34. Terminal Rendering

default fallback:

```python
grid_size = state.get("grid_size", 10)
```

แต่ serverส่ง 50 จึงสร้าง grid 50×50

แต่ละ cellกว้าง 3 characters:

```text
50 × 3 = 150 characters
```

ยังไม่รวม border Terminalแคบจึง wrap/flickerได้

### 34.1 Draw order

```text
empty dots
-> bullets '*'
-> players first letter
```

ถ้า bulletและplayerอยู่ cellเดียวกัน playerถูกวาดทับเพราะวาดทีหลัง

### 34.2 Team label collision

ใช้ตัวอักษรแรก:

```python
team_name[0].upper()
```

`Alpha` และ `A-Team`จึงแสดงเหมือนกันบน grid แม้ HP tableยังมีชื่อเต็ม

### 34.3 HP bar

```text
bar_count = hp // 10
```

HP 100 -> 10 blocks
HP 80 -> 8 blocks
...
HP 0 -> 0 blocks

---

## 35. Terminal Dashboard Schema Mismatch

ไฟล์อ่าน:

```python
is_over = state.get("is_over", False)
```

แต่ serverส่ง:

```text
status = "GAME_OVER"
```

และไม่มี `is_over`

ดังนั้น:

```text
is_over -> Falseเสมอจาก stateปัจจุบัน
```

ผลคือ block:

```python
if is_over:
    print winner banner
```

ไม่ทำงาน แม้ serverเข้าสู่ GAME_OVER

Dashboardยังอัปเดต HP/playersได้ แต่ไม่แสดงป้ายผู้ชนะตาม code branchนั้น

แนวคิดที่ควรเข้าใจคือ producer/consumer schemaต้องตรงกันทุก field ไม่ใช่เพียงใช้ JSONได้เหมือนกัน

---

# Part G — Web Dashboard (`web_dashboard.py`)

## 36. Web Dashboard Backend

ไฟล์เดียวทำสองหน้าที่:

1. FastAPI HTTP/WebSocket server
2. Redis subscriber bridge

routes:

```text
GET /
WebSocket /ws
```

port:

```text
0.0.0.0:8000
```

browser local:

```text
http://localhost:8000
```

---

## 37. FastAPI Lifespan

```python
@asynccontextmanager
async def lifespan(app):
    listener_task = asyncio.create_task(redis_listener())
    yield
    listener_task.cancel()
```

Flow:

```text
FastAPI startup
 -> create Redis listener task
 -> serve requests
FastAPI shutdown
 -> cancel listener task
```

Current caveat:

- cancelแต่ไม่ await task
- ไม่ unsubscribe/close Redis explicitly
- ไม่มี exception monitoringของ background task

ระบบจริงควร cleanup resourceอย่างชัดเจน

---

## 38. Redis-to-WebSocket Bridge

```text
server.py
  PUBLISH game:state JSON
       |
       v
web_dashboard.redis_listener()
       |
       v
manager.broadcast(message["data"])
       |
       v
all active WebSockets
```

backendไม่ parse/transform game stateก่อนส่ง browser แต่ forward Redis stringตรง ๆ

ข้อดี:

- codeสั้น
- schemaเดียวกับ Redis

ข้อเสีย:

- malformed JSONไปถึง browser
- ไม่มี validation/filtering
- ไม่มี per-client rate control

---

## 39. Connection Manager

เก็บ:

```python
self.active_connections: list[WebSocket]
```

### 39.1 Connect

```text
accept websocket
append list
```

### 39.2 Disconnect

removeถ้ามีใน list

### 39.3 Broadcast

วนสำเนา list:

```python
for connection in list(self.active_connections):
    await connection.send_text(message)
```

ถ้าส่งพัง remove connection

### 39.4 Serial broadcast caveat

ส่งทีละ connectionด้วย `await` ดังนั้น clientช้าหนึ่งตัวอาจชะลอ clientsถัดไป

ไม่มี queueต่อ clientหรือ timeout

---

## 40. Browser-Side WebSocket

JavaScriptเลือก protocol:

```text
หน้า http  -> ws
หน้า https -> wss
```

URLใช้ hostเดียวกับหน้าปัจจุบัน:

```javascript
new WebSocket(`${wsProtocol}//${window.location.host}/ws`)
```

จึงใช้งานได้ทั้ง localhostและ hostอื่นโดยไม่ hard-code portซ้ำ

### 40.1 Connection lifecycle

- `onopen` -> status WAITING FOR SERVER
- `onmessage` -> parse JSON, render game/info
- `onclose` -> status DISCONNECTED

ไม่มี:

- reconnect loop
- parse error handling
- heartbeat
- authentication token

### 40.2 WebSocket endpointฝั่ง server

หลัง connect:

```python
while True:
    await websocket.receive_text()
```

browser codeปัจจุบันไม่ได้ส่ง textกลับ แต่ receiveค้างไว้เพื่อรอ disconnect event เมื่อ socketปิดจะเกิด `WebSocketDisconnect`

stateถูกส่งจาก `manager.broadcast()` ซึ่งทำงานอีก coroutine ไม่ใช่จาก loopนี้

---

## 41. Canvas Rendering

Canvas:

```text
600 × 600 pixels
```

server grid 50:

```text
CELL_SIZE = 600 / 50 = 12 pixels
```

### 41.1 Dynamic grid

ถ้า stateส่ง `grid_size`ใหม่:

```javascript
GRID_SIZE = gameState.grid_size
CELL_SIZE = canvas.width / GRID_SIZE
```

### 41.2 Players

วาด:

- circleสีตาม hashของ team name
- white border
- gun lineตาม `dir`
- team text

สี deterministicภายใน list 12 สี แต่หลายชื่ออาจชนสีได้

### 41.3 Bullets

วาดวงกลมสีเหลืองที่ bullet coordinate

### 41.4 Dead players

ไม่วาดบน canvasเมื่อ `hp <= 0` แต่ยังอยู่ scoreboard

---

## 42. Web Status, Scoreboard และ Event Log

### 42.1 Statusที่รองรับ

JavaScriptมี branchเฉพาะ:

```text
WAITING
IN_GAME
GAME_OVER
```

ไม่มี branch `COUNTDOWN`

เมื่อ statusเปลี่ยนเป็น COUNTDOWN:

- `lastStatus` ถูก setเป็น COUNTDOWN
- แต่ title/border/logไม่ได้ updateสำหรับ countdown
- field `countdown` ไม่ถูก render

เมื่อเข้า IN_GAMEจึง updateอีกครั้ง

### 42.2 Scoreboard

สร้าง tableจาก `Object.keys(players)` พร้อม:

- team color
- HP bar
- HP number
- ALIVE/DEAD

### 42.3 Event log

เปรียบเทียบ `lastPlayersState` กับ stateใหม่เพื่อจับ:

- player join
- HPลด
- eliminated
- lifecycle changes

### 42.4 Team name injection caveat

scoreboardใช้ template stringใส่ `team` ลง `innerHTML` โดยไม่ escape

team nameมาจาก command messageที่ publisherกำหนดได้ จึงมีโอกาส HTML injection/XSSใน browser dashboardบน networkที่ไม่ไว้ใจ

Canvas `fillText()` ไม่ตีความ HTML แต่ scoreboard `innerHTML` ตีความ markup

---

# Part H — Infrastructure และ README

## 43. `docker-compose.yaml`

active config:

| ค่า | รายละเอียด |
|---|---|
| image | `redis:alpine` |
| container | `tank_game_redis` |
| restart | `always` |
| port | `6379:6379` |
| RDB | ปิดด้วย `--save ""` |
| AOF | ปิดด้วย `--appendonly no` |
| max memory | `512mb` |
| policy | `noeviction` |
| normal client output limit | ปิด |
| TCP backlog | 512 |
| log level | notice |

ไม่มี volumeจึงไม่ออกแบบเพื่อ persistence

เมื่อ memoryถึง limitและ policyเป็น `noeviction` writesที่ต้อง allocate memoryอาจ fail

สำหรับ Pub/Sub game messagesไม่มี key historyมาก แต่ serverเรียก `flushdb()`อยู่ดี

---

## 44. `Readme.md` เทียบ Source จริง

### 44.1 สิ่งที่ตรง

- ใช้ asyncio/Redis/FastAPI/WebSocket/Canvas
- เปิด serverก่อน
- web dashboardที่ port 8000
- human commandรับ team argument
- botรับ team argument
- hostกด Enterเริ่มเกม

### 44.2 Dependency line

READMEแนะนำ:

```bash
pip install fastapi uvicorn redis websocket
pip install pynput redis
```

sourceไม่ได้ import packageชื่อ `websocket` โดยตรง

WebSocketที่ใช้ฝั่ง serverมาจาก FastAPI/Starlette และ browserใช้ built-in WebSocket API

ขั้นต่ำตาม imports:

```text
redis
fastapi
uvicorn
pynput   # เฉพาะ tank.py
```

actual transitive dependenciesถูกติดตั้งตาม package manager

### 44.3 Human Redis host mismatch

READMEอธิบาย local `localhost:6379` แต่ `tank.py`ชี้:

```text
172.20.56.216:6379
```

server/bot/dashboardsชี้ localhost

ถ้าไม่แก้ให้ตรงกัน human tankจะคุยคนละ Redis instance

### 44.4 Restart claimไม่ตรง implementation

READMEบอก existing clientsจะ auto re-registerหลัง reset แต่:

- `tank.py` breakและจบเมื่อ GAME_OVER
- `bot.py` brain breakและไม่ registerใหม่
- bot listenerยังทำให้ gatherค้าง
- server resetล้าง `players`

ดังนั้น flow auto re-registerยังไม่ implementครบใน sourceปัจจุบัน

### 44.5 Control wording

READMEเขียน “Move / Rotate Turret” แต่ sourceใช้ directionเดียวและ movementทุก arrow action ไม่มี turret rotationแยก

### 44.6 Prompt typo

บรรทัด restartมี Markdown `server.py**` ที่ปิด boldไม่สมดุล เป็นเอกสาร typo ไม่กระทบ Python runtime

---

# Part I — End-to-End Execution

## 45. End-to-End Journey

### 45.1 Server startup

```text
server objectสร้าง Redis client
-> asyncio.run(server.run())
-> FLUSHDB db0
-> create command listener task
-> create game loop task
-> wait host Enterใน executor
```

### 45.2 Player joins

```text
client PUBLISH REGISTER
-> Redis forwardsให้ online server
-> server creates player
-> game loop publishes playerใน stateถัดไป
-> dashboardsเห็น player
```

### 45.3 Start

```text
host Enter
-> 3,2,1
-> status IN_GAME/start_time
-> clientsเห็น state
-> botเริ่มสุ่ม action
-> human keyboardส่ง action
```

### 45.4 One action

```text
client publishes command
-> server listener normalizes
-> stores next_action
-> next game tick consumes action
-> clears next_action
-> updates state
-> publishes state
```

### 45.5 Fire/hit

```text
FIRE buffered
-> server checks cooldown/count
-> spawns bullet one cell ahead
-> same tick checks collision
-> if no hit moves bullet
-> later tick hit reduces HP by20
-> dashboard shows HP/event
```

### 45.6 End

```text
last standing หรือ timeout
-> status GAME_OVER
-> winner set
-> state publishซ้ำทุก tick
-> human exits
-> bot brain exitsแต่ listenerยังรอ
-> host Enter resets server players
```

---

## 46. Setup และ Dependency

แนะนำจาก repo rootและ active virtual environment:

```bash
python -m pip install redis fastapi uvicorn pynput
```

หากไม่ใช้ human keyboard client ไม่จำเป็นต้องติดตั้ง `pynput`

ตรวจ imports:

```bash
python -c "import redis; import redis.asyncio; import fastapi; import uvicorn; print('server dependencies ok')"
```

ตรวจ `pynput`:

```bash
python -c "from pynput import keyboard; print('pynput ok')"
```

`pynput` ต้องเข้าถึง desktop/input subsystem จึงอาจมีปัญหาใน headless, container, SSH หรือ WSLบางรูปแบบ

---

## 47. คำสั่งรันจาก Repo Root

### 47.1 เปิด Redis

```bash
docker compose -f Week10/docker-compose.yaml up -d
```

ตรวจ:

```bash
docker compose -f Week10/docker-compose.yaml ps
```

```bash
docker exec tank_game_redis redis-cli PING
```

คาดว่า:

```text
PONG
```

### 47.2 Terminal 1 — Server

```bash
python Week10/server.py
```

### 47.3 Terminal 2 — Web Dashboard

```bash
python Week10/web_dashboard.py
```

เปิด:

```text
http://localhost:8000
```

### 47.4 Terminal 3 — Terminal Dashboard (optional)

```bash
python Week10/dashboard.py
```

### 47.5 Terminal 4+ — Bots

```bash
python Week10/bot.py Bot_1
python Week10/bot.py Bot_2
```

แต่ละคำสั่งต้องเป็นคนละ terminal/process

### 47.6 Human

```bash
python Week10/tank.py Player_1
```

ก่อนรันต้องทำให้ Redis hostใน `tank.py`ชี้ instanceเดียวกับ server

### 47.7 Start

กลับ terminal serverแล้วกด Enterหลังเห็นผู้เล่น register

---

## 48. คำสั่งรันจากภายใน `Week10`

```bash
cd Week10
docker compose up -d
python server.py
python web_dashboard.py
python dashboard.py
python bot.py Bot_1
python tank.py Player_1
```

ยังต้องเปิดหลาย terminal

เปิด web:

```text
http://localhost:8000
```

หยุด Redis:

```bash
docker compose down
```

---

## 49. ลำดับเริ่มเกมที่ถูกต้อง

```text
1. ตรวจ port 6379ว่าง/Redis instanceถูกตัว
2. เปิด Redis
3. PINGให้ได้ PONG
4. ตรวจ hostทุก componentให้ตรงกัน
5. เปิด serverก่อน clients
6. เปิด dashboard/web dashboard
7. เปิด bot/human players
8. ยืนยัน server log REGISTERED
9. กด Enterที่ server
10. รอ countdown 3-2-1
11. เล่น/สังเกตจน GAME_OVER
12. หยุด/restart clientsตาม behaviorจริง
13. cleanup processesและcontainer
```

เหตุผลที่ serverก่อน clients:

- command channelเป็น Pub/Sub
- REGISTER ที่ publishก่อน server subscribeอาจหาย
- ไม่มี retry protocol

---

## 50. Expected Behavior

### 50.1 Server

คาดว่าจะ:

- ล้าง Redis DB0ตอนเริ่ม
- พิมพ์ server banner
- register teamsที่ส่ง command
- ไม่ startถ้ากด Enterตอน playersว่าง
- countdown 3–2–1เมื่อมี player
- publish stateทุกประมาณ 0.2s
- print destroyed/winner/timeout events

### 50.2 Bot

คาดว่าจะ:

- registerหลังเริ่มราว 0.5s
- รอ lobby
- ส่ง random actionsเมื่อ IN_GAMEและยังมี HP
- พิมพ์ Game Overเมื่อเห็น status
- แต่ processอาจไม่จบเพราะ listenerยังรอ

### 50.3 Human

คาดว่าจะ:

- publish registerหนึ่งครั้ง
- แสดง control guide
- ส่ง actionsจาก arrows/space
- พิมพ์ผลเมื่อ GAME_OVER
- stop listenerและออกจาก run

ทั้งนี้ต้องชี้ Redis hostถูกตัวและ `pynput`ทำงานใน desktop session

### 50.4 Terminal Dashboard

คาดว่าจะวาด 50×50 boardและ HP แต่ **ไม่แสดง GAME OVER banner branch** เพราะ field mismatch

### 50.5 Web Dashboard

คาดว่าจะ:

- เปิดหน้าได้ที่ port8000
- connect WebSocket
- render players/bullets
- update timer/HP/status
- ไม่แสดง countdownเฉพาะ
- แสดง GAME_OVER/winnerเมื่อรับ state

---

## 51. Restart และ Cleanup

### 51.1 Restartตาม sourceจริง

เมื่อ GAME_OVER:

1. hostกด Enter
2. server `reset_game()` และล้าง players
3. ต้องเปิด/ปรับ clientsให้ registerใหม่

current clientsไม่ได้ auto re-registerครบ จึงอาจต้อง restart client processes

### 51.2 Stop Python

ใช้ `Ctrl+C` ในแต่ละ terminal

ระวัง botที่ค้างหลัง GAME_OVERอาจต้องหยุดเอง

### 51.3 Stop Redis

```bash
docker compose -f Week10/docker-compose.yaml down
```

### 51.4 ตรวจ port

ถ้าเปิด server/webซ้ำ:

- Redisใช้ 6379
- Web dashboardใช้ 8000

หยุด processเดิมก่อนเริ่มใหม่

### 51.5 Shared Redis warning

serverเริ่มด้วย `FLUSHDB` จึงไม่ควรชี้ไป Redisที่มีข้อมูลสำคัญของระบบอื่น

---

# Part J — Current-Code Caveats

## 52. Current-Code Caveats แบบละเอียด

### 52.1 Redis hostไม่ตรงกัน

`tank.py`ใช้ `172.20.56.216`; ตัวอื่นใช้ localhost

### 52.2 `FLUSHDB` ลบทั้ง DB0

ไม่จำกัดเฉพาะ `game:*`

### 52.3 Pub/Sub ไม่มี delivery guarantee

REGISTER/action/stateหายได้เมื่อ subscriber offline

### 52.4 Single action slot

commandล่าสุดเขียนทับก่อนหน้าใน tickเดียว

### 52.5 Registrationเปิดกลางเกม

ไม่มี status guardใน registration branch

### 52.6 ไม่มี spawn collision check

ผู้เล่นเกิด cellเดียวกันได้

### 52.7 ไม่มี tank collision

ผู้เล่นเดินทับกันได้

### 52.8 Bullet update ordering

bulletใหม่ถูก updateใน tickเดียวกันและอาจปรากฏห่างสอง cells

### 52.9 Cooldownถูกใช้แม้ยิงออกขอบ

`last_fire_time` updateก่อน in-bounds check

### 52.10 One-player matchไม่จบทันที

winner logicต้องมี playersอย่างน้อย 2 จึง last-standing

### 52.11 Prompt variableไม่ถูก print

serverสร้าง promptแต่ไม่แสดง

### 52.12 Timerใช้ wall clockและ `int`

มี truncationและไวต่อ system clock adjustment

### 52.13 `asyncio.create_task()` ไม่เก็บ references

command/game tasksถูกสร้างแล้วไม่เก็บเพื่อ cancel/awaitอย่างเป็นระบบ

### 52.14 Redis resourcesไม่ปิดอย่างชัดเจน

หลาย processไม่มี graceful unsubscribe/close paths

### 52.15 Human exitsหลัง GAME_OVER

ไม่ auto re-register

### 52.16 Bot brainหยุดแต่ listenerไม่หยุด

`gather()`จึงค้างและไม่ restart logic

### 52.17 Terminal dashboardใช้ `is_over`

serverไม่มี fieldนี้ ทำให้ winner bannerไม่ออก

### 52.18 Web dashboardไม่รองรับ COUNTDOWN UI

แม้ stateมี `countdown`

### 52.19 Web dashboardไม่มี reconnect

socketปิดแล้วต้อง reload page

### 52.20 Team nameลง `innerHTML`

มี XSS riskจาก untrusted team name

### 52.21 ไม่มี authentication

publisherใดที่เข้าถึง Redisสามารถส่ง commandในชื่อทีมใดก็ได้

### 52.22 ไม่มี match namespace

หลาย servers/matchesชน channelsเดียวกัน

### 52.23 ไม่มี tests

Week10ปัจจุบันไม่มี automated testsสำหรับ rules/schema/lifecycle

### 52.24 README restartไม่ตรง code

ต้องยึด source behaviorเมื่อ debug

### 52.25 README dependency `websocket`ไม่ตรง imports

ไม่ควรสมมติ packageเพียงจากคำอธิบาย ต้องดู importsจริง

---

# Part K — Timing, Edge Cases และ Reliability

## 53. Timing และ Concurrency Analysis

### 53.1 Three rates

```text
Human event gate ~20 Hz
Bot brain        ~10 Hz
Server tick       ~5 Hz
```

ผลคือ input producerเร็วกว่า consumer buffer

### 53.2 Action timeline example

```text
T=0.00 server tick, buffer cleared
T=0.03 human sends UP
T=0.08 human sends RIGHT -> overwrites UP
T=0.14 human sends FIRE  -> overwrites RIGHT
T=0.20 server tick executes FIRE only
```

### 53.3 Two asyncio tasksใน server

```text
listen_commands --await Redis listen--> wakes on command

game_loop       --sleep 0.2-----------> wakes on tick

wait_host_input  --executor readline---> wakes on Enter
```

ทั้งหมดแชร์ `self.players`/`self.status` บน event loopเดียว

ไม่มี `await`ภายใน `process_buffered_actions()` และ `update_bullets()` เพราะเป็น sync methods จึงทำงานจนจบก่อน event loopสลับ coroutine

### 53.4 Countdown

`start_countdown()` await sleepทุกวินาที จึงให้ command listener/game loopยังทำงาน

playersใหม่จึง registerระหว่าง countdownได้

---

## 54. Game-Rule Edge Cases

### 54.1 Players spawn same cell

ทั้งสองถูก renderทับและ bulletsอาจชนตาม dict iteration order

### 54.2 Player walks onto another

ไม่มี block จึง overlapได้

### 54.3 Bullet starts on enemy

hitใน same tickก่อน movement

### 54.4 Bullet paths cross

ไม่มี bullet-bullet collisionจึงผ่านกันได้

### 54.5 Two bullets hit same tankใน tickเดียว

loopลด HPทีละ bulletจนถึง 0; bulletถัดไปจะไม่ hitเพราะตรวจ `p["hp"] > 0`

### 54.6 Team fires at edge outward

เสีย cooldownแต่ไม่สร้าง bullet

### 54.7 Action during WAITING

movement/fireถูก ignore; REGISTER/JOINยังรับ

### 54.8 Action during COUNTDOWN

movement/fireถูก ignore; registrationยังรับ

### 54.9 Register during IN_GAME

ผู้เล่นใหม่เข้า 100 HPทันที

### 54.10 Dead player commands

ถูก ignoreเพราะ HPต้อง >0

### 54.11 Same teamจากสอง clients

ทั้งสองสามารถ publish actionชื่อเดียวกันและแย่งเขียน `next_action`

### 54.12 Empty team

server ignoreหลัง strip

### 54.13 Non-string JSON fields

serverแปลงด้วย `str`; เช่น `team=123`กลายเป็นชื่อ `"123"`

### 54.14 Malformed JSON

server catchและ ignoreพร้อม warning

### 54.15 Winner tie

timeoutและ HPสูงสุดเท่ากัน -> DRAW

---

## 55. Reliability และ Message Loss

### 55.1 Command loss

ถ้า server offlineตอน publish command ไม่มีใครเก็บ message

### 55.2 State loss

dashboardพลาดบาง stateไม่ร้ายแรงมาก เพราะ stateใหม่เป็น snapshotและส่งซ้ำ 5 Hz

### 55.3 Registration loss

สำคัญกว่า movementเพราะ registerส่งครั้งเดียวใน clientsปัจจุบัน

### 55.4 No acknowledgements

clientไม่รู้ว่า serverรับ actionหรือ registerแล้วจนกว่าจะสังเกต state/log

### 55.5 Reconnect

Redis librariesอาจ reconnectระดับ connection แต่ applicationไม่มี protocol resend registration/last known stateอย่างชัดเจน

### 55.6 Alternativesสำหรับระบบจริง

- Redis Streamsสำหรับ commandที่ต้อง ACK
- request/response registration
- unique player token
- server sequence/tick number
- client command sequence number
- idempotent registration
- periodic re-register/heartbeat
- retained snapshot key
- match-specific channels

เป็นแนวต่อยอด ไม่ใช่ implementationปัจจุบัน

---

## 56. Security และ Abuse Cases

### 56.1 Impersonation

commandเชื่อทีมจาก JSON ไม่มี secret/session binding

ผู้เข้าถึง Redisสามารถส่ง:

```json
{"team":"Victim","action":"LEFT"}
```

### 56.2 Late join

attacker registerกลาง matchได้

### 56.3 Name injection

team nameสามารถมี HTMLและเข้าสู่ web `innerHTML`

### 56.4 Redis exposure

Composeเปิด `6379:6379` และไม่มี password/TLS

ไม่ควร exposeสู่ public network

### 56.5 Resource abuse

ชื่อทีมใหม่จำนวนมากสร้าง players dictโตได้ ไม่มี player limit/name length limit

### 56.6 Large payload

ไม่มี message size validationก่อน `json.loads`/processing

### 56.7 `FLUSHDB`

ชี้ serverไป Redis production/sharedผิดตัวทำให้ข้อมูลหาย

### 56.8 “Secure” scope

server-side cooldownและbullet limitช่วยกัน clientโกงบางชนิด แต่ไม่เท่ากับ secure systemครบด้าน

---

## 57. Performance และ Scaling

### 57.1 Server state size

ทุก tick publish playersและbulletsทั้งหมด

เมื่อจำนวนผู้เล่นโต:

```text
payload size ∝ players + bullets
```

### 57.2 Web broadcast

Redis stateหนึ่ง messageถูกส่ง serialไปทุก WebSocket

```text
cost ∝ จำนวน connections
```

### 57.3 Terminal dashboard

สร้าง list 2D 2500 cellsและพิมพ์ boardทั้งหมด 5 ครั้ง/วินาที อาจเกิด flicker/terminal overheadสูง

### 57.4 Canvas

50×50บน 600pxให้ cellเพียง 12px ชื่อทีมอาจอ่านยาก

### 57.5 Redis Pub/Sub

subscriberช้าหรือ output bufferโตอาจมีปัญหา ไม่มี per-client application backpressure

### 57.6 Tick drift

sleepคงที่หลัง processingทำให้ tickช้าลงเมื่อ workloadโต

ระบบเกมจริงมักใช้ monotonic fixed timestep/deadlineและวัด overrun

---

# Part L — Troubleshooting

## 58. Troubleshooting Matrix

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ |
|---|---|---|
| Redis connection refused | containerไม่รัน/hostผิด | PING localhost:6379 |
| Humanไม่ register | `tank.py`ชี้ IPอื่น | เทียบ hostกับ server |
| Botพิมพ์ waitingแต่ serverไม่เห็น | REGISTER publishก่อน subscriber/Redisคนละตัว | เปิด serverก่อนและดู log |
| กด Enterแล้วบอก no players | registrationไม่ถึง | ตรวจ command channel/host |
| ไม่มี promptให้กด Enter | `prompt` variableไม่ถูก print | ยึด lifecycleและกด Enterหลัง REGISTERED |
| Actionตอบสนองขาด ๆ | single-slot overwrite | ลด send rate/ดู tick model |
| FIREไม่ออก | cooldown, 2 bullets, หรือยิงออกขอบ | ตรวจ current bullets/dir/เวลา |
| Tankซ้อนกัน | ไม่มี spawn/movement collision | current rule gap |
| Botหลัง GAME_OVERไม่จบ | listenerยัง infiniteและ gatherรอ | Ctrl+C; เข้าใจ lifecycle gap |
| Restartแล้วไม่มี players | resetล้าง playersและ clientsไม่ re-register | restart clients/implement retryในอนาคต |
| Terminalไม่แสดง winner | อ่าน `is_over`แต่ serverส่ง `status` | schema mismatch |
| Webไม่แสดง countdown | JSไม่มี COUNTDOWN branch | stateมีค่าแต่ UIไม่ render |
| Webขึ้นแต่สนามไม่ขยับ | web backend/Redisคนละ host หรือ serverไม่ publish | ตรวจ browser WSและ Redis subscriber |
| Address already in use 8000 | web processเดิมยังรัน | หยุด processเดิม |
| Port 6379ชน | Redisอีก instanceรัน | ตรวจ container/service |
| `pynput` error | headless/permission/input backend | ใช้ desktop sessionและติด package |
| Board wrap | terminalแคบสำหรับ 150+ chars | ขยาย terminal/ใช้ web dashboard |
| Browser disconnectไม่กลับ | ไม่มี reconnect logic | reloadหน้า/เริ่ม backendใหม่ |
| HTMLแปลกจาก team name | innerHTML injection | ใช้ trusted namesเท่านั้นใน lab |
| ข้อมูล Redisอื่นหาย | server `FLUSHDB` | ใช้ dedicated Redis DB/container |
| สองเกม stateสลับกัน | channelsไม่มี match namespace | รัน serverเดียวต่อ Redis namespace |

---

## 59. Debug Checklist

1. `python` environmentมี packagesครบหรือไม่
2. Redis container/serviceรันหรือไม่
3. PINGได้ PONGหรือไม่
4. serverใช้ `localhost:6379` จริงหรือไม่
5. bot/dashboardsใช้ instanceเดียวกันหรือไม่
6. `tank.py` hostถูกแก้ให้ตรงหรือไม่
7. serverเปิดก่อน clientsหรือไม่
8. serverพิมพ์ `[REGISTERED]` หรือไม่
9. team nameว่าง/ซ้ำหรือไม่
10. กด Enterหลัง player registerแล้วหรือไม่
11. statusอยู่ WAITING/COUNTDOWN/IN_GAME/GAME_OVERอะไร
12. clientกำลัง publish actionหรือไม่
13. actionsถูก overwriteก่อน tickหรือไม่
14. player HP >0หรือไม่
15. FIREติด cooldownหรือactive limitหรือไม่
16. tankหันออกขอบหรือไม่
17. dashboardใช้ state schemaถูกหรือไม่
18. web backend subscribe Redisถูกตัวหรือไม่
19. browser WebSocket openหรือ disconnected
20. มี server/web processซ้ำบน portหรือไม่
21. bot brainจบแต่ listenerยังค้างหรือไม่
22. resetแล้ว clientsได้ registerใหม่จริงหรือไม่
23. มีอีก server publish channelเดียวกันหรือไม่
24. ใช้ shared Redisที่ไม่ควรถูก FLUSHDBหรือไม่
25. cleanupทุก processหลังทดสอบหรือยัง

---

# Part M — แบบฝึกหัด

## 60. แบบฝึกหัด

### Exercise 1 — วาด Architecture

วาดเส้นทางจากการกด Spaceจน browserเห็น bullet โดยระบุ channelและ methodหลักทุกขั้น

### Exercise 2 — Schema

จาก stateต่อไปนี้ fieldใดขาดสำหรับ sourceปัจจุบัน:

```json
{
  "players": {},
  "bullets": [],
  "is_over": false
}
```

### Exercise 3 — Tick Rate

ตอบ:

1. `TICK_RATE=0.2` เท่ากับกี่ Hz
2. 180 วินาทีมีกี่ ticksเชิงอุดมคติ
3. ทำไม runtimeจริงอาจน้อยกว่า

### Exercise 4 — Buffer

ก่อน tickมี commands:

```text
UP, UP, LEFT, FIRE, RIGHT
```

actionใดถูก executeจาก single-slot buffer

### Exercise 5 — Movement Boundary

playerอยู่ `(0,0)`, dirเดิม RIGHT แล้วรับ LEFT จากนั้นรับ UPคนละ tick ตำแหน่งและ dirเป็นอะไรหลังแต่ละ tick

### Exercise 6 — Fire at Edge

playerอยู่ `(0,0)`หัน UPและ cooldownผ่าน:

1. bulletถูกสร้างหรือไม่
2. `last_fire_time`เปลี่ยนหรือไม่

### Exercise 7 — New Bullet Ordering

playerอยู่ `(10,10)`หัน RIGHTและยิง ไม่มี enemyที่ `(11,10)` หลัง tickแรก bulletที่ publishมีโอกาสอยู่ xเท่าไรจาก source flow

### Exercise 8 — Damage

เริ่ม 100 HP ต้องถูก hitกี่ครั้งจึงเป็น 0 และแต่ละครั้งเหลือเท่าไร

### Exercise 9 — Winner

ทำนาย:

1. เกมเริ่มด้วย playerเดียว HP100
2. เกมมีสองคน คนหนึ่ง HP0 อีกคน HP60
3. timeout มีสามคน HP60,60,20

### Exercise 10 — Pub/Sub

bot publish REGISTERก่อน server subscribe แล้ว serverเปิดทีหลัง จะได้รับ REGISTERเก่าหรือไม่

### Exercise 11 — Human vs Bot Rates

อธิบายเหตุผลที่ commandจาก human/botอาจหายทางตรรกะแม้ Redis deliverครบ

### Exercise 12 — Restart

เขียนสิ่งที่เกิดกับ server, human, botหลัง GAME_OVERและ hostกด Enterตาม current code

### Exercise 13 — Dashboard Bug

ทำไม Terminal Dashboardไม่เข้า `if is_over:`

### Exercise 14 — Web COUNTDOWN

serverส่ง COUNTDOWNและ countdown=3 แต่ UI titleจะเปลี่ยนเป็น countdownหรือไม่ เพราะอะไร

### Exercise 15 — Security

ยกตัวอย่างสามวิธีที่ publisherใน Redisเดียวกันรบกวนเกมได้

### Exercise 16 — Server Authority

กฎใด enforceฝั่ง server และกฎใดอยู่ clientเท่านั้น

### Exercise 17 — Late Join

ทีมใหม่ส่ง REGISTERตอน IN_GAME sourceรับหรือปฏิเสธ อธิบาย branch

### Exercise 18 — State vs Event

ทำไมการพลาด `game:state`หนึ่ง messageมักฟื้นได้ง่ายกว่าพลาด REGISTERหนึ่ง message

### Exercise 19 — Testing Plan

ออกแบบ unit testsอย่างน้อย 8 กรณีสำหรับ movement, fire, collision, winnerและschemaโดยไม่ต้องเปิด Redisจริง

### Exercise 20 — Safe Local Run

เขียน checklistก่อนรัน serverเพื่อไม่ให้ `FLUSHDB`ลบข้อมูลระบบอื่น

---

## 61. เฉลยแบบฝึกหัด

### Answer 1

```text
Space
-> tank.on_press
-> send_action("FIRE")
-> PUBLISH game:commands
-> server.listen_commands
-> next_action="FIRE"
-> game tick process_buffered_actions
-> validate cooldown/count
-> append bullet
-> update_bullets
-> build/PUBLISH game:state
-> web Redis listener
-> manager.broadcast WebSocket
-> browser JSON.parse/renderGame
-> canvas draws bullet
```

### Answer 2

ขาดอย่างน้อย `grid_size`, `status`, `winner`, `time_left`, `countdown` ตาม state contract ส่วน `is_over`ไม่ใช่ fieldจาก serverปัจจุบัน

### Answer 3

```text
5 Hz
900 ticksเชิงอุดมคติ
```

runtimeลดจาก processing, JSON, Redis publishและ sleepที่ไม่ชดเชย overhead

### Answer 4

`RIGHT` เพราะทุก commandเขียนทับ `next_action`และ serverอ่านค่าล่าสุด

### Answer 5

LEFTที่ `(0,0)`เปลี่ยน dirเป็น LEFTแต่ xไม่ลด หลัง UPเปลี่ยน dirเป็น UPแต่ yไม่ลด ตำแหน่งยัง `(0,0)`

### Answer 6

bulletไม่ถูกสร้างเพราะ spawn `(0,-1)`นอก grid แต่ `last_fire_time`ถูก updateแล้ว

### Answer 7

เกิดที่ `(11,10)` แล้ว `update_bullets()`ใน tickเดียวกันขยับเป็น `(12,10)`ก่อน publishถ้าไม่มี hit

### Answer 8

```text
100 -> 80 -> 60 -> 40 -> 20 -> 0
```

5 hits

### Answer 9

1. ไม่ last-standingเพราะ total players<2; รอ timeout
2. ทีม HP60ชนะ last standing
3. DRAWที่ timeoutเพราะ top HP60เสมอสองทีม

### Answer 10

ไม่ได้ Pub/Subไม่เก็บ messageย้อนหลัง

### Answer 11

Redisอาจส่งทุก commandถึง listener แต่ `next_action`มีช่องเดียว ค่าใหม่จึง overwriteค่าเก่าก่อน server tick

### Answer 12

serverยัง GAME_OVER/publishจน Enter จากนั้นล้าง playersและกลับ WAITING; humanออกจาก runแล้ว; bot brainหยุดแต่ listenerยังรอและไม่ re-register จึงไม่มี auto restartครบ

### Answer 13

serverส่ง `status="GAME_OVER"` ไม่มี `is_over`; dashboardใช้ default False

### Answer 14

ไม่ มีการ set `lastStatus`แต่ไม่มี branch COUNTDOWNและไม่ใช้ `countdown` render

### Answer 15

ตัวอย่าง:

- impersonate teamเดิม
- registerชื่อจำนวนมากกลางเกม
- inject HTMLผ่าน team name
- flood commands/payloads
- run serverอีกตัว publish stateชนกัน

### Answer 16

server enforce action allowlist, HP alive, movement boundary, fire cooldown, bullet limit, damage/winner Client cooldown 0.05และbot random policyเป็น client behaviorที่ข้ามได้

### Answer 17

รับถ้า teamยังไม่อยู่ เพราะ registration `if`มาก่อน status-gated `elif`และไม่ตรวจ WAITING

### Answer 18

stateเป็น snapshotใหม่และ publishซ้ำประมาณ 5 Hzจึงตาม stateถัดไปได้ REGISTERส่งครั้งเดียวและไม่มี retry ถ้าพลาด serverไม่มี playerนั้น

### Answer 19

ตัวอย่าง tests:

1. move UPในสนาม
2. move UPที่ขอบ
3. directionเปลี่ยนเมื่อชนขอบ
4. fireผ่าน cooldown
5. fireไม่ผ่าน cooldown
6. max 2 bullets
7. bullet hitลด20
8. self bulletไม่ hit
9. last standing
10. timeout highest HP
11. timeout tie
12. published schemaไม่มี/มี fieldsตาม contract

แยก logic methodsออกจาก Redisหรือ instantiate serverแล้วแทน Redisด้วย fakeได้

### Answer 20

- ใช้ dedicated container
- ตรวจ host/port/db
- ตรวจว่าไม่มีข้อมูลสำคัญ
- อย่าชี้ classroom/production Redisโดยไม่ตั้งใจ
- list keysก่อนรัน
- backupถ้าจำเป็น
- เข้าใจว่า `init_game()`เรียก FLUSHDB

---

# Part N — คำถามแนวสอบ

## 62. คำถามแนวสอบพร้อมคำตอบสั้น

### 62.1 Authoritative serverคืออะไร

serverเป็นผู้ถือ stateจริงและตัดสินว่าคำสั่งใดถูกกฎ ไม่เชื่อ stateที่ clientคำนวณเอง

### 62.2 Redisทำหน้าที่อะไร

เป็น message busของ commandและgame-state Pub/Sub ไม่ได้ถือ authoritative stateในโปรเจกต์นี้

### 62.3 ทำไมมีสอง channels

แยกทิศ client→server (`game:commands`) จาก server→clients (`game:state`)

### 62.4 Pub/Subเก็บ messageหรือไม่

ไม่สำหรับ replay ผู้ subscribeทีหลังพลาด messageเก่า

### 62.5 Command schemaมีอะไร

`team` และ `action`

### 62.6 State schemaหลักมีอะไร

`grid_size`, `players`, `bullets`, `status`, `winner`, `time_left`, `countdown`

### 62.7 Server tickกี่ Hz

target 5 Hzจาก sleep 0.2 วินาที

### 62.8 `next_action`เป็น queueหรือไม่

ไม่ เป็น single slot ค่าใหม่ overwriteค่าเดิม

### 62.9 Clientส่ง 20 Hzแล้วรถเดิน 20 cells/sไหม

ไม่แน่ server processสูงสุดหนึ่ง buffered actionต่อ tickราว 5 Hz และ inputsถูก overwriteได้

### 62.10 Serverป้องกัน FIREอย่างไร

ตรวจ cooldown 0.5sและactive bulletsน้อยกว่า2

### 62.11 ยิงกี่ครั้ง tankถึง 0 HP

5 hitsเมื่อเริ่ม100และ damage20

### 62.12 Tankชนกันได้ไหม

ได้ sourceไม่มี player collision

### 62.13 Spawnทับกันได้ไหม

ได้ random positionไม่มี uniqueness check

### 62.14 Bulletใหม่ทำไมอาจดูข้าม cell

spawnหนึ่ง cellหน้าแล้วถูก `update_bullets()`ขยับอีกใน tickเดียวก่อน publish

### 62.15 Last standingใช้เงื่อนไขอะไร

มี playersอย่างน้อย2และ aliveเหลือ1

### 62.16 Timeoutเลือก winnerอย่างไร

ผู้รอดที่ HPสูงสุดคนเดียวชนะ; top HPเสมอเป็น DRAW

### 62.17 Lifecycleมีอะไร

WAITING→COUNTDOWN→IN_GAME→GAME_OVER→reset WAITING

### 62.18 ทำไมใช้ executorรอ Enter

เพื่อไม่ให้ blocking stdinหยุด event loop

### 62.19 Promptใน sourceแสดงไหม

ไม่ ตัวแปรถูกสร้างแต่ไม่ได้ print/useกับ input

### 62.20 Human clientเป็น asyncไหม

ไม่ ใช้ synchronous Redisกับ pynput listener

### 62.21 Botรันสองงานอะไร

listen stateและbrainเลือก actionด้วย `asyncio.gather`

### 62.22 ทำไม botไม่จบหลัง brain break

listenerยัง infiniteและ gatherรอทั้งสอง

### 62.23 Terminal dashboard bugคืออะไร

อ่าน `is_over`แต่ serverส่ง `status`

### 62.24 Web dashboard bridgeอย่างไร

subscribe Redis stateแล้ว broadcast stringไป active WebSockets

### 62.25 FastAPI lifespanใช้ทำอะไร

start Redis listenerตอน app startupและ cancelตอน shutdown

### 62.26 ทำไม serial WebSocket broadcastเสี่ยง

connectionช้าหนึ่งตัวชะลอการส่งให้ตัวถัดไป

### 62.27 Web UIรองรับ COUNTDOWNไหม

stateรับได้แต่ไม่มี branch/render countdownเฉพาะ

### 62.28 `FLUSHDB`อันตรายอย่างไร

ลบทุก keyใน selected Redis DB ไม่ใช่แค่เกม

### 62.29 ทำไม `Secure`ยังไม่ secureครบ

ไม่มี auth, identity binding, input limits, safe HTML, network security และ late-join restriction

### 62.30 README auto-restartตรงไหม

ไม่ตรงกับ current human/bot lifecycle

### 62.31 ทำไม package `websocket`อาจไม่จำเป็น

sourceใช้ FastAPI WebSocketและ browser built-in ไม่ import packageนั้นโดยตรง

### 62.32 Team nameสร้าง XSSได้อย่างไร

ถูก interpolatedลง `innerHTML`โดยไม่ escape

### 62.33 State messageหายหนึ่งครั้งกับ commandหายต่างกันอย่างไร

snapshot stateใหม่มาแทนได้ แต่ commandเป็น intentครั้งเดียวที่อาจไม่ถูก execute

### 62.34 ทำไมหลาย serverใช้ Redisเดียวกันไม่ได้ดี

subscribe commandsและpublish statesบน global channelsเดียว ทำให้ stateขัดกัน

### 62.35 มี automated testsไหม

ไม่มีใน Week10ปัจจุบัน

---

## 63. Exam Checklist

- [ ] วาด process topologyทั้งหมดได้
- [ ] จำ channels `game:commands` และ `game:state` ได้
- [ ] อธิบาย Pub/Sub ephemeral semanticsได้
- [ ] อธิบาย authoritative serverได้
- [ ] จำ command schemaได้
- [ ] จำ game-state schemaทั้ง 7 fieldsได้
- [ ] อธิบาย player/bullet schemaได้
- [ ] จำ grid50, tick0.2, cooldown0.5, bullets2, duration180ได้
- [ ] คำนวณ 5 Hzและ900 ticksได้
- [ ] อธิบาย single-slot `next_action`ได้
- [ ] ยก timeline input overwriteได้
- [ ] อธิบาย movement boundaryได้
- [ ] รู้ว่า directionและmovementผูกกัน
- [ ] อธิบาย fire cooldown/limitได้
- [ ] รู้ว่ายิงออกขอบยังเสีย cooldown
- [ ] อธิบาย bullet update orderingได้
- [ ] คำนวณ 5 hitsถึง0 HPได้
- [ ] อธิบาย last-standingและtimeout winnerได้
- [ ] รู้ว่า one-player matchรอ timeout
- [ ] อธิบาย lifecycleครบได้
- [ ] อธิบาย executorสำหรับ stdinได้
- [ ] รู้ว่า prompt variableไม่ได้ print
- [ ] อธิบาย human controller flowได้
- [ ] รู้ว่า human hostไม่ตรง localhost
- [ ] อธิบาย bot gatherสอง loopได้
- [ ] รู้ว่า bot brainจบแต่ listenerยังค้าง
- [ ] ชี้ terminal dashboard field mismatchได้
- [ ] อธิบาย Redis→FastAPI→WebSocket bridgeได้
- [ ] รู้ว่า web UIไม่ render COUNTDOWN
- [ ] อธิบาย XSSจาก team nameได้
- [ ] เตือน `FLUSHDB`บน shared Redisได้
- [ ] แยก README claimจาก source behaviorได้
- [ ] วางลำดับ start serverก่อน clientsได้
- [ ] วาง cleanup/restartตาม current codeได้

---

## 64. Cheat Sheet

```text
ARCHITECTURE
Human/Bot --PUBLISH--> game:commands
                              |
                              v
                         server.py
                              |
                PUBLISH game:state every ~0.2s
                    /         |          \
                 client   terminal UI   web bridge -> WebSocket -> browser

REDIS
host server/bot/dash/web = localhost:6379
host tank.py              = 172.20.56.216:6379  <-- mismatch
Pub/Sub = live only, no ACK, no replay

COMMAND
{"team": "Bot_1", "action": "FIRE"}
REGISTER/JOIN
UP/DOWN/LEFT/RIGHT/FIRE

STATE
{
  grid_size,
  players,
  bullets,
  status,
  winner,
  time_left,
  countdown
}

CONSTANTS
GRID_SIZE          50
TICK_RATE          0.2s = 5Hz
FIRE_COOLDOWN      0.5s
MAX_ACTIVE_BULLETS 2/team
GAME_DURATION      180s
HP                 100
DAMAGE             20
HITS TO ZERO       5

ACTION BUFFER
one next_action per player
new command overwrites old command before tick

TICK ORDER
process actions
-> update bullets
-> check winner/timer
-> publish state
-> sleep 0.2

LIFECYCLE
WAITING -> COUNTDOWN -> IN_GAME -> GAME_OVER -> reset -> WAITING

WINNER
>=2 players + 1 alive -> last standing
0 alive -> DRAW
Timeout -> highest HP; tie -> DRAW

KNOWN GAPS
tank Redis host mismatch
FLUSHDB wipes all DB0
REGISTER allowed mid-game
spawn/player overlap allowed
new bullet moves in same tick
tank exits at GAME_OVER
bot brain exits but listener waits forever
no auto re-register as README claims
dashboard.py expects is_over, server sends status
web UI ignores COUNTDOWN
team name enters innerHTML
no auth/match namespace/tests
```

---

## 65. สรุปสุดท้าย

Week 10 เป็นตัวอย่าง event-driven multiplayer system ที่แบ่งความรับผิดชอบชัดเจน:

- Human/Bot clients ส่ง intent ผ่าน `game:commands`
- `server.py` ถือ authoritative state และประมวลผลกฎทุกประมาณ 0.2 วินาที
- serverส่ง snapshotผ่าน `game:state`
- Terminal Dashboardอ่าน stateตรงจาก Redis
- Web Dashboardแปลงเส้นทาง Redis Pub/Subเป็น WebSocketเพื่อให้ browser render Canvas

กฎสำคัญถูกบังคับฝั่ง server เช่น movement boundary, fire cooldown, active bullet limit, damage, timer และ winner แต่ architectureปัจจุบันยังเป็น classroom prototype มีข้อจำกัดที่ควรรู้ ได้แก่ Pub/Subไม่มี replay, registrationไม่มี ACK, input bufferเก็บเพียง actionล่าสุด, Redis hostของ humanไม่ตรงตัวอื่น, `FLUSHDB`ลบทั้ง DB0, restart clientsไม่ตรง README, terminal dashboardอ่าน fieldผิด และ web scoreboardไม่ escape team name

ประโยคจำก่อนสอบ:

> **Client ส่งคำขอ — Server ตัดสิน state — Redis Pub/Sub ส่งสด — Dashboardแสดง snapshot**

ประโยคจำเรื่อง timing:

> **Clientส่งเร็วกว่า tickไม่ได้แปลว่าทุก actionถูกเล่น เพราะ `next_action`มีช่องเดียวและค่าล่าสุดเขียนทับค่าเดิม**

และประโยคจำก่อนรันจริง:

> **ใช้ Redisเฉพาะงาน → เปิด serverก่อน clients → ทำ hostทุกไฟล์ให้ตรง → ยืนยัน REGISTERED → ค่อยกด Enter → cleanupทุก processหลังจบ**
