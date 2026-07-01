from time import sleep, ctime, time
import threading

def greet_diners(customer):
    print(f"{ctime()} -> Greeting for customer-{customer} ...")
    sleep(1)
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")

def customer_private_workflow(customer):
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Taking Order ...Done!")

    print(f"{ctime()} [Thread-{customer}] -> Cooking ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Cooking ...Done!")

    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...")
    sleep(1)
    print(f"{ctime()} [Thread-{customer}] -> Mini bar ...Done!")

if __name__ == "__main__":
    customers = ["A", "B", "C"]

    start_time = time()

    for customer in customers:
        greet_diners(customer)
    
    print(f"{ctime()} --- All customers greeted, FORKING into independent processes for each customer ...")

    processes = []

    for customer in customers:
        t = threading.Thread(target=customer_private_workflow, args=(customer,))
        t.start()
        processes.append(t)

    for t in processes:
        t.join()

    print(f"Total Operation time: {time() - start_time:.2f} seconds")