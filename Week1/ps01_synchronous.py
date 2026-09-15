from time import sleep, ctime, time, process_time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import os  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import psutil  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


# ฟังก์ชันจำลองการทำกาแฟให้ลูกค้า 1 คนแบบซิงโครนัส
def make_coffee(customer_name):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    # ดึง PID และ Thread ID ออกมาดู
    pid = os.getpid()  # กำหนดหรือปรับค่าให้ pid
    thread_id = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ thread_id
    thread_name = threading.current_thread().name  # กำหนดหรือปรับค่าให้ thread_name

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] กำลังชงกาแฟให้ ลูกค้า {customer_name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sum(i * i for i in range(1000000)) # จำลองงานคำนวณ (CPU-bound) เล็กน้อย และรอ 5 วินาที
    sleep(5) # บล็อกการทำงานของ Thread นี้ไว้ 5 วินาทีเต็มๆ
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue
    main_pid = os.getpid()  # กำหนดหรือปรับค่าให้ main_pid
    main_tid = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ main_tid

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] === เริ่มระบบจำลองตู้กาแฟแบบ Synchronous ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time
    start_cpu = process_time() # เริ่มจับเวลา CPU

    # ลูปทำงานตามลำดับคิวเดียว (ทีละคน)
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        make_coffee(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    duration = time() - start_time  # กำหนดหรือปรับค่าให้ duration
    cpu_duration = process_time() - start_cpu  # กำหนดหรือปรับค่าให้ cpu_duration

    # ใช้ psutil ดึงค่าการกิน RAM
    process = psutil.Process(os.getpid())  # กำหนดหรือปรับค่าให้ process
    mem_mb = process.memory_info().rss / (1024 * 1024)  # กำหนดหรือปรับค่าให้ mem_mb

    print(f"[สรุปผล Synchronous]")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"เวลาที่ใช้จริง (Wall Time): {duration:0.2f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"เวลาที่ CPU ใช้ประมวลผลจริง (CPU Time): {cpu_duration:0.4f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"ทรัพยากร Memory (RAM) ที่ใช้: {mem_mb:.2f} MB")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน