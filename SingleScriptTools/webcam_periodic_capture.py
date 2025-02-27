"""
Script to capture webcam images periodically.

`pip install opencv-python`

![](readme_res/webcam_periodic_capture.png)

:Author: jupiterbjy@gmail.com
"""

import time
import pathlib
import itertools

import cv2


# --- Config ---

RES = 2592, 1944
DISPLAY_RES = 640, 480
DISPLAY_INTERVAL: int = 100

IMG_NAME_DIGITS = 10
IMG_START_IDX = 0

CAM_ID = 1
CAM_BACKEND = cv2.CAP_DSHOW
# CAM_BACKEND = cv2.CAP_MSMF
CAP_INTERVAL = 10


ROOT = pathlib.Path(__file__).parent
CAP_DIR = ROOT / "CAP"
# CAP_DIR = pathlib.Path("Z:/CAP")

CAP_DIR.mkdir(exist_ok=True)


# --- Logics ---

# def list_webcams() -> Sequence[cv2.VideoCapture]:
#     """List available webcams"""
#
#     webcams: List[cv2.VideoCapture] = []
#
#     index = 0
#     for idx in itertools.count():
#
#         cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
#         if not cap.read()[0]:
#             break
#
#         webcams.append(cap)
#
#         print(f"Camera index: {idx}")
#         index += 1
#
#     return webcams


def _get_cam():
    """Fetch cam set by global config"""

    return cv2.VideoCapture(CAM_ID, cv2.CAP_DSHOW)


def capture_webcam_images():
    """Loop for capturing images from the selected webcam"""

    camera = _get_cam()

    # set resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, RES[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, RES[1])

    # prep names
    counter = itertools.count(IMG_START_IDX)
    captured_count = 0
    last_capture = 0
    baked_title = f"Webcam <cam {CAM_ID}> - {RES[0]}x{RES[1]} | Captured "

    while True:

        ret, frame = camera.read()

        # if broken release and recreate cam
        if not ret:
            print("Error reading frame from webcam - reinitializing")
            camera.release()
            camera = _get_cam()
            continue

        # show resized img so it doesn't explode the screen
        displayed_frame = cv2.resize(frame, DISPLAY_RES)
        cv2.imshow("Webcam", displayed_frame)
        cv2.setWindowTitle("Webcam", baked_title + str(captured_count))

        # check for esc or window closure
        if (
            cv2.waitKey(DISPLAY_INTERVAL) == 27
            or cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1
        ):
            print("Stopping!")
            break

        # save image
        if (new_time := int(time.time())) - last_capture >= CAP_INTERVAL:
            last_capture = new_time

            img_path = (CAP_DIR / f"img_{next(counter):010}.jpg").as_posix()
            print("Saving at", img_path)

            cv2.imwrite(img_path, frame)
            captured_count += 1

    # release cam
    camera.release()
    cv2.destroyAllWindows()


# --- Driver ---

if __name__ == "__main__":
    capture_webcam_images()
