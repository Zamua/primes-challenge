"""
Prime numbers module
"""

import redis

def primes(lo, hi):
    """ Return all prime numbers between lo (inclusive) and hi (inclusive). """

    primes = []

    n = next_prime(lo - 1, hi)

    while n is not None and n <= hi:
        primes.append(n)
        n = next_prime(n, hi)

    return primes

def next_prime(lo, hi):
    """ Return the smallest prime number such that lo < p <= hi. """

    n = lo + 1
    while n <= hi:
        if is_prime(n):
            return n
        n += 1

    return None

def is_prime(n):
    """ Return True if n is prime, and false otherwise. """

    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False

    # A simple optimization to only check for numbers of the form 6k+1/6k-1
    i = 6
    while i * i <= n:
        if n % i - 1 == 0 or n % i + 1 == 0:
            return False
        i += 6

    return True
