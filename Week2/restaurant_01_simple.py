from time import sleep, ctime, time  # นำเข้าส่วนประกอบที่ต้องใช้จากโมดูลที่ระบุ


# restaurant_01_simple.py
def greet_diners(customer):  # ประกาศฟังก์ชัน greet_diners สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} Greeting for Customer-{customer} ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} Greeting for Customer-{customer} ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def take_order(customer):  # ประกาศฟังก์ชัน take_order สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} [Customer-{customer}] Taking Order ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Customer-{customer}] Taking Order ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def do_cooking(customer):  # ประกาศฟังก์ชัน do_cooking สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def mini_bar(customer):  # ประกาศฟังก์ชัน mini_bar สำหรับรวมขั้นตอนการทำงาน
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    sleep(1)  # รอหรือจำลองระยะเวลาการทำงานตามค่าที่กำหนด
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...Done!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def serve_customer(customer):  # ประกาศฟังก์ชัน serve_customer สำหรับรวมขั้นตอนการทำงาน
    take_order(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    do_cooking(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    mini_bar(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน
    print(f"{ctime()} [Customer-{customer}] All served!")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print()  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


def main():  # ประกาศฟังก์ชัน main สำหรับรวมขั้นตอนการทำงาน
    customers = ["A", "B", "C"]  # กำหนดหรือปรับค่าให้ customers
    start_time = time()  # กำหนดหรือปรับค่าให้ start_time

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        greet_diners(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    print()  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print(f"{ctime()} --- All customers greeted. Serving customers one by one! ---")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ
    print()  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ

    for customer in customers:  # วนซ้ำเพื่อประมวลผลข้อมูลทีละรายการ
        serve_customer(customer)  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน

    print(f"{ctime()} Finished Entire Restaurant Operation in {time() - start_time:.2f} seconds.")  # แสดงข้อมูลหรือผลลัพธ์ออกทางหน้าจอ


if __name__ == "__main__":  # ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือถูก import
    main()  # ดำเนินคำสั่งของบรรทัดนี้ตามลำดับการทำงาน