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


print(f"Naive fibo runtime    : {timeit(lambda: naive_fibo(35), number=100):.8f}", )
print(f"Cached fibo runtime   : {timeit(lambda: cached_naive_fibo(35), number=100):.8f}", )
print(f"Iterative fibo runtime: {timeit(lambda: generator_style_fibo(35), number=100):.8f}", )


"""
Naive fibo runtime    : 66.05947450
Cached fibo runtime   : 0.00002790
Iterative fibo runtime: 0.00007550
"""
