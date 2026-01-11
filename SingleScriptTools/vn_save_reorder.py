"""
`WARNING: NOT SUFFICIENTLY TESTED, BACKUP FIRST`

Script to 'compact' order of save files in various visual novels.

Basically generalized version of `favorite_save_file_reorder_▽.py` that attempts to autodetect method,
based on save file naming.

e.g. compacting save file range of 1~30 would compacts `(2, 3, 6, 12, 28)` to `(1, 2, 3, 4, 5)`.

```text
# FavoriteStrategy:
Desc: FAVORITE's VN save file rename strategy
Type: 03 pad / 1-start
e.g.: s001.bin (s{idx:03}.bin)
Note: Do not temper with s800(for iroseka) & s901~s906 files.
Used: Irotoridori no Sekai, Sakura Moyu, Hoshizora no Memoria

# KiriKiriPagedStrategy:
...

# KonosoraENG:
Desc: PULLTOP's Konosora ENG save file rename strategy
Type: 03 padding / 1-start / separate thumbnail
e.g.: 'Save001.Konosora EnglishSave-WillPlus', Save001.png
Note: _
Used: If my heart had wings (Konosora ENG)

Strategy KonosoraENG selected.
Save start idx: >? 1
Save end idx: >? 63

Save038.Konosora EnglishSave-WillPlus -> Save001.Konosora EnglishSave-WillPlus
Save038.png -> Save001.png
...
Save061.Konosora EnglishSave-WillPlus -> Save023.Konosora EnglishSave-WillPlus
Save061.png -> Save023.png
Save062.Konosora EnglishSave-WillPlus -> Save024.Konosora EnglishSave-WillPlus
Save062.png -> Save024.png
Proceed? (y/N): y

...
```

Though beware, ALWAYS backup first.

Currently supported formats:
- FAVORITE
  - All: `s001.bin`

- YUZUSOFT/Madosoft, KiriKiri-engine page based:
  - All: `data_0001_01.jpg`

- PULLTOP:
  - If my heart had wings(Konosora) ENG: `Save001.png` & `Save001.Konosora EnglishSave-WillPlus`

- ~~AsaProject's recent works: (e.g. `renrowa51.bmp`, `sukitosuki51.bmp`)~~
  - For god's sake what kind of system are they even using...

I can't figure out why and how to make it work for ASAProject, as I can't figure out the general
mechanism at all - image files purely serve as thumbnail and no more.

:Author: jupiterbjy@gmail.com
"""

import re
import itertools
import pathlib
import argparse
from collections.abc import Sequence

"""
# old: 1~240 Save / 241~252 AS / 901~906 system
# new_iroseka: 1~480 Save / 481~492 AS / 800 ? / 901~906 system, 12 per page
# new_hoshimemo: 1~800 Save / 801~810 AS / 901~906 system, 10 per page
# sakumoyu: 1~360 Save / 361~368 AS / 901~906 system, 8 per page
_STRAT: FAVORITE / 03 pad / 1-start
favorite/iroseka: s001.bin (s{idx:03}.bin)
favorite/sakumoyu: ==
favorite/hoshimemo: ==
favorite/hoshimemo-eh: ==
favorite/irohika: ==
favorite/akahito: ==

_STRAT: KIRIKIRI_PAGED / 04 pad / 1-start / 02 pad paged / 12 per page
yuzu/senrenbanka: data_0001_12.jpg (data_{page:04}_{order_in_page:02}.jpg)
yuzu/sanobawitch: ==
yuzu/riddlejoker: ==
yuzu/cafestella: ==
mado/wagahigh: ==
yuzu/angelic chaos: ==

_START: KIRIKIRI_PAGED_VOICE / 04 pad / 1-start
yuzu/riddlejoker: data_voice_0001_12.jpg (data_voice_{page:04}_{order_in_page:02}.jpg)
yuzu/cafestella: ==
yuzu/angelic chaos: ==

_STRAT: KIRIKIRI_NOPAGE / no padding / 1-start
whitepowder/lamunation: data1.bmp (data_{idx:04}.bmp)

_STRAT: ARTEMIS / 04 pad / 1-start
saga/hatsuyuki: save0001.dat (save{idx:04}.dat) & save0001.png (save{idx:04}.png)
asarashi/amanatsu: ==

_STRAT: GENERIC_DATA_UNPADDED_0START / no padding / 0-start
pallete/nine_kokoiro: data1.bmp (data{idx}.bmp)
pallete/nine_sorairo: data1.bmp (data{idx}.bmp)

_STRAT: UNITY / 03 pad / 0-start
sprite/aokana: AoKana035.bmp (AoKana{idx:03}.bmp)
saga/kinkoi: Kinkoi001.dat (Kinkoi{idx:03}.dat)

# old asa games like sangaku renai doesn't have page system and starts like 9-nine-.
# 0~2: System usage? / 11~22: Quicksave / 31~42: Autosave / 51~: Saves, hence 1-start.
_STRAT: ASAPROJECT_NEW / no padding / 51-start
asa/renairoyal: renrowa51.bmp (renrowa{idx}.bmp)
asa/koikari: sukitosuki51.bmp (sukitosuki{idx}.bmp)

# wtf is this suffix...
_STRAT: PULLTOP_KONOSORA_ENG / 03 pad / 1-start
pulltop/konosora_english: "Save001.Konosora EnglishSave-WillPlus"
pulltop/konosora_english: Save001.png
"""


class RenameStrategyBase:
    """
    Desc: NOT_SET
    Type: NOT_SET
    e.g.: NOT_SET
    Note: NOT_SET
    Used: NOT_SET
    """

    @classmethod
    def condition(cls, files: list[pathlib.Path]) -> bool:
        """Returns True if strategy can be applied.
        Files will be entire folder content of save directory, hence implement
        various filtering as required. (e.g. extensions, etc.)
        """

        raise NotImplementedError

    @classmethod
    def rename(cls, files: list[pathlib.Path]) -> None:
        """Renames save files. Passed files are sorted.
        One must receive user input to determine start-end index.
        This is due to some VNs using the paged naming system."""

        raise NotImplementedError

    @staticmethod
    def _get_range_non_paged() -> tuple[int, int]:
        """Receive save file order compress range from user.

        Raises:
            AssertionError: if start index is larger than end index

        Returns:
            (logical_start_idx, logical_end_idx)
        """

        start = int(input("Save start idx: "))
        end = int(input("Save end idx: "))

        assert start < end, "Start index must be smaller than end index"

        return start, end

    @staticmethod
    def _get_range_paged() -> tuple[tuple[int, int], tuple[int, int]]:
        """Receive save file order compress range from user.

        Raises:
            AssertionError: if start save/page index is larger than corresponding ends.

        Returns:
            (start(page, idx_in_page), end(page, idx_in_page))))
        """

        start_page, start_idx = map(
            int, input("Start page & idx (page-idx, e.g. 12-4): ").split("-")
        )
        end_page, end_idx = map(int, input("End page & idx: ").split("-"))

        assert start_page < end_page, "Start page must be smaller than end page"

        return (start_page, start_idx), (end_page, end_idx)

    @staticmethod
    def _condition_generic(
        files: Sequence[pathlib.Path], ext: str, pattern: re.Pattern
    ) -> bool:
        """Apply generic filter for files with given extension and regex pattern.
        Will return True on the first valid file, otherwise False.
        """

        for file in files:
            if file.suffix != ext:
                continue

            if pattern.match(file.name):
                return True

        return False

    @staticmethod
    def _filter_generic(
        files: Sequence[pathlib.Path], ext: str, pattern: re.Pattern
    ) -> dict[int, pathlib.Path]:
        """Apply generic filter for files with given extension and regex pattern.
        Pattern's first capture group must capture index.

        Returns:
            {save_idx: file_path}
        """

        # apply ext filter
        _temp = [file for file in files if file.suffix == ext]

        # apply pattern filtering & idx extraction
        valid_files: dict[int, pathlib.Path] = {}

        for file in files:
            matched = pattern.match(file.name)
            if matched:
                valid_files[int(matched[1])] = file

        return valid_files

    @staticmethod
    def _filter_paged(
        files: Sequence[pathlib.Path],
        ext: str,
        pattern: re.Pattern,
    ) -> dict[tuple[int, int], pathlib.Path]:
        """Apply generic filter for files with given extension and regex pattern.
        Pattern's first capture group must capture page, second must capture index in page.

        Returns:
            {(page, idx_in_page): file_path}
        """

        # apply pattern filtering & idx extraction
        valid_files: dict[tuple[int, int], pathlib.Path] = {}

        for file in files:
            if file.suffix != ext:
                continue

            matched = pattern.match(file.name)
            if matched:
                valid_files[(int(matched[1]), int(matched[2]))] = file

        return valid_files

    @staticmethod
    def _rename_on_confirmation(
        old_new_path_pairs: list[tuple[pathlib.Path, pathlib.Path]],
    ) -> None:
        """Get user confirmation for renaming & perform renaming."""

        print("\n")
        print(
            *(f"{old.name} -> {new.name}" for old, new in old_new_path_pairs), sep="\n"
        )

        if input("\nProceed? (y/N): ") in "yY":
            for old, new in old_new_path_pairs:
                old.rename(new)

            print("Renamed successfully.")
            return

        print("Rename canceled.")


MAPPING: list[RenameStrategyBase] = []


def _register_strat(cls: RenameStrategyBase) -> RenameStrategyBase:
    """Decorator to register strategy because I'm lazy"""

    MAPPING.append(cls)
    return cls


@_register_strat
class FavoriteStrategy(RenameStrategyBase):
    """
    Desc: FAVORITE's VN save file rename strategy
    Type: 03 pad / 1-start
    e.g.: s001.bin (s{idx:03}.bin)
    Note: Do not temper with s800(for iroseka) & s901~s906 files.
    Used: Irotoridori no Sekai, Sakura Moyu, Hoshizora no Memoria
    """

    _pattern = re.compile(r"^s(\d{3}).bin$")

    @classmethod
    def condition(cls, files: list[pathlib.Path]) -> bool:
        """Returns True if strategy can be applied.
        files will be entire folder content of save directory, hence implement
        various filtering as required. (e.g. extensions, etc.)

        Will only test maximum designated number of files.
        """

        return cls._condition_generic(files, ".bin", cls._pattern)

    @classmethod
    def rename(cls, files: list[pathlib.Path]) -> None:
        """Renames save files. Passed files are automatically sorted."""

        # filter
        valid_files = cls._filter_generic(files, ".bin", cls._pattern)

        start_idx, end_idx = cls._get_range_non_paged()

        # populate pairs in order
        counter = itertools.count(start_idx)
        old_new_path_pairs: list[tuple[pathlib.Path, pathlib.Path]] = []

        for idx in range(start_idx, end_idx + 1):
            if idx not in valid_files:
                continue

            old_new_path_pairs.append(
                (valid_files[idx], valid_files[idx].with_stem(f"s{next(counter):03}"))
            )

        cls._rename_on_confirmation(old_new_path_pairs)


@_register_strat
class KiriKiriPagedStrategy(RenameStrategyBase):
    """
    Desc: KiriKiri-engine based save file rename strategy, paged version
    Type: 04 pad / 1-start / 02 pad paged / 12 per page
    e.g.: data_0001_12.jpg (data_{page:04}_{order_in_page:02}.jpg)
    Note: _
    Used: Senren*Banka, Sanobawitch, RIDDLE JOKER, Cafe Stella, Wagamama HIGH SPEC, Angelic Chaos
    """

    _pattern = re.compile(r"^data_\d{4}_\d{2}.jpg$")

    @classmethod
    def condition(cls, files: list[pathlib.Path]) -> bool:
        """Returns True if strategy can be applied.
        files will be entire folder content of save directory, hence implement
        various filtering as required. (e.g. extensions, etc.)
        """

        return cls._condition_generic(files, ".jpg", cls._pattern)

    @classmethod
    def rename(cls, files: list[pathlib.Path]) -> None:
        """Renames save files. Passed files are automatically sorted."""

        page_size = 12

        # filter
        valid_files = cls._filter_paged(files, ".jpg", cls._pattern)

        start_page_idx, end_page_idx = cls._get_range_paged()

        start_idx = start_page_idx[0] * page_size + start_page_idx[1]
        end_idx = end_page_idx[0] * page_size + end_page_idx[1]

        # populate pairs in order
        counter = itertools.count(start_idx)

        old_new_path_pairs: list[tuple[pathlib.Path, pathlib.Path]] = []

        for eff_idx in range(start_idx, end_idx + 1):
            page_idx_pair = divmod(eff_idx - start_idx, page_size)

            if page_idx_pair not in valid_files:
                continue

            new_page_idx_pair = divmod(next(counter), page_size)

            old_new_path_pairs.append(
                (
                    valid_files[page_idx_pair],
                    valid_files[page_idx_pair].with_stem(
                        f"{new_page_idx_pair[0]:04}_{new_page_idx_pair[1]:02}"
                    ),
                )
            )

        cls._rename_on_confirmation(old_new_path_pairs)


# @_register_strat
class AsaNewStrategy(RenameStrategyBase):
    """
    Desc: KiriKiri-engine based, ASAProject's save file rename strategy
    Type: no padding / 51-start
    e.g.: renrowa51.bmp (renrowa{idx}.bmp), sukitosuki51.bmp (sukitosuki{idx}.bmp)
    Note: ASA's VNs don't delete files, one should manually delete files corresponding to empty slots.
    Used: RenaiRoyal, Koikari
    """

    _prefixes: set[str] = {
        "renrowa",
        "sukitosuki",
    }

    @classmethod
    def condition(cls, files: list[pathlib.Path]) -> bool:

        for file in files:
            if file.suffix != ".bmp":
                continue

            for prefix in cls._prefixes:
                if file.stem.startswith(prefix):
                    return True

        return False

    @classmethod
    def rename(cls, files: list[pathlib.Path]) -> None:

        offset = 50

        # first filtering path
        ext_filtered = [file for file in files if file.suffix == ".bmp"]

        # determine prefix.
        # prefix will exist, since it passed condition check
        detected_prefix: str = ""

        for file in ext_filtered:
            for prefix in cls._prefixes:
                if file.stem.startswith(prefix):
                    detected_prefix = prefix
                    break

        valid_files: dict[int, pathlib.Path] = {}

        for file in ext_filtered:
            if file.stem.startswith(detected_prefix):
                valid_files[int(file.stem[len(detected_prefix) :])] = file

        start_idx, end_idx = cls._get_range_non_paged()
        counter = itertools.count(start_idx + offset)

        old_new_path_pairs: list[tuple[pathlib.Path, pathlib.Path]] = []

        for idx in range(start_idx + offset, end_idx + offset + 1):
            if idx not in valid_files:
                continue

            old_new_path_pairs.append(
                (
                    valid_files[idx],
                    valid_files[idx].with_stem(f"{detected_prefix}{next(counter)}"),
                )
            )

        cls._rename_on_confirmation(old_new_path_pairs)


# noinspection SpellCheckingInspection
@_register_strat
class KonosoraENG(RenameStrategyBase):
    """
    Desc: PULLTOP's Konosora ENG save file rename strategy
    Type: 03 padding / 1-start / separate thumbnail
    e.g.: 'Save001.Konosora EnglishSave-WillPlus', Save001.png
    Note: _
    Used: If my heart had wings (Konosora ENG)
    """

    _pattern = re.compile(r"^Save(\d{3}).Konosora EnglishSave-WillPlus$")
    _pattern_thumb = re.compile(r"^Save(\d{3}).png$")

    @classmethod
    def condition(cls, files: list[pathlib.Path]) -> bool:
        return cls._condition_generic(
            files, ".Konosora EnglishSave-WillPlus", cls._pattern
        )

    @classmethod
    def rename(cls, files: list[pathlib.Path]) -> None:

        # filter
        valid_files = cls._filter_generic(
            files, ".Konosora EnglishSave-WillPlus", cls._pattern
        )
        valid_thumbs = cls._filter_generic(files, ".png", cls._pattern_thumb)

        start_idx, end_idx = cls._get_range_non_paged()

        # populate pairs in order
        counter = itertools.count(start_idx)
        old_new_path_pairs: list[tuple[pathlib.Path, pathlib.Path]] = []

        for idx in range(start_idx, end_idx + 1):
            if idx not in valid_files:
                continue

            assert (
                idx in valid_thumbs
            ), f"Thumbnail '{valid_thumbs[idx].name}' not found."

            next_idx = next(counter)

            old_new_path_pairs.append(
                (
                    valid_files[idx],
                    valid_files[idx].with_stem(f"Save{next_idx:03}"),
                )
            )
            old_new_path_pairs.append(
                (
                    valid_thumbs[idx],
                    valid_thumbs[idx].with_stem(f"Save{next_idx:03}"),
                )
            )

        cls._rename_on_confirmation(old_new_path_pairs)


# --- Drivers ---


def rename_save(save_path: pathlib.Path):

    for strat in MAPPING:
        files = list(save_path.iterdir())

        if strat.condition(files):
            print(f"\nStrategy {strat.__name__} selected.")
            strat.rename(files)
            return
    else:
        print(f"No strategy found for {save_path}")


if __name__ == "__main__":

    print("Supported strategies:\n")
    for _strat in MAPPING:
        print(f"# {_strat.__name__}:\n{_strat.__doc__.lstrip()}", end="\n")

    _parser = argparse.ArgumentParser()
    _parser.add_argument("save_path", type=pathlib.Path)

    try:
        rename_save(_parser.parse_args().save_path)

    except Exception as err:
        import traceback

        traceback.print_exc()
        input("\nPress enter to exit:")
        raise

    input("\nPress enter to exit:")
