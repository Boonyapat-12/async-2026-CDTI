# 💡 Smart Lab Lighting System - API Specification

This specification documents the API endpoints and WebSocket channels for the Smart Lab Lighting System. The system allows multiple students to independently control their own set of 4 simulated lab lights to test asynchronous programming and concurrency concepts.

## 🛠️ Base URL
* **HTTP:** `http://127.0.0.1:8000`
* **WebSockets:** `ws://127.0.0.1:8000`

---

## 📋 System Parameters

Each student interacts with their own environment using a unique identifier (`student_id`). 
The environment contains 4 virtual lights, each simulated with a specific hardware latency (delay):

| Light ID | Name | Hardware Delay (Simulated) |
| :--- | :--- | :--- |
| `light_1` | ไฟหน้าประตู (Light 1) | 0.5 seconds |
| `light_2` | ไฟโต๊ะปฏิบัติการ A (Light 2) | 1.2 seconds |
| `light_3` | ไฟโต๊ะปฏิบัติการ B (Light 3) | 2.0 seconds |
| `light_4` | ไฟกระดานหน้าห้อง (Light 4) | 0.8 seconds |

---

## 🌐 HTTP REST API (For Students)

### 1. Get All Lights Status
Retrieve the current status, display name, and simulated delay of all 4 lights for a specific student.

* **Method:** `GET`
* **URL Path:** `/api/{student_id}/lights`
* **Headers:** `Accept: application/json`
* **Response:**
  * **Code:** `200 OK`
  * **Content-Type:** `application/json`
  * **Body Example:**
    ```json
    {
      "light_1": {"name": "ไฟหน้าประตู (Light 1)", "status": "OFF", "delay": 0.5},
      "light_2": {"name": "ไฟโต๊ะปฏิบัติการ A (Light 2)", "status": "ON", "delay": 1.2},
      "light_3": {"name": "ไฟโต๊ะปฏิบัติการ B (Light 3)", "status": "OFF", "delay": 2.0},
      "light_4": {"name": "ไฟกระดานหน้าห้อง (Light 4)", "status": "OFF", "delay": 0.8}
    }
    ```

---

### 2. Control Individual Light
Turn a specific light `ON` or `OFF`. The API will intentionally block/delay the response based on the light's hardware latency to simulate physical I/O operations.

* **Method:** `POST`
* **URL Path:** `/api/{student_id}/lights/{light_id}`
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  * **Content Type:** `JSON`
  * **Properties:**
    * `status` (string, required): Must be either `"ON"` or `"OFF"` (case-insensitive).
  * **Body Example:**
    ```json
    {
      "status": "ON"
    }
    ```
* **Response (Success):**
  * **Code:** `200 OK` (Returned *after* the simulated hardware delay completes)
  * **Body Example:**
    ```json
    {
      "student_id": "65010001",
      "light_id": "light_1",
      "current_status": "ON"
    }
    ```
* **Response (Errors):**
  * **Code:** `404 Not Found` (If `light_id` does not exist)
    ```json
    { "detail": "ไม่พบหลอดไฟที่ระบุ" }
    ```
  * **Code:** `422 Unprocessable Content` (If JSON format is invalid or missing `status`)
  * **Code:** `400 Bad Request` (If `status` value is not `"ON"` or `"OFF"`)
    ```json
    { "detail": "สถานะต้องเป็น ON หรือ OFF เท่านั้น" }
    ```

---

### 3. Reset All Lights
Instantly reset the status of all 4 lights back to `OFF` for the specified student.

* **Method:** `DELETE`
* **URL Path:** `/api/{student_id}/lights/reset`
* **Response:**
  * **Code:** `200 OK`
  * **Body Example:**
    ```json
    {
      "message": "รีเซ็ตไฟทุกดวงของนักเรียน 65010001 เป็น OFF เรียบร้อยแล้ว"
    }
    ```

---

## 🔌 WebSocket Channel (For Web Dashboard Frontend)

The Web Dashboard establishes a persistent WebSocket connection to receive instant, real-time broadcasts whenever a light status changes.

### Connection Establishment
* **URL Path:** `/ws/{student_id}`
* **Protocol:** `ws://` (or `wss://` for secure connections)

### Server-to-Client Broadcast (Push Event)
Upon a successful connection, and **immediately after any state change** caused by the HTTP API (Control or Reset endpoints), the server will automatically push the entire updated lights payload to all connected WebSocket clients under that `student_id`.

* **Data Format:** `JSON string`
* **Payload Example:**
  ```json
  {
    "light_1": {"name": "ไฟหน้าประตู (Light 1)", "status": "ON", "delay": 0.5},
    "light_2": {"name": "ไฟโต๊ะปฏิบัติการ A (Light 2)", "status": "OFF", "delay": 1.2},
    "light_3": {"name": "ไฟโต๊ะปฏิบัติการ B (Light 3)", "status": "OFF", "delay": 2.0},
    "light_4": {"name": "ไฟกระดานหน้าห้อง (Light 4)", "status": "ON", "delay": 0.8}
  }