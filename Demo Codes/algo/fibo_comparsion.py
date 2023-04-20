import functools
from timeit import timeit


def naive_fibo(n):
    return 1 if n <= 2 else naive_fibo(n - 2) + naive_fibo(n - 1)


@functools.lru_cache(128)
def cached_naive_fibo(n):
    return 1 if n <= 2 else cached_naive_fibo(n - 2) + cached_naive_fibo(n - 1)


def generator_style_fibo(n):
    a = b = 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


print("Naive fibo runtime    :", timeit(lambda: naive_fibo(30), number=100))
print("Cached fibo runtime   :", timeit(lambda: cached_naive_fibo(30), number=100))
print("Iterative fibo runtime:", timeit(lambda: generator_style_fibo(30), number=100))
