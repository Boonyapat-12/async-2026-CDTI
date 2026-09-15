from time import sleep, ctime, time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ
import threading  # นำเข้าโมดูลที่จำเป็นสำหรับโปรแกรม

def greet_diners(customer):  # ประกาศฟังก์ชัน greet_diners สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} -> Greeting for customer-{customer} ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

def customer_private_workflow(customer):  # ประกาศฟังก์ชัน customer_private_workflow สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    print(f"{ctime()} [Thread-{customer}] -> Cooking ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Thread-{customer}] -> Cooking ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    customers = ["A", "B", "C"]  # กำหนดหรือปรับค่าให้ customers

    start_time = time()  # กำหนดหรือปรับค่าให้ start_time

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        greet_diners(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    
    print(f"{ctime()} --- All customers greeted, FORKING into independent processes for each customer ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    processes = []  # กำหนดหรือปรับค่าให้ processes

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        t = threading.Thread(target=customer_private_workflow, args=(customer,))  # กำหนดหรือปรับค่าให้ t
        t.start()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
        processes.append(t)  # เพิ่มหรือปรับปรุงข้อมูลในโครงสร้างข้อมูล

    for t in processes:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        t.join()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    print(f"Total Operation time: {time() - start_time:.2f} seconds")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ