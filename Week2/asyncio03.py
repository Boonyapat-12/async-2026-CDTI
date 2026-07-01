# Program 3: The Event Loop (asyncio.run)
# Concept: Using the Event Loop to actually execute a Coroutine Object.
import asyncio

async def greet():
    print("Hello From the Event Loop!")

if __name__ == "__main__":
    coro_object = greet()  # Create a Coroutine Object

    
    asyncio.run(coro_object)  # Run the Coroutine Object using the Event Loop