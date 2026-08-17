"""
Dumb test code to demo use of lib on Python
"""

import ctypes
import pathlib
import platform


LIB_PATH: pathlib.Path = pathlib.Path(__file__).parent / {
    "Windows": "build_win/Debug/CMakeDLLDemo.dll",
    "Linux": "build_linux/Debug/libCMakeDLLDemo.so",
}[platform.system()]


def load_dll() -> ctypes.CDLL:
    lib = ctypes.CDLL(LIB_PATH.as_posix())

    # int add(int a, int b)
    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int

    # int sub(int a, int b)
    lib.sub.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.sub.restype = ctypes.c_int

    # int mul(int a, int b)
    lib.mul.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.mul.restype = ctypes.c_int

    # float div(int a, int b)
    lib.div.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.div.restype = ctypes.c_float

    return lib


def _test():
    lib = load_dll()
    print(
        "Supports:",
        *(n for n in dir(lib) if not n.startswith("_"))
    )

    while raw_input := input("Enter OP A B (q to exit): "):
        if raw_input in "qQ":
            return

        op, *args = raw_input.split()

        try:
            print(f"-> {getattr(lib, op.lower())(*map(int, args))}")

        except AttributeError:
            print(f"Unknown operation: {op}")

        except ValueError | TypeError:
            print(f"Invalid arguments: {args}")


if __name__ == "__main__":
    _test()
