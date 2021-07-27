import subprocess
import pathlib
from sys import executable

# install all required packages


def install():
    root = pathlib.Path(__file__).parent
    main_req = root.joinpath("requirements.txt")

    input_ = input("Install these modules? (y/n): ")

    if input_ not in "yY":
        print("Installation canceled.")
        return

    subprocess.check_call([executable, "-m", "pip", "install", "-r", main_req.as_posix()])


if __name__ == '__main__':
    install()
