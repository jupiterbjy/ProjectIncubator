import time
from contextlib import contextmanager


@contextmanager
def measure_time(name: str):
    print(f"[{name}] Start measuring time")
    start_time = time.monotonic()
    yield
    print(f"[{name}] Time taken: {time.monotonic() - start_time} secs")


def ham(func):
    def wrapper():
        func()

        with measure_time("Deco:ham"):
            time.sleep(5)

    return wrapper


def egg(func):
    def wrapper():
        func()

        with measure_time("Deco:egg"):
            time.sleep(3)

    return wrapper


@egg
@ham
def foo():
    print("[foo] In foo")
    return


if __name__ == '__main__':
    foo()
