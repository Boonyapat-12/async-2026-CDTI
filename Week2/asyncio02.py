# Program 2: The Coroutine Object
# Concept: Seeing that calling an async def function creates an "Object" but does not execute it yet.

import asyncio

async def greet():
    print("Hello!")

coro_object = greet()  # Create a Coroutine Object
print(type(coro_object))  # <class 'coroutine'>, not executed yet
coro_object.close() # Close the coroutine object to free resources

