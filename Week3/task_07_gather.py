# Objective: Group multiple operations to run concurrently and return an ordered list of outputs.
import asyncio
from time import time, ctime

async def fetch_db_record(table_name, latency):
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"

async def main():
    start = time()
    
    # 
    results = await asyncio.gather(
        fetch_db_record("Users", 1.0),
        fetch_db_record("Products", 0.5),
        fetch_db_record("Invoices", 1.0)
    )
    
    print(f"{ctime()} Aggregated Output Results List: {results}")
    print(f"{ctime()} Execution Completed in: {time() - start:.2f} seconds") #

asyncio.run(main())