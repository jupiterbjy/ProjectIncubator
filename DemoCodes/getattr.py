"""
Demonstraction of __getattr__'s behavior, used in LoggingConfigurator.py

>>> instance = A()

>>> instance.this_attr_doesnt_exist(30)
'calling: this_attr_doesnt_exist(30)'
"""


class A:
    def __getattr__(self, item):
        return lambda x: f"calling: {item}({x})"


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
