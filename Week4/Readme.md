# 🍳 Smart Food Court System - API Specification

This documentation outlines the API endpoint for the Smart Food Court System. The system simulates ordering food from multiple virtual kitchens in a food court, each having a different simulated cooking latency to help students practice asynchronous operations and connection handling.

## 🛠️ Base URL
* **HTTP:** `http://127.0.0.1:8088`

---

## 📋 System Parameters & Kitchen Latency

The food court consists of 3 simulated shops. When a request is made, the API will intentionally block and delay the response using asynchronous sleep to replicate real-world food preparation times:

| Shop Name (`shop_name`) | Description | Cooking Time (Simulated Latency) |
| :--- | :--- | :--- |
| `hainanese_chicken` | ข้าวมันไก่ (Fast: Chopped and served quickly) | 0.8 seconds |
| `noodle` | ก๋วยเตี๋ยว (Medium: Boiling noodles and soup) | 1.5 seconds |
| `steak` | สเต็ก (Slowest: Grilling thick meat) | 4.0 seconds |

---

## 🌐 HTTP REST API

### 1. Place a Food Order
Submit an order to a specific kitchen shop. The API response will be returned only *after* the simulated cooking time for that specific shop has elapsed.

* **Method:** `POST`
* **URL Path:** `/order/{shop_name}`
* **Headers:** `Content-Type: application/json`

#### Request Body
* **Content Type:** `JSON`
* **Properties:**
  * `student_id` (string, required): The unique identifier of the student making the order.
  * `menu_name` (string, required): The name of the dish being ordered.

* **Body Example:**
  ```json
  {
    "student_id": "65010001",
    "menu_name": "T-Bone Steak"
  }