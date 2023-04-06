"""
Simply checks if all files in folder is included in m3u file in the same dir
or if any of listed entry is missing
"""

import pathlib
import argparse
import itertools


parser = argparse.ArgumentParser()
parser.add_argument("path", metavar="PATH", type=str, help="Path to folder containing mp3 and m3u.")
parser.add_argument("-extensions", type=str, default=".ogg.mp3", help="files to include in m3u. Separated with dot.")

args = parser.parse_args()
extensions = tuple("." + extension for extension in args.extensions.strip(".").split("."))


target_path = pathlib.Path(args.path).absolute()
if not target_path.exists():
    raise FileNotFoundError(f"No such file - {target_path.as_posix()}")


files = [path for path in target_path.iterdir() if path.is_file()]

m3u_file = tuple(target_path.glob("*.m3u"))[0]
audio_filtered = itertools.chain(*tuple(target_path.glob("*" + ext) for ext in extensions))

audio_fn_only = set(file.name for file in audio_filtered)


to_add = []
to_remove = []


with open(m3u_file, encoding="utf8") as fp:
    m3u_list = [line.strip("\n") for line in iter(fp.readline, "")]
    m3u_set = set(m3u_list)

    to_add.extend(audio_fn_only - m3u_set)
    to_remove.extend(m3u_set - audio_fn_only)


print(f"Existing files: {len(audio_fn_only)}")
print(f"Entries in m3u: {len(m3u_list)}\n")
print(f"Files to add: {to_add}")
print(f"Files absent: {to_remove}")


if to_add or to_remove:
    while input_ := input("Fix automatically? (y/n): "):
        if input_ in "yY":

            # remove from list
            for file in to_remove:
                m3u_list.remove(file)

            # append to list
            m3u_list.extend(to_add)

            with open(m3u_file, "wt", encoding="utf8") as fp:
                fp.write("\n".join(m3u_list))

            print("Write done!")
            break

        if input_ in "nN":
            break
else:
    print("No action needed.")
