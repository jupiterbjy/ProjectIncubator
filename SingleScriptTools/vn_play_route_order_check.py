"""
Typed in vim for quick test to answer reddit comment

I thought I played wakana route first.
I wasn't, she was 3rd. Meguru was first.
RIP my memory

Assumes you use parsec, and has moonlight file mixed in.
Will update this in future (if I ever need to) to expand this for automatic detection
based on screenshot percentage.

```text
❯ py .\check_route_order.py 사노바위치
사노바위치 공통 - 2024-09-22-00-24-58 ~ 2024-09-22-08-04-45 / total 617
사노바위치 메구루 - 2024-09-22-08-11-38 ~ 2024-09-26-02-54-58 / total 1129
사노바위치 네네 - 2024-09-23-02-22-53 ~ 2024-09-26-02-18-05 / total 2368
사노바위치 와카나 - 2024-09-26-03-12-26 ~ 2024-09-29-07-25-48 / total 860
사노바위치 토오카 - 2025-06-04-02-46-58 ~ 2025-06-06-06-53-56 / total 882
사노바위치 시바 - 2025-06-06-07-00-39 ~ 2025-06-09-04-51-59 / total 871
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
from argparse import ArgumentParser

_parser = ArgumentParser()
_parser.add_argument(
    "name",
    type=str,
)
_args = _parser.parse_args()

sabbat_roots = [p for p in pathlib.Path(".").iterdir() if p.stem.startswith(_args.name)]


def extract_date_range(r: pathlib.Path) -> tuple[str, str, str, int]:
    imgs = sorted(r.iterdir())

    # focus parsec if exists, otherwise moonlight
    # if it's mixed, probably lately added standing CG screenshots
    prefix = "Moon" if imgs[-1].stem.startswith("Moon") else "Parsec"
    imgs = [p for p in imgs if p.stem.startswith(prefix)]

    return r.stem, imgs[0].stem.split("_")[-1], imgs[-1].stem.split("_")[-1], len(imgs)


for name, start, end, count in sorted(
    map(extract_date_range, sabbat_roots), key=lambda x: x[1]
):
    print(f"{name} - {start} ~ {end} / total {count}")
