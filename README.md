# คลังเรียน Asynchronous Programming

> พื้นที่เก็บโค้ด ตัวอย่าง Lab และโน้ตสรุปสำหรับการเรียน Python, concurrent programming และ asynchronous programming

Repository นี้เป็นพื้นที่รวบรวมงานเรียน ตัวอย่างในห้อง Lab และคู่มือที่เกี่ยวข้องกับวิชา Asynchronous Programming ค่ะ  
เนื้อหาจะค่อย ๆ เพิ่มขึ้นตามสัปดาห์ที่เรียน ไม่ได้จำกัดแค่ Week1 หรือ Week2 เท่านั้น

---

## ภาพรวม

เป้าหมายของ repo นี้คือเก็บทุกอย่างที่เกี่ยวกับการเรียนไว้ในที่เดียว เช่น

- ตัวอย่างโค้ดรายสัปดาห์
- ไฟล์ Lab / Assignment
- ตัวอย่างเปรียบเทียบรูปแบบการรันโปรแกรม
- คู่มืออธิบายโค้ดแบบ Markdown
- simulation เล็ก ๆ เช่น ร้านกาแฟ / ร้านอาหาร เพื่อให้เข้าใจ concept ง่ายขึ้น

เนื้อหาส่วนใหญ่ตั้งใจให้เป็นโปรแกรมสั้น ๆ ที่รันดูผลลัพธ์ได้จริง เพื่อให้เห็นพฤติกรรมของแต่ละแนวคิดจาก terminal output โดยตรง

---

## หัวข้อที่เรียน / อาจมีเพิ่มในอนาคต

| หัวข้อ | อธิบายสั้น ๆ |
|---|---|
| Synchronous Programming | การทำงานทีละขั้นตามลำดับ ใช้เป็น baseline เปรียบเทียบ |
| Threading | การแยกงานหลาย workflow ด้วย thread ภายใน process เดียว |
| Multiprocessing | การแยกงานไปทำใน process คนละตัว |
| Asyncio | การเขียน asynchronous programming ด้วย coroutine และ event loop |
| Event Loop | กลไกหลักที่ใช้จัดคิวและสลับงาน async |
| Coroutine & Task | โครงสร้างสำคัญของ `asyncio` ใน Python |
| Timing Comparison | การวัดเวลาเพื่อเปรียบเทียบวิธีรันแต่ละแบบ |
| Simulation Labs | ตัวอย่างจำลองสถานการณ์ เช่น ร้านกาแฟและร้านอาหาร |

---

## โครงสร้าง Repository

```text
.
├── Week1/
│   ├── coffee*.py
│   ├── pid*.py
│   ├── ps*.py
│   └── up*.py
│
├── Week2/
│   ├── asyncio01.py - asyncio10.py
│   └── restaurant_01_*.py
│
├── *.md
│   └── คู่มือสรุป Lab, คำอธิบายโค้ด และโน้ตประกอบการเรียน
│
└── README.md
```

> ในอนาคตอาจมี `Week3/`, `Week4/` หรือโฟลเดอร์อื่น ๆ เพิ่มเข้ามาตามเนื้อหาที่เรียนค่ะ

---

## โมดูลที่มีตอนนี้

| ส่วน | เนื้อหาหลัก |
|---|---|
| `Week1/` | เปรียบเทียบ synchronous, threading, multiprocessing และ asyncio ผ่านตัวอย่างพื้นฐาน |
| `Week2/` | เรียน `asyncio`, coroutine object, task และตัวอย่าง workflow ร้านอาหาร |
| Markdown Guides | คู่มืออธิบาย Lab และ walkthrough สำหรับอ่านทบทวน |

---

## คู่มือประกอบการเรียน

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `Week1_UP1-4_Lab_Guide.md` | คู่มือ Week1 สำหรับเข้าใจ pattern ของ Lab และการเปรียบเทียบวิธีรัน |
| `Week2_Asyncio_Restaurant_Lab_Guide.md` | คู่มือ Week2 สำหรับปูพื้นฐาน `asyncio` และ Lab ร้านอาหาร |
| `Week2_Restaurant_01_Code_Study_Guide.md` | คู่มืออ่านโค้ดร้านอาหารทั้ง 4 แบบ: simple, thread, process และ asyncio |

---

## วิธีรันตัวอย่าง

รันไฟล์ Python ทีละไฟล์จาก root ของ repo:

```bash
python3 Week2/asyncio01.py
python3 Week2/restaurant_01_asyncio.py
```

รันตัวอย่าง `asyncio01.py` ถึง `asyncio10.py` ทั้งชุด:

```bash
for f in Week2/asyncio{01..10}.py; do
  echo "===== $f ====="
  python3 "$f"
  echo
done
```

ตรวจ syntax ของไฟล์ Python ใน Week2:

```bash
python3 -m py_compile Week2/*.py
```

---

## แนวทางการเรียนใน repo นี้

Repo นี้เน้นการเรียนแบบ “เปรียบเทียบให้เห็นภาพ”:

```text
simple / synchronous
        ↓
threading
        ↓
multiprocessing
        ↓
asyncio
```

หลายตัวอย่างจะใช้โจทย์คล้ายกัน แต่เปลี่ยนวิธีรันงาน เพื่อให้เห็นว่า:

- โค้ดเปลี่ยนตรงไหน
- output เรียงต่างกันอย่างไร
- เวลารวมต่างกันแค่ไหน
- วิธีไหนเหมาะกับงานลักษณะใด

---

## หมายเหตุ

- Repo นี้เป็นพื้นที่เรียนรู้ ไม่ใช่ production project
- บางไฟล์ตั้งใจเขียนให้เรียบง่าย เพื่อให้เห็น concept หลักชัดที่สุด
- output ของ thread, process และ async task อาจสลับลำดับกันได้ในแต่ละครั้งที่รัน
- เนื้อหาจะเพิ่มขึ้นเรื่อย ๆ ตามสัปดาห์และ Lab ที่เรียนต่อไป

---

## ผู้จัดทำ

สร้างขึ้นเพื่อเก็บงานเรียนและฝึกเขียนโปรแกรมในสาย Computer Engineering โดยเน้นหัวข้อ asynchronous programming และ concurrent execution ใน Python
