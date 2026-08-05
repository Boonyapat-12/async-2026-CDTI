import asyncio
import time

@app.get("/sync-blocking")
async def blocking_endpoint():
    time.sleep(10)  # Simulate a blocking operation
    return {"message": "Done"}

