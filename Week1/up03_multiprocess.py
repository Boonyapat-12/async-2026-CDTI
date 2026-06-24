from time import sleep, ctime, perf_counter
import multiprocessing


def log(message):
    print(f"{ctime()} | {message}", flush=True)


def update_cup_number(customer_name):
    log(f"LCD: Processing for customer {customer_name}...")
    sleep(1)
    log(f"LCD: Done for customer {customer_name}.")


def make_coffee(customer_name):
    log(f"Making coffee for {customer_name}...")
    sleep(1)
    log(f"Coffee ready for {customer_name}!")
    update_cup_number(customer_name)


def main():
    queue = ['A', 'B', 'C']

    log("=== Multi-processing Coffee Machine ===")
    start_time = perf_counter()

    processes = []
    for customer in queue:
        p = multiprocessing.Process(target=make_coffee, args=(customer,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    duration = perf_counter() - start_time
    log(f"Total time: {duration:0.2f} seconds")


if __name__ == "__main__":
    main()
