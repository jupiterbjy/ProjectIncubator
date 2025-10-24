Random sets of command(script) I have lying around for random usages, since I love drag-dropping to script a lot.

## 4 to 1 square merge

`_4sm` - initials of '4, square merge'

batch:
```shell
set out="%~n1_4sm.mp4"
ffmpeg -i %1 -i %2 -i %3 -i %4 -filter_complex "[0:v][1:v]hstack=inputs=2[top];[2:v][3:v]hstack=inputs=2[bottom];[top][bottom]vstack=inputs=2[v]" -map "[v]" -shortest -y %out%
```

<br>


## 2 to 1 vertical merge

`_2vm` - initials of '2, vertical merge'

batch:
```shell
set out="%~n1_2vm.mp4"
ffmpeg -i %1 -i %2 -filter_complex vstack -c:v libx264 -crf 18 -shortest -y %out%
```

ps(not intended for drag drop):
```shell
param (
	[System.IO.FileInfo] $file_0,
	[System.IO.FileInfo] $file_1
)
$out = $file_0.BaseName + "_2vm.mp4"

ffmpeg -i $file_0 -i $file_1 -filter_complex vstack -c:v libx264 -crf 18 -shortest -y $out
```

Preferably add `-an` flag to remove audio

<br>


## Frame dropping acceleration, no audio

`xNfd` - 'x(requested multiply factor), frame dropping' e.g. `Iroseka Shinku_x9.0fd.mp4`

command (replace all braces):
```shell
ffmpeg -i "{in}" -r 60 -filter:v "setpts={factor/60}*PTS" -an -c:v libx264 -crf 18 -y "{out}"
```

python: Refer [script](/SingleScriptTools/ffmpeg_playback_multiply_▽.py)

Mostly used for accelerating timelapse of
[my scribblings](https://youtu.be/0QziZU9Bwa8?list=PLmaqFP6jEVikTV5xsSAY8QzgEfPg5q4tm)
without blurry interpolated frames

<br>


## mkv 2 mp4

batch:
```shell
ffmpeg -i %1 -c copy "%~n1.mp4"
```

Mostly used for converting mkv to mp4 without encoding

<br>


## Audio removal

`_na` - initials of 'no audio'

batch:
```shell
ffmpeg -i %1 -c copy -an "%~n1_na.mp4"
```

<br>


## 2 AV1

`_av1` - yeah

batch(cpu):
```shell
ffmpeg -i %1 -c:v libsvtav1 -crf 25 "%~n1_av1.mp4"
```

batch(amd amf):
```shell
ffmpeg -i %1 -c:v av1_amf -rc cqp "%~n1_av1.mp4"
```

For quick drag drop encoding to save space.
Check `ffmpeg -encoders | grep av1` to check fitting encoder for your hw.

When checking VMAF score & size, for my scribbling vids output by CSP - `av1_amf`
worked best & simplest for `cqp` mode at default(speed) & balanced quality preset considering encoding time.

Following is my test based on my scribbling which is mostly thin black & white:

| Encoder     | Extra param              | VMAF  | Size(MB) |
|-------------|--------------------------|-------|----------|
| `libsvtav1` |                          | 97.06 | 2.77     |
| `libsvtav1` | `-crf 25`                | 97.27 | 4.29     |
| `av1_amf`   |                          | 99.01 | 18.1     |
| `av1_amf`   | `-cqp`                   | 99.32 | 4.47     |
| `av1_amf`   | `-cqp -quality balanced` | 99.32 | 4.47     |
| `av1_amf`   | `-cqp -quality quality`  | 99.25 | 4.24     |

...kinda feel weird to see VMAF drop with higher quality preset

<br>


## VMAF Score

command:
```shell
ffmpeg -i src -i
```

Used for checking video's variance from original.