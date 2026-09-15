from time import sleep, ctime, time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import multiprocessing  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import os  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ฟังก์ชันจำลองการทำกาแฟให้ลูกค้า 1 คน
def make_coffee(customer_name):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    # ดึง PID ของหน่วยประมวลผลนี้ (ซึ่งจะแยกกันเด็ดขาด)
    pid = os.getpid()  # กำหนดหรือปรับค่าให้ pid
    thread_id = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ thread_id
    thread_name = threading.current_thread().name  # กำหนดหรือปรับค่าให้ thread_name

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] กำลังชงกาแฟให้ ลูกค้า {customer_name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(5) # บล็อกการทำงานของ Thread นี้ไว้ 5 วินาทีเต็มๆ
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue
    main_pid = os.getpid()  # กำหนดหรือปรับค่าให้ main_pid
    main_tid = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ main_tid

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] === เริ่มระบบจำลองตู้กาแฟแบบ Multi-processing ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time

    processes = []  # กำหนดหรือปรับค่าให้ processes
    # ลูปการทำงาน process
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        # สร้าง Process ใหม่แยกจากกันเด็ดขาด
        p = multiprocessing.Process(target=make_coffee, args=(customer,))  # กำหนดหรือปรับค่าให้ p
        processes.append(p)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        p.start()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    for p in processes:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        p.join()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    duration = time() - start_time  # กำหนดหรือปรับค่าให้ duration
    print(f"{ctime()} | ใช้เวลารวมทั้งหมด: {duration:0.2f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน