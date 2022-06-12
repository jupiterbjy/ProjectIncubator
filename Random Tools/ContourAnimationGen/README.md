Convert source image to contoured webm. Just for fun!

Simply drag and drop the image file to [contour_gen.py](contour_gen.py)!


To install - just execute `install_module.py` - this will install requirements.txt.
You can simply do it yourself with `python3 -m pip install -r requirements.txt`.

---

### Options:

Both parameter and json configurations are same.

Explicit parameter always overrides json configuration.

- param

    ```commandline
    usage: Script generating contour timelapse video for given image.
           [-h] [-s INT] [-t BOOL] [-f INT] [-d FLOAT] [-m INT] [-tl INT]
           [-th INT] [-w INT]
           file
    
    positional arguments:
      file                  Path to image
    
    optional arguments:
      -h, --help            show this help message and exit
      -s INT, --fade-step INT
                            alpha value step size for fading effects
      -t BOOL, --transparent BOOL
                            If true, generates transparent webm - this yield worse
                            quality.
      -f INT, --fps-cap INT
                            Sets hard limit on frame rate.
      -d FLOAT, --duration FLOAT
                            how long video should be in seconds. This will be
                            ignored when fps exceed fps-cap.
      -m INT, --res-multiply INT
                            Resolution multiplier for contours.
      -tl INT, --threshold-low INT
                            Low threshold of canny edge detection. More lines are
                            drawn when lower.
      -th INT, --threshold-high INT
                            High threshold of canny edge detection. More lines are
                            drawn when lower.
      -w INT, --line-width INT
                            Thickness of contour lines.
    ```

- json

    ```json
      {
        "fade_step": 5,
        "transparent": false,
        "fps_cap": 60,
        "duration": 5,
        "res_multiply": 4,
        "threshold_low": 0,
        "threshold_high": 100,
        "line_width": 3
    }
    ```

---

### Source

![](cyan_quick_3_MAD.png)

---

### Non-transparent Output (Converted to webp)

![](Demo/ReadmePreview.webp)
