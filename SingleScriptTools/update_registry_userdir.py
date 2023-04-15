"""
![](Demo_regedit.png)

Script to update all registry entries after changing user directory name.
Primarily intended to be used for Win10 as a stopgap measure before reinstalling.

This script recursively update all affected paths containing *target* keyword
Honestly this would've been better done with usual batchscript, or maybe not.

There is no safety feature in this, use with caution!
"""

import winreg
import itertools
from sys import argv
# from textwrap import shorten

tip = r"""
Simple Script originally designed to change Registry paths recursively.
Recommended to add directory separators on str so it won't catch non-path registries.
There is no type checking, proceed with extreme caution.

Usage:
    RegistryUpdateUser <HKEY> <FOLDER> <FIND_STR> <REPLACE_STR>

Example usage:
    RegistryUpdateUser HKEY_LOCAL_MACHINE SOFTWARE \abc\ \ABC\
"""


def assert_fast():
    # check length first by unpacking
    try:
        _, hkey_name, folder_, find_str, repl_str = argv
    except ValueError as err:
        raise AssertionError("Not enough param") from err

    # Check if HKEY exists, don't cover all possible cases!
    try:
        hkey = getattr(winreg, hkey_name)
    except AttributeError as err:
        raise AssertionError("No such HKEY named", hkey_name)

    # Check if folder exists
    try:
        hkey_root = winreg.OpenKey(hkey, folder_)
    except FileNotFoundError as err:
        raise AssertionError("No such folder or file named", folder_)

    return hkey_root, folder_, find_str, repl_str


def get_keyword():
    target = input("Keyword >> ")
    if input("Confirm? (y/n) >> ") == "y":
        return target

    return get_keyword()


def iterkeys(key, root_path):
    """
    Recursively iterates thru keys, revealing all keys.
    returns absolute path relative to root, and EnumValue result.
    """

    for i in itertools.count():
        try:
            out = winreg.EnumValue(key, i)
        except OSError as err:
            try:
                out = winreg.EnumKey(key, i)
            except OSError as err:  # end of key
                return

            # else it's likely to be a folder. recursively opens it.
            try:
                yield from iterkeys(winreg.OpenKey(key, out), f"{root_path}\\{out}")
            except OSError as err:
                return

        else:
            yield root_path, out


def fetch_list(hkey_root, root_path, find_str):
    counter = 1
    convert_list = []

    for idx, (path_, (name, val, type_)) in enumerate(iterkeys(hkey_root, root_path)):
        if find_str in name or find_str in str(val):
            try:
                val_short = val[:50]
            except TypeError:
                val_short = val

            print(f"Match: {counter:<7} Total: {idx:<10} | {path_[:50]} | {name[:50]} | {val_short}")
            counter += 1
            convert_list.append((path_, name, val))

    return convert_list


def fetch_reg_type_table():
    """
    >>> import winreg

    >>> def a():
    ...     for n_ in [name_ for name_ in dir(winreg) if name_.startswith("REG")]:
    ...         yield n_, getattr(winreg, n_)
    ...

    >>> l = list(a())

    >>> for n_, v in sorted(l, key=lambda x: x[1]):
    ...     print(f"{v}: "{n_}",")
    ...
    """
    table = {0: "REG_NONE",
             1: "REG_SZ",
             3: "REG_BINARY",
             4: "REG_DWORD",
             # 4: "REG_DWORD_LITTLE_ENDIAN",
             5: "REG_DWORD_BIG_ENDIAN",
             6: "REG_LINK",
             7: "REG_MULTI_SZ",
             8: "REG_RESOURCE_LIST",
             9: "REG_FULL_RESOURCE_DESCRIPTOR",
             10: "REG_RESOURCE_REQUIREMENTS_LIST",
             11: "REG_QWORD",
             # 11: "REG_QWORD_LITTLE_ENDIAN",
             }

    return table


def convert_interactively(hkey_root, old_str, new_str, conversion_list, registry_table):
    for idx, (path_, name, val) in enumerate(conversion_list, 1):

        print(hkey_root, path_)
        try:
            context = winreg.OpenKey(hkey_root, path_, 0, winreg.KEY_ALL_ACCESS)
        except PermissionError:
            print(f"Permission error on {path_}, {name}!")
            continue
        except FileNotFoundError as err:
            print(f"Something went wrong!")
            print(err)
            continue

        with context as h_key:

            value, type_ = winreg.QueryValueEx(h_key, name)

            print(f"\n{idx} / {len(conversion_list)}\n"
                  f"Path: {path_}\n"
                  f"Type: {registry_table[type_]}\n"
                  f"From: {val}")

            try:
                converted = value.replace(old_str, new_str)
            except (AttributeError, TypeError) as err:
                print(err)
                print(f"Passing {name}, {val}")
                continue

            print(f"To  : {converted}\n")

            input(f"Press enter to convert this key, or press Ctrl+C to stop.")

            winreg.SetValueEx(h_key, name, 0, type_, value.replace(old_str, new_str))


def main(hkey_root_key, folder_name, find_str, replace_str):

    fetched = fetch_list(hkey_root_key, folder_name, find_str)
    print(f"Fetched {len(fetched)} entries.")

    fetch_reg_types = fetch_reg_type_table()

    convert_interactively(hkey_root_key, find_str, replace_str, fetched, fetch_reg_types)


if __name__ == '__main__':
    try:
        args = assert_fast()
    except AssertionError as err_:
        print(err_)
        print(tip)
    else:
        main(*args)
