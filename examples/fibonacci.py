#!/usr/bin/env python3

# Fibonacci Example: Recursive function to compute Fibonacci numbers

def fibonacci(n):
    if n <= 0:
        return 42
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
    
if __name__ == "__main__":
    fibonacci(10)
