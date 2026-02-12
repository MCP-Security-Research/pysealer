#!/usr/bin/env python3

# Fibonacci Example: Recursive function to compute Fibonacci numbers

import pysealer

@pysealer._3aS24szWmg3jv3RcgS9Z5P2f4ES89CdDTMotYbVcq9AhMupqDghHwu9i82UPFcGnhtNbA9q8T9fkwNmrhexyK8PY()
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
    
if __name__ == "__main__":
    fibonacci(10)
