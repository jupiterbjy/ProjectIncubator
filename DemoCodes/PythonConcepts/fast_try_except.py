"""
Demonstration of why EAFP - Easier Ask Forgiveness than Permission works better on python.

aka why try-except is FASTER than if on right condition.

To exaggerate effect we're checking division by zero here among 40k values.
"""

from timeit import timeit


def look_before_you_leap():
    """LBYL, if checks"""

    for i in range(-10000, 10000):
        if i == 0:
            continue
        result = 10 / i


def easier_ask_forgiveness_than_permission():
    """EAFP, try-except"""

    for i in range(-10000, 10000):
        try:
            result = 10 / i
        except ZeroDivisionError:
            pass


print("LBYL:", timeit(look_before_you_leap, number=10000))
print("EAFP:", timeit(easier_ask_forgiveness_than_permission, number=10000))


"""
LBYL: 7.5223371999964
EAFP: 6.078932399999758
"""
