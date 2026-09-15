from time import sleep, ctime, time, process_time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import multiprocessing  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import os  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม
import psutil  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

# ฟังก์ชันจำลองการทำกาแฟให้ลูกค้า 1 คน
def make_coffee(customer_name, result_queue):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    # ดึง PID ของหน่วยประมวลผลนี้ (ซึ่งจะแยกกันเด็ดขาด)
    pid = os.getpid()  # กำหนดหรือปรับค่าให้ pid
    thread_id = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ thread_id
    thread_name = threading.current_thread().name  # กำหนดหรือปรับค่าให้ thread_name

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] กำลังชงกาแฟให้ ลูกค้า {customer_name}...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    start_cpu = process_time()  # กำหนดหรือปรับค่าให้ start_cpu
    sum(i * i for i in range(1000000)) # จำลองงานคำนวณ (CPU-bound) เล็กน้อย และรอ 5 วินาที
    sleep(5) # บล็อกการทำงานของ Thread นี้ไว้ 5 วินาทีเต็มๆ
    cpu_duration = process_time() - start_cpu  # กำหนดหรือปรับค่าให้ cpu_duration
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    # ส่งค่าการกิน RAM และ CPU ของตัวเองกลับไปให้หน่วยหลักผ่าน Queue
    process = psutil.Process(pid)  # กำหนดหรือปรับค่าให้ process
    mem_mb = process.memory_info().rss / (1024 * 1024)  # กำหนดหรือปรับค่าให้ mem_mb
    result_queue.put((mem_mb, cpu_duration))  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก

def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue
    main_pid = os.getpid()  # กำหนดหรือปรับค่าให้ main_pid
    main_tid = threading.current_thread().native_id  # กำหนดหรือปรับค่าให้ main_tid

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] === เริ่มระบบจำลองตู้กาแฟแบบ Multi-processing ===")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time
    main_start_cpu = process_time()  # กำหนดหรือปรับค่าให้ main_start_cpu

    result_queue = multiprocessing.Queue()  # กำหนดหรือปรับค่าให้ result_queue
    processes = []  # กำหนดหรือปรับค่าให้ processes
    # ลูปการทำงาน process
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        # สร้าง Process ใหม่แยกจากกันเด็ดขาด
        p = multiprocessing.Process(target=make_coffee, args=(customer, result_queue))  # กำหนดหรือปรับค่าให้ p
        processes.append(p)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        p.start()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    # รวบรวมข้อมูลทรัพยากรจากทุก Process ย่อย
    child_memories = []  # กำหนดหรือปรับค่าให้ child_memories
    child_cpu_times = []  # กำหนดหรือปรับค่าให้ child_cpu_times
    for _ in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        mem, cpu_t = result_queue.get()  # เรียกใช้บริการหรือส่งคำขอไปยังระบบภายนอก
        child_memories.append(mem)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        child_cpu_times.append(cpu_t)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    for p in processes:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        p.join()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    duration = time() - start_time  # กำหนดหรือปรับค่าให้ duration

    # คำนวณแรมของ Main Process เองด้วย
    main_process = psutil.Process(os.getpid())  # กำหนดหรือปรับค่าให้ main_process
    main_mem = main_process.memory_info().rss / (1024 * 1024)  # กำหนดหรือปรับค่าให้ main_mem

    total_memory = main_mem + sum(child_memories)  # กำหนดหรือปรับค่าให้ total_memory
    total_cpu_time = (process_time() - main_start_cpu) + sum(child_cpu_times)  # กำหนดหรือปรับค่าให้ total_cpu_time

    print(f"[สรุปผล Multi-processing]")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"เวลาที่ใช้จริง (Wall Time): {duration:0.2f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"เวลารวมที่ CPU ทุก Core ช่วยกันประมวลผล (Total CPU Time): {total_cpu_time:0.4f} วินาที")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"ทรัพยากร Memory (RAM) รวมทุก Process: {total_memory:.2f} MB (Main: {main_mem:.2f} MB + ย่อย: {sum(child_memories):.2f} MB)")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน