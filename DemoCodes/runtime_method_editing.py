"""
Demonstrates method editing in runtime
"""

from pprint import pprint
import traceback


class SomeClass:
    """SomeDocstring"""

    some_class_attr = "I love shinku"


instance = SomeClass()


# add __getattr__ that return param name as-is
def return_to_sender(_self, arg):
    return arg


# note that we're adding callable to CLASS, NOT INSTANCE
SomeClass.__getattr__ = return_to_sender

# now we see that in namespace, also that 'SomeDocstring' and some_class_attr.
pprint(SomeClass.__dict__)
r"""
mappingproxy({'__dict__': <attribute '__dict__' of 'SomeClass' objects>,
              '__doc__': 'SomeDocstring',
              '__getattr__': <function return_to_sender at 0x000001B5AC9A8A40>,
              '__module__': '__main__',
              '__weakref__': <attribute '__weakref__' of 'SomeClass' objects>,
              'some_class_attr': 'I love shinku'})
"""

# test access
print(instance.nonexistent_param)
r"""
nonexistent_param
"""

# remove access
del SomeClass.__getattr__

# test access
try:
    print(instance.nonexistent_param)
except AttributeError:
    print(traceback.format_exc())
r"""
Traceback (most recent call last):
  File "E:\github\ProjectIncubator\DemoCodes\runtime_method_editing.py", line 48, in <module>
    print(instance.nonexistent_param)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'SomeClass' object has no attribute 'nonexistent_param'
"""
