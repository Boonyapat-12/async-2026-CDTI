from time import sleep, ctime, time
import multiprocessing

def greet_diners(customer):
    print(f"{ctime()} -> Greeting for customer-{customer} ...")
    sleep(1)
    print(f"{ctime()} -> Greeting for customer-{customer} ...Done!")

def customer_private_workflow(customer):
    print(f"{ctime()} [Process-{customer}] -> Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Taking Order ...Done!")

    print(f"{ctime()} [Process-{customer}] -> Cooking ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Cooking ...Done!")

    print(f"{ctime()} [Process-{customer}] -> Mini bar ...")
    sleep(1)
    print(f"{ctime()} [Process-{customer}] -> Mini bar ...Done!")

if __name__ == "__main__":
    customers = ["A", "B", "C"]

    start_time = time()

    for customer in customers:
        greet_diners(customer)
    
    print(f"{ctime()} --- All customers greeted, FORKING into independent processes for each customer ...")

    processes = []

    for customer in customers:
        p = multiprocessing.Process(target=customer_private_workflow, args=(customer,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print(f"Total Operation time: {time() - start_time:.2f} seconds")