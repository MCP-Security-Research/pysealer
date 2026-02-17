#!/usr/bin/env python3

# Math example: Fibonacci and Factorial with recursion, async, and a class

import math
import asyncio

def fibonacci(n):
    """Recursive function to compute the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Recursive function to compute factorial of n."""
    if n < 0:
        raise ValueError("Negative values not allowed")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n-1)

async def async_sum_squares(numbers):
    """Async function to sum the squares of a list of numbers."""
    await asyncio.sleep(0.1)  # Simulate async work
    return sum(x*x for x in numbers)

class MathHelper:
    """A class for math utilities."""
    def __init__(self, value):
        self.value = value

    def double(self):
        return 2 * self.value

    def sqrt(self):
        return math.sqrt(self.value)

    @staticmethod
    def is_even(n):
        return n % 2 == 0

def main():
    n = 7
    print(f"Fibonacci({n}) = {fibonacci(n)}")
    print(f"Factorial({n}) = {factorial(n)}")

    numbers = list(range(1, 6))
    print(f"Numbers: {numbers}")
    print("Sum of squares (async):", end=" ")
    result = asyncio.run(async_sum_squares(numbers))
    print(result)

    mh = MathHelper(16)
    print(f"Double of 16: {mh.double()}")
    print(f"Square root of 16: {mh.sqrt()}")
    print(f"Is {n} even? {MathHelper.is_even(n)}")

if __name__ == "__main__":
    main()
