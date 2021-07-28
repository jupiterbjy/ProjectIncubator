Convert source image to contoured webm. Just for fun!

Simply drag and drop the image file to [contour_gen.py](contour_gen.py)!


To install - just execute `install_module.py` - this will install requirements.txt.
You can simply do it yourself with `python3 -m pip install -r requirements.txt`.

---

### Options:

```json
{
    "fade_div_factor": 5,  // fade steps for generating fading frames of range(255, 0, -fade_div_factor)
    "transparent": false,  // whether script should generate transparent webm - this yield worse quality.
    "fps_cap": 60, // how high framerate can go
    "time_limit": 5,  // how long video should be in seconds. This will be ignored when fps exceed fps cap.
    "res_multiply": 4,  // resolution multiplier for contour
    "threshold": [0, 100],  // low-high threshold for contours. lower draw more lines with much more computing time.
    "line_width": 3  // thickness of contour lines
}
```

---

### Source

![](cyan_quick_3_MAD.png)

---

### Non-transparent Output (Converted to webp)

![](Demo/ReadmePreview.webp)
