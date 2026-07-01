from time import sleep, ctime, time


# restaurant_01_simple.py
def greet_diners(customer):
    print(f"{ctime()} Greeting for Customer-{customer} ...")
    sleep(1)
    print(f"{ctime()} Greeting for Customer-{customer} ...Done!")


def take_order(customer):
    print(f"{ctime()} [Customer-{customer}] Taking Order ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Taking Order ...Done!")


def do_cooking(customer):
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Cooking Spaghetti ...Done!")


def mini_bar(customer):
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...")
    sleep(1)
    print(f"{ctime()} [Customer-{customer}] Manage Bar for Drink ...Done!")


def serve_customer(customer):
    take_order(customer)
    do_cooking(customer)
    mini_bar(customer)
    print(f"{ctime()} [Customer-{customer}] All served!")
    print()


def main():
    customers = ["A", "B", "C"]
    start_time = time()

    for customer in customers:
        greet_diners(customer)

    print()
    print(f"{ctime()} --- All customers greeted. Serving customers one by one! ---")
    print()

    for customer in customers:
        serve_customer(customer)

    print(f"{ctime()} Finished Entire Restaurant Operation in {time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()