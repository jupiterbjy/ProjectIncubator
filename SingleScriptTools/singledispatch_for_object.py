"""
Mimics functools.singledispatch, but for objects.
usage is also almost identical.
"""

from functools import wraps


def obj_dispatch(func):
    # I do aware A().__class__ and type(A) may differ for some proxy classes.
    # But I'm not counting those in for now.
    # TODO: utilize weakref to allow gc.

    func.dispatch_list = {}

    @wraps(func)
    def wrapper(target, *args, **kwargs):
        nonlocal func
        try:
            # try with class type of the target.
            return func.dispatch_list[type(target)](target, *args, **kwargs)
        except KeyError:
            try:
                # If error, it might be definition of class and __class__ is pointing superclass 'type'.
                # Not sure using key value to argument is any use, but it's an edge case anyway.
                return func.dispatch_list[target](target, *args, *kwargs)
            except KeyError:
                return func(target, *args, *kwargs)

    def register(registering_object_type):
        # A decorator that does same job like functools.singledispatch register.
        def register_deco(registering_func):
            nonlocal func
            func.dispatch_list[registering_object_type] = registering_func

            def register_inner(*args, **kwargs):
                return func(*args, **kwargs)

            return register_inner
        return register_deco

    wrapper.register = register

    return wrapper


if __name__ == '__main__':
    def doctest():
        """
        >>> class A:
        ...     pass

        >>> class B:
        ...     pass

        >>> @obj_dispatch
        ... def dispatch_main(target, *args, **kwargs):
        ...     print('on main', target, args, kwargs)

        >>> @dispatch_main.register(A)
        ... def a(*args):
        ...     print("a", args)

        >>> dispatch_main(A, 20, 30)
        a (<class '__main__.A'>, 20, 30)

        >>> dispatch_main(A(), 20, 30)
        a (<__main__.A object at 0x0000029CC0BFE940>, 20, 30)

        >>> dispatch_main(B , 20, 30)
        on main <class '__main__.B'> (20, 30) {}
        """
