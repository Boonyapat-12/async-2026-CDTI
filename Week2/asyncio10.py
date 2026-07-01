# Program 10: Extracting Return Values from Tasks
# Concept: Accessing returned results from completed Task objects using .result() or direct assignment.

import asyncio

async def calculate_bill(customer, base_price):
    print(f"Calculating bill for {customer}...")
    await asyncio.sleep(2)  # Simulate a delay in calculation
    final_price = base_price * 1.07  # Adding 7% vat
    return final_price

async def main():
    # Create tasks for two customers
    task_a = asyncio.create_task(calculate_bill("A", 100))
    task_b = asyncio.create_task(calculate_bill("B", 200))

    # Await the tasks and get their results
    result_a = await task_a
    result_b = await task_b

    print(f"Final Bill A: ${result_a:.2f}")
    print(f"Final Bill B: ${result_b:.2f}")
    print(f"Total bill: ${result_a + result_b:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
