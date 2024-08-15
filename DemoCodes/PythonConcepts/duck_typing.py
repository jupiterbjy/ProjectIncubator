"""
Duck typing demonstrator.

TODO: Add demonstration for iteration method python intelligently chooses
"""

from collections.abc import MutableSequence, Sized


class MyOwnType:
    """
    >>> # Demo of sized class in duck typing
    >>> issubclass(MyOwnType, Sized)
    True
    >>>
    >>> len(MyOwnType())
    1
    """

    def __len__(self):
        return 1


class FakeMutableSequence:
    """Some fake mutable sequence that pretend to be mutable, or even a sequence itself

    >>> issubclass(FakeMutableSequence, MutableSequence)
    True
    >>>
    >>> seq = FakeMutableSequence()
    >>>
    >>> for n in seq:
    ...     print(n)
    0
    1
    4
    9
    16
    >>> seq[0]
    0
    >>> seq[0] = 1
    [FakeMutableSequence] Ha! That was cheap trick too, you neither can set!
    >>> del seq[0]
    [FakeMutableSequence] Ha! That was cheap trick, you can't delete!
    """

    def __getitem__(self, idx):
        if idx < len(self):
            return idx**2

        raise IndexError

    def __delitem__(self, idx):
        print(
            f"[{self.__class__.__name__}] Ha! That was cheap trick, you can't delete!"
        )

    def __setitem__(self, idx, val):
        print(
            f"[{self.__class__.__name__}] Ha! That was cheap trick too, you neither can set!"
        )

    def insert(self, idx, val):
        print(f"[{self.__class__.__name__}] No, not even inserting!")

    def __len__(self):
        return 5
