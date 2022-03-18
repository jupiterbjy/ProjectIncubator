try:
    from .some_submodule import SomeClass
except ImportError:
    # attempted relative import with no known parent package
    # because this is running as main script, there's no parent package.
    from some_submodule import SomeClass

    # now since we don't have parent package, we just append the path.
    from sys import path
    import pathlib
    path.append(pathlib.Path(__file__).parent.parent.as_posix())

    print("Importing module_in_parent_dir from sys.path")
else:
    print("Importing module_in_parent_dir from working directory")

# Now either case we have parent directory of `module_in_parent_dir`
# in working dir or path, we can import it

# might need to suppress false IDE warning this case.
# noinspection PyUnresolvedReferences
from module_in_parent_dir import SomeOtherClass
