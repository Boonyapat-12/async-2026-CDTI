# ใบงานปฏิบัติการ (Lab Assignment) Real-Time High-Throughput Streaming Processing with Redis Streams & Python AsyncIO

**ปฏิบัติการ:** F1 Telemetry Processing Pipeline & F1 Grand Prix Race Control

---

## F1: ทำไมการจัดการข้อมูลถึงตัดสินผลแพ้-ชนะ?

ในกีฬา Formula 1 ชัยชนะไม่ได้ขึ้นอยู่กับฝีมือของนักแข่งเพียงอย่างเดียว แต่อยู่ที่ **"ข้อมูล (Data)"** รถ F1 หนึ่งคันคือศูนย์รวมของเทคโนโลยีวิศวกรรมขั้นสูงที่มีเซนเซอร์ติดตั้งอยู่รอบคันมากกว่า 300 ตัว เพื่อวัดค่าทุกอย่างตั้งแต่ความเร็ว ความร้อน สภาพยาง ไปจนถึงการไหลของอากาศ ข้อมูลเหล่านี้ถูกส่งกลับมายัง Pit Wall (ทีมวิศวกรข้างสนาม) และ Factory HQ (ศูนย์วิจัยยุทธศาสตร์) ตลอดเวลาด้วยความเร็วสูงมาก

หากระบบจัดการข้อมูลทำงานช้าแม้เพียง 0.1 วินาที (100 Milliseconds) อาจหมายถึงการตัดสินใจสั่งเข้า Pit Stop ผิดพลาด หรือเครื่องยนต์ระเบิดจนต้องออกจากการแข่งขัน

ในทาง Software Engineering นี่คือโจทย์คลาสสิกของระบบ High-Throughput, Low-Latency Data Pipeline ที่ต้องรับข้อมูลมหาศาล (Stream) เข้ามา แล้วแจกจ่ายให้ระบบย่อยต่างๆ ประมวลผลขนานกันโดยไม่เกิดคอขวด (Bottleneck)

---

## รูปแบบการทำใบงาน: ทำงานเป็นกลุ่ม กลุ่มละ 5 คน (แจกแจงตามบทบาท Student 1 – Student 5)



---

## 1. วัตถุประสงค์ (Objectives)



1. เข้าใจสถาปัตยกรรมแบบ Append-Only Log และกลไก Consumer Groups บน Redis Streams


2. สามารถพัฒนาการประมวลผลข้อมูลความเร็วสูงแบบขนาน (Concurrent/Asynchronous Processing) โดยใช้ Python `asyncio` และ `redis.asyncio`

3. สามารถออกแบบสถาปัตยกรรมแบบ Stream-to-Pub/Sub Integration เพื่อเชื่อมต่อระบบย่อยต่างชนิดกันได้


4. เข้าใจการบริหารจัดการ Namespace เพื่อป้องกัน Data Collision เมื่อใช้ Redis Server กลางร่วมกัน


5. สามารถทดสอบการรับส่งและประมวลผลข้อมูล Real-Time Telemetry ภายในกลุ่ม และเข้าร่วมการแข่งขัน Grand Prix บนหน้าจอศูนย์ควบคุมกลาง (Race Control) ได้

---

## 2. กฎการตั้งชื่อและการตั้งค่าระบบ (Namespace Rules)



ไม่ว่าจะใช้ Redis Server กลางเครื่องเดียวกัน (เครื่องอาจารย์) หรือใช้เครื่องตนเอง (localhost) ให้นักศึกษาทุกคนปฏิบัติตามกฎนี้เคร่งครัด:

1. **การตั้งค่า Server IP (`REDIS_HOST`):**

* **การทดสอบภายในกลุ่ม (Internal Lab Test):** ให้เปลี่ยนไปใช้ `'localhost'` หรือ IP เครื่องเพื่อนในกลุ่มที่รัน Redis Server


* **การลงสนามแข่งจริงกับอาจารย์ (F1 Grand Prix Race):** ให้เปลี่ยนไปใส่ IP เครื่องอาจารย์ตามที่ได้รับแจ้งในห้องเรียน




2. **การป้องกันชื่อ Stream ชนกัน (Namespace Policy):**

* **Stream Key Pattern:** `f1:telemetry:<GROUP_ID>` (เช่น `f1:telemetry:g01`, `f1:telemetry:g02`)


* **Consumer Group Name:** `f1_pitwall`

* **Consumer Name Pattern:** `engineer_<ROLE>_<STUDENT_ID>` (เช่น `engineer_pit_strategy_66010002`)


* **Pub/Sub Channel Pattern:** `f1:dashboard:<GROUP_ID>` (เช่น `f1:dashboard:g01`)


* **Race Start Control Key:** `f1:race:status` (คุมสัญญาณปล่อยตัวจากเครื่องอาจารย์)



---

## 3. บทบาทหน้าที่ในแต่ละกลุ่ม (Roles & Tasks)



* **Student 1 (F1 Car Telemetry Producer):** จำลองรถแข่ง F1 สุ่มค่า Telemetry 6 ตัวแปร (`speed`, `engine_temp`, `tire_wear`, `rpm`, `gear`, `distance`) ยิงเข้า Redis Stream ความเร็ว 20 ข้อความ/วินาที (20 Hz) **โดยจะออกตัวได้ก็ต่อเมื่อได้รับสัญญาณ `GREEN` จากศูนย์ควบคุมการแข่งขันเท่านั้น**

* **Student 2 (Pit Strategy Engineer):** อ่าน Stream ตรวจสอบ `tire_wear %` เพื่อสั่งการเข้า Pit Stop (Box Box Box)


* **Student 3 (Race Control Safety):** อ่าน Stream ตรวจสอบ `engine_temp` (> 115°C) และ `rpm` (> 14500 RPM) เพื่อเตือนภัยอันตราย


* **Student 4 (DRS Automation Controller):** อ่าน Stream ตรวจสอบ `speed` (> 250 km/h) และ `gear` (>= 7) เพื่อสั่งเปิดระบบ DRS อัตโนมัติ


* **Student 5 (Dashboard Broadcaster):** อ่านข้อมูล Stream ประมวลผลและแปลงโครงสร้างข้อมูลเป็น JSON ยิงต่อเข้า Redis Pub/Sub Channel ชื่อ `f1:dashboard:<GROUP_ID>` สำหรับนำไปโชว์บน Dashboard



---

## 4. เครื่องมือสำหรับการทดสอบและหน้าจอควบคุม (Auxiliary Tools)

ทางผู้สอนได้เตรียม Script เสริมไว้บน GitHub Repository สำหรับใช้ในขั้นตอนการซ้อมและการแข่งขันจริง ดังนี้:

1. **`dashboard_listener.py` (Team Local Dashboard):**
* **วัตถุประสงค์:** ให้นักเรียนรันเพื่อดู UI แสดงสถานะความเร็ว เกียร์ รอบเครื่องยนต์ และระยะทางสะสมแบบ Real-time ของทีมตนเอง
* **กลไกการทำงาน:** คอยดักฟังข้อมูลที่ broadcast ออกมาจาก Student 5 ผ่าน Redis Pub/Sub Channel `f1:dashboard:<GROUP_ID>`


2. **`teacher_race_control.py` (Grand Prix Live Leaderboard - จออาจารย์):**
* **วัตถุประสงค์:** แสดงตารางการแข่งขันและ Progress Bar ระยะทาง 10,000 เมตร (10 km) ของทุกกลุ่มบนจอ Projector
* **กลไกการทำงาน:**
* สั่งการปล่อยตัวนักเรียนพร้อมกันด้วยสัญญาณไฟเขียว (`f1:race:status` = `"GREEN"`)
* ดักฟัง Pub/Sub Telemetry จาก Student 5 ทุกกลุ่มเพื่ออัปเดตอันดับ (Leaderboard) แบบ Real-time
* รับสัญญาณการเข้าเส้นชัย (`f1:race:finish`) เมื่อมีกลุ่มที่วิ่งครบระยะทาง 10,000 เมตร





---

## 5. ขั้นตอนการติดตั้งและการทดสอบการทำงาน (Execution Guide)

ให้นักศึกษา ดาวน์โหลด (Clone/Download) โค้ดโปรเจกต์ทั้งหมดจาก **GitHub Repository** ที่อาจารย์ได้แจ้งไว้ในชั้นเรียน

### 5.1 การเตรียมความพร้อมของ Environment

ติดตั้งไลบรารีที่จำเป็นบน เครื่องคอมพิวเตอร์ของนักศึกษาทุกคน:

```bash
pip install redis asyncio rich

```

หากต้องการทดลองรัน Redis Server บนเครื่องตนเอง สามารถใช้ Docker Command นี้ได้:

```bash
docker run --name redis-f1 -p 6379:6379 redis:alpine

```

---

### 5.2 ขั้นตอนการซ้อมและทดสอบระบบภายในกลุ่ม (Internal Group Practice)

ก่อนเข้าร่วมการแข่งขันสนามจริง ให้แต่ละกลุ่มทดสอบความถูกต้องของ Pipeline ภายในกลุ่มตนเองตามลำดับดังนี้:

1. **กำหนดเครื่อง Redis กลางประจำกลุ่ม:** เลือกเครื่องของนักเรียนคนใดคนหนึ่งในกลุ่มเป็น Redis Server (หรือใช้ `localhost` หากทดสอบบนเครื่องเดียวกัน)
2. **ตรวจสอบการแก้ไขไฟล์:** ให้นักเรียนทุกคนเปลี่ยน `REDIS_HOST`, `GROUP_ID` และ `STUDENT_ID` ในไฟล์ของตนเองให้ถูกต้อง
3. **เปิดหน้าจอแสดงผลของทีม (Student 5 หรือคนในกลุ่ม):**
```bash
python dashboard_listener.py

```


4. **เปิดสคริปต์ประมวลผล Pit Wall (Student 2, 3, 4, 5):**
```bash
# แต่ละคนรันไฟล์ประจำบทบาทของตนเอง
python student2_pit_strategy.py
python student3_engine_safety.py
python student4_drs_controller.py
python student5_dashboard_broadcaster.py

```


5. **สร้างสัญญาณปล่อยตัวจำลอง (สำหรับซ้อมในกลุ่ม):**
เปิด Terminal ใหม่แล้วสั่งเปลี่ยนสถานะ Redis ให้เป็น GREEN เพื่อทดลองปล่อยตัว:
```bash
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.set('f1:race:status', 'GREEN')"

```


6. **เริ่มรันโปรแกรมส่งข้อมูลรถแข่ง (Student 1):**
```bash
python student1_telemetry_producer.py

```


7. **สังเกตผลการทำงาน:**
* สังเกตว่า `dashboard_listener.py` แสดงค่าความเร็ว เกียร์ และหลอดระยะทางเพิ่มขึ้นอย่างต่อเนื่องหรือไม่
* สังเกตว่า Student 2, 3, 4 มีการแจ้งเตือนตามเงื่อนไข (Threshold) ทาง Terminal หรือไม่



---

### 5.3 ขั้นตอนการลงแข่งขันสนามจริง (F1 Grand Prix Final Race)

เมื่อทุกกลุ่มทดสอบระบบภายในเรียบร้อยแล้ว จะเข้าสู่ขั้นตอนการแข่งขันจริงโดยเปิดแสดงผลขึ้นจอ Projector:

1. **ปรับ `REDIS_HOST`:** นักศึกษาทุกคนในทุกกลุ่ม เปลี่ยนค่า `REDIS_HOST` ให้ชี้ไปที่ **IP เครื่องอาจารย์**
2. **เตรียมความพร้อมบน Grid:**
* นักเรียนทุกคนสั่งรันสคริปต์ของตนเอง (Student 1 - Student 5)
* Student 1 จะแสดงสถานะ `Waiting for Teacher's GREEN LIGHT...` เพื่อจ่อคิวรอปล่อยตัวบน Grid


3. **เปิดหน้าจอแข่งบน Projector:** อาจารย์รันสคริปต์ควบคุมการแข่งขัน:
```bash
python teacher_race_control.py

```


4. **ปล่อยตัว (LIGHTS OUT!):** อาจารย์กด `[ENTER]` เพื่อเริ่มนับถอยหลัง 3.. 2.. 1.. และกระจายสัญญาณ `GREEN` ออกไปในระบบ
5. **ติดตามการแข่งขัน:** รถแข่งของทุกกลุ่มจะออกตัวพร้อมกัน ระบบจะประมวลผลข้อมูล telemetry 20 Hz แบบเรียลไทม์ กลุ่มที่ส่งและประมวลผลข้อมูลครบระยะทาง 10,000 เมตร (10 km) ได้ไวที่สุด จะถูกบันทึกอันดับเข้าเส้นชัยบน Leaderboard ของศูนย์ควบคุมการแข่งขัน