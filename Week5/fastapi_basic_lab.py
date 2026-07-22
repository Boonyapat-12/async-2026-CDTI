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

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="CS-302: Basic FastAPI Lab",
    description="This is the first step lab for students to understand FastAPI routing and data binding.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    Step 1: The simplest GET endpoint.
    Returns a basic JSON response to confirm the server is running.
    """
    print("[SERVER LOG] Hello World endpoint was requested!")
    return {"message": "Welcome to CS-302! Your first FastAPI server is alive!"}


@app.get("/items/{item_id}")
def read_item_by_id(item_id: int):
    """
    Step 2: Path Parameters and Type Coercion.
    FastAPI reads the URL path. Even though 'item_id' arrives as a string (e.g., "/items/123"),
    FastAPI's type hint 'item_id: int' forces the engine to auto-cast it into a Python Integer.
    """
    print(f"[SERVER LOG] Requested Item ID: {item_id} (Type of variable: {type(item_id)})")
    
    # Notice that we can directly do math operations on item_id because it is already an integer
    doubled_value = item_id * 2
    
    return {
        "received_item_id": item_id,
        "type_in_python": str(type(item_id)),
        "demonstration_math": f"Your ID doubled is: {doubled_value}"
    }


@app.get("/users")
def search_users(username: str, age: int = 18):
    """
    Step 3: Query Parameters.
    Access via: http://127.0.0.1:8000/users?username=Alice&age=21
    'age' has a default value of 18 if the user does not provide it in the URL.
    """
    print(f"[SERVER LOG] Searching for user: {username}, Age constraint: {age}")
    return {
        "search_term": username,
        "age_filter": age,
        "status": f"Successfully queried user database for {username}"
    }


class SimpleStudent(BaseModel):
    """
    Step 4: Creating a Pydantic Model.
    This model acts as a blueprint/contract for incoming POST data.
    """
    student_id: str
    nickname: str
    gpa: float


@app.post("/register/student")
def register_student(student: SimpleStudent):
    """
    Step 5: Receiving JSON Data via POST.
    FastAPI reads the JSON payload from the request body,
    runs it through the SimpleStudent schema, and casts it into a Python Object.
    """
    print(f"[SERVER LOG] New Registration Received!")
    print(f"[SERVER LOG] ID: {student.student_id}, Name: {student.nickname}, GPA: {student.gpa}")
    
    # We can access attributes using dot notation directly!
    is_academic_probation = student.gpa < 2.00
    
    return {
        "message": "Student registration data parsed successfully!",
        "student_object_data": {
            "id": student.student_id,
            "name": student.nickname,
            "current_gpa": student.gpa
        },
        "academic_probation_alert": is_academic_probation
    }