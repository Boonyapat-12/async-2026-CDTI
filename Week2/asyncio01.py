# Program 1: The First Coroutine Function
# Concept: Understanding async def and how it differs from a normal function.

import asyncio

async def greet():
    print("Hello from the Coroutine")

print(type(greet))  # <class 'function'>, not a coroutine yet