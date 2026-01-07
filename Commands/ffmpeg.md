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


## sRGB to Rec.709

Not sure if this is working properly, since regardless of this youtube still makes my video darker.
Funny that VLC player correctly identifies it as Rec.709 but I'm not sure if it's inferring it as sRGB or not.

TODO: check this later

```shell
ffmpeg -colorspace bt709 -color_trc iec61966-2-1 -i %1 -color_primaries 1 "%~n1_av1_rec709.mp4"
```

```shell
ffmpeg -colorspace bt709 -color_trc iec61966-2-1 -i %1 -c:v libsvtav1 -crf 25 -preset 4 -svtav1-params tune=0:enable-tf=0:enable-qm=1:qm-min=0 -color_primaries 1 -c:a libopus -b:a 192k -vbr:a on "%~n1_av1_rec709.mp4"
```

<br>


## Adding full color flag

Used for rare cases where video is in full color range but isn't marked as such. (e.g. steam recording).

```shell
ffmpeg -i %1 -c copy -bsf:v h264_metadata=video_full_range_flag=1 "%~n1_flagged.mp4"
```

For my usecase when encoding unflagged full range(pc) to limited range(tv):
```shell
ffmpeg -i %1 -vf scale=in_range=pc:out_range=tv -c:v libsvtav1 -crf 25 -preset 4 -svtav1-params tune=0:enable-tf=0:enable-qm=1:qm-min=0 -c:a libopus -b:a 192k -vbr:a on 
```

And due to long-time VLC bug on windows regarding full range color - for those either move to mpv or
re-encode flagged video to limited color range. (Refer [this](https://code.videolan.org/videolan/vlc/-/issues/28741))

```text
[vf#0:0 @ ...] Reconfiguring filter graph because video parameters changed to yuvj420p(pc, bt709), 1920x1080
[swscaler @ ...] deprecated pixel format used, make sure you did set range correctly
```

ffmpeg tend to set `yuvj420p` for fullcolor(pc) for whatever reason and then complain about it being deprecated but ignore it.

Still full range AV1 HW decoding on AMD + MPV is messed up too but slightly better at H264 full range at least.

<br>


## 2 AV1

TODO: retest & rewrite this section

Refer [ffmpeg av1 manual](https://trac.ffmpeg.org/wiki/Encode/AV1)

`_av1` - yeah

batch(cpu):
```shell
ffmpeg -i %1 -c:v libsvtav1 -crf 25 -c:a aac -q:a 2 "%~n1_av1.mp4"
```

batch(amd amf):
```shell
ffmpeg -i %1 -c:v av1_amf -rc cqp -c:a aac -q:a 2 "%~n1_av1.mp4"
```

batch personal archiving(cpu):
```shell
ffmpeg -i %1 -c:v libsvtav1 -crf 25 -preset 4 -svtav1-params tune=0:enable-tf=0:enable-qm=1:qm-min=0 -c:a libopus -b:a 192k -vbr:a on "%~n1_av1.mp4"
```
(libsvtav1 has very low keyframe interval of 2~3s, but effect of extending it seems barely dramatic)

bash personal batch-archiving for web streaming, one-liner (cpu):
```shell
mkdir av1; for i in *.mp4; do [ -f "$i" ] || break; ffmpeg -i "$i" -c:v libsvtav1 -crf 25 -preset 4 -svtav1-params tune=0:enable-tf=0:enable-qm=1:qm-min=0 -c:a libopus -b:a 192k -vbr:a on -y "av1/$i"; done
```
(There's option to make decoding faster if you have trouble decoding)

For quick drag drop encoding to save space.
Check `ffmpeg -encoders | grep av1` to check fitting encoder for your hw.

When checking VMAF score & size, for my scribbling vids output by CSP - `av1_amf`
worked best & simplest for `cqp` mode at default(speed) & balanced quality preset considering encoding time.

Following is my test based on my scribbling which is mostly thin black & white:

| Encoder     | Extra param                 | VMAF  | Size(MB) |
|-------------|-----------------------------|-------|----------|
| `libsvtav1` |                             | 97.06 | 2.77     |
| `libsvtav1` | `-crf 25`                   | 97.27 | 4.29     |
| `av1_amf`   |                             | 99.01 | 18.1     |
| `av1_amf`   | `-rc cqp`                   | 99.32 | 4.47     |
| `av1_amf`   | `-rc cqp -quality balanced` | 99.32 | 4.47     |
| `av1_amf`   | `-rc cqp -quality quality`  | 99.25 | 4.24     |

...kinda feel weird to see VMAF drop with higher quality preset.
Tho I still need `libsvtav1` since iirc `amd_amf` has hw bug with frame width,
which in ffmpeg effects resulting vid to be somewhat messed up.

EDIT: After search, that might be result of dupe frame dropping related. 

Another random test (pat a mat first episode, 960x720 7min) with bit more proper vmaf,
where we can clearly see the result more inline with what we expect, compared to above
which had tons of static white background since it's drawing timelapse.

```shell
ab-av1 vmaf --reference SRC --distorted ENCODED
```

| Encoder     | Extra param                                      | VMAF  | Size(MB) |
|-------------|--------------------------------------------------|-------|----------|
| `libsvtav1` | `-crf 17`                                        | 94.23 | 113      |
| `libsvtav1` | `-crf 17 -svtav1-params tune=0`                  | 94.62 | 116      |
| `libsvtav1` | `-crf 17 -preset 4 -svtav1-params tune=0`        | 95.65 | 117      |
| `libsvtav1` | `-crf 20 -preset 4 -svtav1-params tune=0`        | 95.14 | 95.7     |
| `libsvtav1` | `-crf 17 -preset 5 -svtav1-params tune=0`        | 95.63 | 120      |
| `libsvtav1` | `-crf 17 -g 120 -preset 5 -svtav1-params tune=0` | 95.62 | 119      |
| `libsvtav1` | `-crf 15 -preset 5 -svtav1-params tune=0`        | 96.04 | 143      |
| `libsvtav1` | `-crf 20 -preset 5 -svtav1-params tune=0`        | 95.13 | 97       |
| `av1_amf`   | `-rc cqp`                                        | 95.81 | 219      |
| `av1_amf`   | `-rc cqp -quality quality`                       | 95.90 | 212      |
| `libsvtav1` | (not ffmpeg) `ab-av1 auto-encode`                | 96.20 | 232      |

Since this episode has tons of film grain I should've `flim-grain` option but for vmaf it's off. 

Also refer [this comment](https://www.reddit.com/r/AV1/comments/18l0k07/comment/kdw9mg3/?utm_source=share&utm_medium=web2x&context=3)


<br>


## XPSNR Score

command:
```shell
ffmpeg -v error -i "{in_reference}" -i "{in_encoded}" -t 30 -filter_complex xpsnr="stats_file=-" -f null -
```

Alternative method to measure 


## VMAF Score

command:
```shell
 ffmpeg -i "{in_reference}" -i "{in_encoded}" -filter_complex libvmaf -t 15 -f null -
```

<sub>(Since when drag dropped from explorer param doesn't distinguish order so better type manually)</sub>

`-t` flag is there so that I don't have to wait eternity, this is very slow operation (at least for my 5800X)

Used for checking video's variance from original. Not an absolute standard, has own downsides.
