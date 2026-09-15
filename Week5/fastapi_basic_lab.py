"""
================================================================================
CS-302: Introduction to FastAPI - Basic Lab 01
Topic: First Step with FastAPI, Routing, Parameters, & Basic Validation
================================================================================

How to Run This Lab:
--------------------
1. Install dependencies (if you haven't yet):
   $ pip install fastapi uvicorn

2. Run the development server:
   $ uvicorn fastapi_basic_lab:app --reload

3. Open your browser:
   - Interactive API Docs (Test Area): http://127.0.0.1:8000/docs
   - Hello World endpoint:              http://127.0.0.1:8000/
"""

from fastapi import FastAPI  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
from pydantic import BaseModel  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ

app = FastAPI(  # กำหนดหรือปรับค่าให้ app
    title="CS-302: Basic FastAPI Lab",  # กำหนดหรือปรับค่าให้ title
    description="This is the first step lab for students to understand FastAPI routing and data binding.",  # กำหนดหรือปรับค่าให้ description
    version="1.0.0"  # กำหนดหรือปรับค่าให้ version
)  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้

@app.get("/")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
def read_root():  # ประกาศฟังก์ชัน read_root สำหรับรวมขั้นตอนการทำงาน
    """
    Step 1: The simplest GET endpoint.
    Returns a basic JSON response to confirm the server is running.
    """
    print("[SERVER LOG] Hello World endpoint was requested!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    return {"message": "Welcome to CS-302! Your first FastAPI server is alive!"}  # ส่งผลลัพธ์กลับไปยังผู้เรียก


@app.get("/items/{item_id}")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
def read_item_by_id(item_id: int):  # ประกาศฟังก์ชัน read_item_by_id สำหรับรวมขั้นตอนการทำงาน
    """
    Step 2: Path Parameters and Type Coercion.
    FastAPI reads the URL path. Even though 'item_id' arrives as a string (e.g., "/items/123"),
    FastAPI's type hint 'item_id: int' forces the engine to auto-cast it into a Python Integer.
    """
    print(f"[SERVER LOG] Requested Item ID: {item_id} (Type of variable: {type(item_id)})")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # Notice that we can directly do math operations on item_id because it is already an integer
    doubled_value = item_id * 2  # กำหนดหรือปรับค่าให้ doubled_value
    
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "received_item_id": item_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "type_in_python": str(type(item_id)),  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "demonstration_math": f"Your ID doubled is: {doubled_value}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


@app.get("/users")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
def search_users(username: str, age: int = 18):  # ประกาศฟังก์ชัน search_users สำหรับรวมขั้นตอนการทำงาน
    """
    Step 3: Query Parameters.
    Access via: http://127.0.0.1:8000/users?username=Alice&age=21
    'age' has a default value of 18 if the user does not provide it in the URL.
    """
    print(f"[SERVER LOG] Searching for user: {username}, Age constraint: {age}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "search_term": username,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "age_filter": age,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "status": f"Successfully queried user database for {username}"  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้


class SimpleStudent(BaseModel):  # ประกาศคลาส SimpleStudent สำหรับรวมข้อมูลและพฤติกรรมที่เกี่ยวข้อง
    """
    Step 4: Creating a Pydantic Model.
    This model acts as a blueprint/contract for incoming POST data.
    """
    student_id: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    nickname: str  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    gpa: float  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


@app.post("/register/student")  # ใช้ decorator เพื่อกำหนดพฤติกรรมเพิ่มเติมให้กับฟังก์ชันหรือคลาส
def register_student(student: SimpleStudent):  # ประกาศฟังก์ชัน register_student สำหรับรวมขั้นตอนการทำงาน
    """
    Step 5: Receiving JSON Data via POST.
    FastAPI reads the JSON payload from the request body,
    runs it through the SimpleStudent schema, and casts it into a Python Object.
    """
    print(f"[SERVER LOG] New Registration Received!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"[SERVER LOG] ID: {student.student_id}, Name: {student.nickname}, GPA: {student.gpa}")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    
    # We can access attributes using dot notation directly!
    is_academic_probation = student.gpa < 2.00  # กำหนดหรือปรับค่าให้ is_academic_probation
    
    return {  # ส่งผลลัพธ์กลับไปยังผู้เรียก
        "message": "Student registration data parsed successfully!",  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        "student_object_data": {  # เริ่มบล็อกหรือโครงสร้างข้อมูลสำหรับขั้นตอนถัดไป
            "id": student.student_id,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "name": student.nickname,  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
            "current_gpa": student.gpa  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        },  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้
        "academic_probation_alert": is_academic_probation  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    }  # ปิดบล็อกหรือโครงสร้างข้อมูลที่เริ่มไว้