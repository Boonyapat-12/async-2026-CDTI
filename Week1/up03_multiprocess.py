from time import sleep, ctime, perf_counter  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import multiprocessing  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม


def log(message):  # ประกาศฟังก์ชัน log สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} | {message}", flush=True)  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def update_cup_number(customer_name):  # ประกาศฟังก์ชัน update_cup_number สำหรับรวมขั้นตอนการทำงาน
    log(f"LCD: Processing for customer {customer_name}...")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    log(f"LCD: Done for customer {customer_name}.")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


def make_coffee(customer_name):  # ประกาศฟังก์ชัน make_coffee สำหรับรวมขั้นตอนการทำงาน
    log(f"Making coffee for {customer_name}...")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    log(f"Coffee ready for {customer_name}!")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    update_cup_number(customer_name)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    queue = ['A', 'B', 'C']  # กำหนดหรือปรับค่าให้ queue

    log("=== Multi-processing Coffee Machine ===")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    start_time = perf_counter()  # กำหนดหรือปรับค่าให้ start_time

    processes = []  # กำหนดหรือปรับค่าให้ processes
    for customer in queue:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        p = multiprocessing.Process(target=make_coffee, args=(customer,))  # กำหนดหรือปรับค่าให้ p
        processes.append(p)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล
        p.start()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    for p in processes:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        p.join()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    duration = perf_counter() - start_time  # กำหนดหรือปรับค่าให้ duration
    log(f"Total time: {duration:0.2f} seconds")  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
