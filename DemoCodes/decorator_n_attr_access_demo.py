"""
Demonstration of attribute access behavior with decorators
"""

from typing import Any, Callable
import functools


"""
Decorators are used to 'decorate' callables and either extend or alter behavior.

For example, we can define a decorator like:
```
func some_deco(func):
    def wrapper(*args, **kwargs):
        # do something
        return func(*args, **kwargs)
    return wrapper

@some_deco
def some_func():
    pass

# equivalent to:
some_func = some_deco(some_func)
```

Or can make it accept arguments
```
def some_deco(arg1, arg2):
    def runtime_created_decorator(func):
        def wrapper(*args, **kwargs):
            # do something
    
    return runtime_created_decorator

@some_deco(arg1, arg2)
def some_func():
    pass

# equivalent to:
some_func = some_deco(arg1, arg2)(some_func)
```

Decorators demonstrate functions are first-class citizen and can be created in runtime.
Also demonstrates how to use `functools.wraps` to preserve callable's name and docstring.
"""


def debug_method_deco(func: Callable) -> Callable[..., Any]:
    """
    Decorate function to print caller name with call params.

    Args:
        func: Function to be decorated

    Returns:
        Decorated(wrapped) function
    """

    blacklist: set[str] = {"__dict__", "__slots__", "print_instance_namespace"}

    # `functools.wraps` is a decorator that preserves callable's name and docstring.
    # otherwise decorated functions' name would be `wrapper` without docstring
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):

        # ignore if it's __dict__ or __slots__ since we'll access it below
        if args and args[0] in blacklist:
            return func(self, *args, **kwargs)

        # else print verbose
        print(
            f"<{func.__name__}> called with:\n"
            f"  └ Positional args: {(self, *args)}"
            # f"  └ Keyword args: {kwargs}"
        )
        return func(self, *args, **kwargs)

    return wrapper


def colored_print(*args, color="yellow", **kwargs) -> None:
    """ANSI color print"""

    color_code = {
        "yellow": "\033[33m",
        "red": "\033[31m",
        "green": "\033[32m",
        "cyan": "\033[36m",
        "reset": "\033[0m",
    }

    print(color_code[color], end="")
    print(*args, **kwargs)
    print(color_code["reset"], end="")


# vvvv Despite NOT inherited, all class inherite from `object` implicitly.
# This is because of Python2 -> Python3 migration.
# This is similar with how godot inherit from `RefCounted`.
class VerboseClass:
    """
    Demonstration class for how attribute access happens.

    Refer following for details on `__get__`, `__getattribute__` & `__getattr__`:
    https://stackoverflow.com/a/25808799/10909029
    """

    @debug_method_deco
    def __getattribute__(self, name):
        return super().__getattribute__(name)

    @debug_method_deco
    def __getattr__(self, name) -> Any:
        """
        Called when NO attribute exists, used to 'compute' attribute

        Hence, this should either compute value or raise AttributeError.
        """

        if name == "fox":
            return "hentai"

        raise AttributeError(f"'VerboseClass' object has no attribute '{name}'")

    @debug_method_deco
    def __setattr__(self, name, value):
        """Called when attribute exists, used to 'update' attribute"""
        super().__setattr__(name, value)

    def print_instance_namespace(self):
        colored_print(f"{self} namespace:", self.__dict__, color="cyan")

    @debug_method_deco
    def some_func(self, *args, **kwargs):
        return args, kwargs


# --- Test ---

import traceback


a = VerboseClass()

colored_print(">>> a.fox")
colored_print(a.fox, end="\n\n", color="green")


colored_print(">>> a.not_fox")
a.print_instance_namespace()
try:
    a.not_fox
except AttributeError as err:
    colored_print(traceback.format_exc(), end="\n\n", color="red")
    # note that `__getattribute__` is called with "__class__" to get class for traceback


colored_print(">>> a.not_fox = 10")
a.not_fox = 10
a.print_instance_namespace()
print(end="\n\n")


colored_print(">>> a.not_fox")
a.print_instance_namespace()
colored_print(a.not_fox, end="\n\n\n", color="green")


colored_print('>>> a.some_func("some_positional_arg", some_keyword_arg="I love hina")')
colored_print(
    a.some_func("some_positional_arg", some_keyword_arg="I love hina"),
    end="\n\n\n",
    color="green",
)


# can't replace dunder method in func but still can call it manually
colored_print(
    '>>> a.some_func.__call__("some_positional_arg", some_keyword_arg="I love hina")'
)
colored_print(
    a.some_func.__call__("some_positional_arg", some_keyword_arg="I love hina"),
    end="\n\n\n",
    color="green",
)


r"""
>>> a.fox
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'fox')
<__getattr__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'fox')
hentai

>>> a.not_fox
<__main__.VerboseClass object at 0x000001BD8FF414C0> namespace: {}
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'not_fox')
<__getattr__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'not_fox')
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, '__class__')
Traceback (most recent call last):
  File "E:\github\ProjectIncubator\DemoCodes\decorator_and_attr_access_demo.py", line 154, in <module>
    a.not_fox
  File "E:\github\ProjectIncubator\DemoCodes\decorator_and_attr_access_demo.py", line 78, in wrapper
    return func(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\github\ProjectIncubator\DemoCodes\decorator_and_attr_access_demo.py", line 125, in __getattr__
    raise AttributeError(f"'VerboseClass' object has no attribute '{name}'")
AttributeError: 'VerboseClass' object has no attribute 'not_fox'


>>> a.not_fox = 10
<__setattr__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'not_fox', 10)
<__main__.VerboseClass object at 0x000001BD8FF414C0> namespace: {'not_fox': 10}


>>> a.not_fox
<__main__.VerboseClass object at 0x000001BD8FF414C0> namespace: {'not_fox': 10}
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'not_fox')
10


>>> a.some_func("some_positional_arg", some_keyword_arg="I love hina")
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'some_func')
<some_func> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'some_positional_arg')
(('some_positional_arg',), {'some_keyword_arg': 'I love hina'})


>>> a.some_func.__call__("some_positional_arg", some_keyword_arg="I love hina")
<__getattribute__> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'some_func')
<some_func> called with:
  └ Positional args: (<__main__.VerboseClass object at 0x000001BD8FF414C0>, 'some_positional_arg')
(('some_positional_arg',), {'some_keyword_arg': 'I love hina'})
"""
