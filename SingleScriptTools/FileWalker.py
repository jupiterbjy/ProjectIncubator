import pathlib
import itertools
from typing import List, Iterator


class PathWrapper:
    # Considering idx 0 to always be step out!

    def __init__(self, path: str = "./"):
        self.current_path = pathlib.Path(path).absolute()
        self.file_list: List[pathlib.Path] = []
        self.folder_list: List[pathlib.Path] = []

    def step_in(self, idx: int) -> pathlib.Path:
        try:
            self.current_path = self.folder_list[idx]
        except IndexError as err:
            raise NotADirectoryError("Cannot step inside non-directory!") from err
        self.refresh_list()
        return self.current_path

    def refresh_list(self):
        self.file_list.clear()
        self.folder_list.clear()

        self.folder_list.append(self.current_path.parent)

        self.file_list.extend(dir_ for dir_ in self.current_path.iterdir() if dir_.is_file())
        self.folder_list.extend(dir_ for dir_ in self.current_path.iterdir() if dir_.is_dir())

    def return_strings(self) -> Iterator:
        directory = [f"DIR| {dir_.stem}" for dir_ in self.folder_list]
        directory[0] = "DIR| .."

        files = (f"FIL| {file.name}" for file in self.file_list)

        return itertools.chain(directory, files)

    def __len__(self) -> int:
        return len(self.folder_list) + len(self.file_list)

    def __getitem__(self, item: int) -> pathlib.Path:
        # index order is folder, followed by files
        try:
            return self.folder_list[item]
        except IndexError as err:
            if len(self) == 0:
                raise IndexError("No file or folder in current directory.") from err

            return self.file_list[item - len(self.folder_list)]
