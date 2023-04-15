import inspect


"""
Python 3.9.1 (tags/v3.9.1:1e5d33e, Dec  7 2020, 17:08:21) [MSC v.1927 64 bit (AMD64)] on win32

Doctest of extracting outer, or current scope name on both async/sync colored functions.
Not sure if asyncio also does same for this case.
"""


def inspect_outer():
    caller = inspect.stack()
    return caller


def wrapper():
    return inspect_outer()


async def inspect_outer_async():
    caller = inspect.stack()
    return caller


async def wrapper_async():
    return await inspect_outer_async()


# Tests ----------------------------------------

def test_normal_functions():
    """
    >>> stack = wrapper()

    >>> stack[0][3]
    'inspect_outer'

    >>> stack[1][3]
    'wrapper'
    """


def test_async_functions():
    """
    >>> import trio

    >>> stack = trio.run(wrapper_async)

    >>> stack[0][3]
    'inspect_outer_async'

    >>> stack[1][3]
    'wrapper_async'
    """


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
