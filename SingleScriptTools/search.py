"""
![](readme_res/search.png)

Searches for lines containing given keyword.
Has options to Filter multiple extensions for searching.

:Author: jupiterbjy@gmail.com
"""

import pathlib
from typing import List, Generator, Tuple


ROOT = pathlib.Path("./")
ENCODINGS = "utf8", "cp949"


RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
END = "\033[0m"


class DecodingError(Exception):
    pass


def colored_input(prompt: str, color: str = YELLOW) -> str:
    return input(color + prompt + END)


def colored_print(text: str, color: str = YELLOW):
    print(color + text + END)


def _read_file(path: pathlib.Path, decode_priority=ENCODINGS) -> str:
    """Reads file and return content as string.
    
    Raises:
        UnicodeDecodingError: on decoding error
    """
    
    for encoding in decode_priority:
        try:
            return path.read_text(encoding)
        
        except UnicodeDecodeError:
            continue
    
    # all attempt failed, throw again with the last encoding
    path.read_text(encoding)


def find_in_file(keyword: str, path: pathlib.Path) -> List[int]:
    """Finds line number where keyword appears in file.
    Returns -1 if keyword is not found.
    Args:
        keyword (str): keyword to search for
        path (pathlib.Path): path to file to search in
    Returns:
        int: line number where keyword appears, or -1 if not found
    
    Raises:
        UnicodeDecodeError: on decoding error
    """
    
    return [
        idx for idx, line in enumerate(_read_file(path).splitlines())
        if keyword in line
    ]


def search_file(
    keyword: str, path: pathlib.Path, ext_whitelist: set
) -> Generator[Tuple[pathlib.Path, List[int]], None, None]:
    """Generator that searches for keyword in files with specified extensions.
    Args:
        keyword (str): keyword to search for.
        path (pathlib.Path): path to search in.
        ext_whitelist (set): Extensions to search for. If empty ignores extension.
    Yields:
        Tuple[pathlib.Path, List[int]: path to file & list of line# where keyword appears.
    """
    
    for path in path.iterdir():
        
        # if path is a directory, recursively search in it
        if path.is_dir():
            yield from search_file(keyword, path, ext_whitelist)
            continue
        
        # if path is not a file we're looking for, skip
        if ext_whitelist and path.suffix not in ext_whitelist:
            continue
        
        try:
            results = find_in_file(keyword, path)
            
        except UnicodeDecodeError:
            # we can't do a shete on encoding errors
            colored_print(f"Failed to read file {path} with encoding {ENCODINGS}", RED)
            continue
        
        if results:
            yield path, results


def get_search_target() -> set:
    raw = colored_input("\nEnter extensions separated by space(blank for all files):\n> ")
    return set(raw.split())


def get_search_target_preset() -> set:
    """Get a set of extensions to search for from a preset list.
    Type 'm' to manually type in extensions."""
    
    ext_set_dict = {
        "all": {},
        "c": {".c", ".h", ".cpp", ".hpp"},
        "py": {".py", ".pyw", ".pyx"},
        "java": {".java", ".class", ".jar", ".jsp"},
        "web": {".html", ".css", ".js", ".ts"},
        "json": {".json", ".yaml", ".yml", ".toml"},
        "text": {".txt", ".md", ".rst"},
        "godot": {".gd", ".gdshader"},
    }
    digits = max(len(name) for name in ext_set_dict.keys())
    
    colored_print("\nSelect extension set index to search for (default all):")
    print(f"{GREEN}m{END} Type yourself")
    
    for i, (name, ext_set) in enumerate(ext_set_dict.items()):
        print(f"{GREEN}{i}{END} {name:{digits}} : {RED}{' '.join(ext_set)}{END}")
    
    _input = 0
    while True:
        raw = colored_input("> ").strip()
        
        match raw:
            case "": break
            case "m": return get_search_target()
        
        try:
            _input = int(raw)
            assert 0 <= _input <= len(ext_set_dict)
        
        except (ValueError, AssertionError):
            continue
        
        break
    
    key = list(ext_set_dict.keys())[_input]
    exts = ext_set_dict[key]
    
    colored_print(f"Extension Filter: {key}", GREEN)
    return exts


def get_search_path() -> pathlib.Path:
    """Get user input for path to search in.
    If blank, return Script path.
    Returns:
        pathlib.Path: path to search in.
    """
    
    colored_print("\nEnter search path (blank for Script path):")
    
    while True:
        path = colored_input("> ")
        if not path:
            break
        
        path = pathlib.Path(path)
        if path.exists():
            break
    
    selected = pathlib.Path(path) if path else ROOT
    colored_print(f"Searching in: {selected.absolute().as_posix()}", GREEN)
    return selected


def main():
    search_path = get_search_path()
    search_extensions = get_search_target_preset()

    while True:
        query = colored_input("\n\nKeyword (q to exit): ")
        if not query:
            continue
        
        if query in "Qq":
            return
        
        for path, line_nos in search_file(query, search_path, search_extensions):
            colored_print(f"\nIn {path.absolute().as_posix()}:", GREEN)
            
            # search for lines in file. Reading file here again cause IDC.
            # QOL > performance
            lines = path.read_text("utf8").splitlines()
            digits = len(str(len(lines)))
            
            for line_no in line_nos:
                print(f"{GREEN} {line_no + 1:0{digits}}|{END}  {lines[line_no]}")
        
        colored_print("\n-- END OF RESULTS --", RED)


if __name__ == "__main__":
    main()