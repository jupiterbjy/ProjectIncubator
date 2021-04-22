import json
from collections.abc import Mapping
from typing import Iterator, Any, Union


def flatten_json(source: Mapping):
    new_dict = {}

    def recursive_search(dict_: dict):
        for key, val in dict_.items():
            pass


class JSONWrapper(Mapping):
    def __init__(self, source: Union[str, dict]):
        self.source = json.loads(source) if isinstance(source, str) else source

    def __getitem__(self, k: str) -> Any:
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[str]:
        pass
