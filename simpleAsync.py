import sys

def evaluate_grade(score):
    if score > 60:
        return "A"
    else:
        return "C"

def main():
    # เปลี่ยนจาก > 2 เป็น > 1 เพื่อรองรับระบบ arguments ของ VPL
    if len(sys.argv) > 1:
        # sys.argv[-1] จะดึงอาร์กิวเมนต์ตัวสุดท้ายเสมอ (ซึ่งก็คือตัวเลขคะแนน เช่น 64, 45)
        test_score = int(sys.argv[-1])
        result = evaluate_grade(test_score)
        print(result) # พ่นเฉพาะผลลัพธ์ดิบให้ VPL จับคู่ตรวจสอบ
    else:
        # หากนักเรียนกดรันธรรมดา (ไม่มี arguments)
        test_score = 85
        result = evaluate_grade(test_score)
        print(f"Score: {test_score} -> Grade: {result}")

if __name__ == "__main__":
    main()