"""
Script to add text to images, because I'm too lazy
"""

import pathlib
from typing import Sequence, Generator


import tkinter
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk


ROOT = pathlib.Path(__file__).parent
IMG_SRC = ROOT / "Images"
IMG_OUT = ROOT / "Outputs"
IMG_OUT.mkdir(exist_ok=True)

TXT_SRC = ROOT / "cdi_voice_map.txt"


class ScalingImageWidget(ttk.Label):
    def __init__(self, master, image: Image.Image = None, resize_wait_ms=500):

        # without anchor="center" it won't ever center inside label.
        super().__init__(master, compound="image", anchor="center")

        # source image without modification
        self._src: Image.Image | None = image

        self._resize_wait = resize_wait_ms

        # current displayed image.
        # without reference keeping image gets GC-ed and not show up.
        self._displayed: ImageTk.PhotoImage | None = None

        # bind resize event
        self.master.bind("<Configure>", self._on_resize)

        # resize event cooldown timer's ID
        self._active_timer_id = ""

    def _on_resize(self, _):
        """Callback for resize event. Schedules resize in timeout_ms.
        Resets timer when another resize event fires, to reduce resizing calculations.
        """

        # if already in resize timer, cancel and restart
        if self._active_timer_id:
            self.after_cancel(self._active_timer_id)

        self._active_timer_id = self.after(self._resize_wait, self._on_timeout)

    def _on_timeout(self):
        """Scheduled task for actual resizing."""

        self._active_timer_id = ""
        self._resize()

    def _resize(self, margin_px=10):
        """Resize image to fit within current widget's width & height."""

        if self._src is None:
            return

        # subtract margin, or border keeps up triggering resizing events.
        width = self.winfo_width() - margin_px
        height = self.winfo_height() - margin_px

        print(f"Resizing to ({width} {height})")

        ratio = min(width / self._src.size[0], height / self._src.size[1])
        size = int(ratio * self._src.size[0]), int(ratio * self._src.size[1])

        self._displayed = ImageTk.PhotoImage(self._src.resize(size))
        self.configure(image=self._displayed, padding=0)

    def update_img(self, img: Image.Image | None):
        """Replace/Remove displayed image. Send None to clear image on widget."""

        print("Updating preview")

        self._src = img

        # if none clear image
        if img is None:
            self._displayed = None
            self.configure(image=None)
            return

        try:
            self._resize()
        except ValueError:
            # widget's just started and size is 0, 0. Ignore
            pass


class App(ttk.Frame):
    def __init__(self, master, sample_img: Image.Image, sample_line: str):
        super().__init__(master)

        self.pack(fill="both", expand=True)

        self.master = master

        self.subframe = ttk.Frame(self)
        self.subframe.grid(column=0, row=0)

        _x_label = ttk.Label(self.subframe, text="X:")
        _x_label.grid(column=0, row=0)
        self.x_spin = ttk.Spinbox(
            self.subframe, from_=0, to=sample_img.size[0], format="", command=self.update_image
        )
        self.x_spin.grid(column=1, row=0)
        self.x_spin.set(0)

        self.y_spin = ttk.Spinbox(self, from_=0, to=sample_img.size[1], command=self.update_image)
        self.y_spin.grid(column=1, row=0)
        self.y_spin.set(0)

        self.start_btn = ttk.Button(self, text="Start")
        self.start_btn.grid(column=2, row=0)

        self.src_img = sample_img
        self.src_str = sample_line

        # need to keep ref or gets GCed
        self.displayed_img: ImageTk.PhotoImage | None = None

        self.image_widget = ScalingImageWidget(self)
        self.image_widget.grid(column=0, row=1, columnspan=3, sticky="NSWE")
        # self.image_widget.update_img(sample_img)

        # schedule update, widget size isn't ready yet
        self.after_idle(self.image_widget.update_img, sample_img)

        # configure bottom widget(image) weight to 1 & let both column expand
        self.grid_rowconfigure(1, weight=1)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

    def update_image(self):
        """Redraws text onto image using current coordinates, and update preview"""

        new_img = draw_text(self.src_img, self.src_str, int(self.x_spin.get()), int(self.y_spin.get()))
        self.image_widget.update_img(new_img)


def draw_text(src_img: Image.Image, text: str, pos_x: int, pos_y: int) -> Image.Image:
    """Draws text onto src image at given xy coordinates and returns new image."""

    new_img = src_img.copy()

    draw = ImageDraw.Draw(new_img, "RGBA")
    draw.text((pos_x, pos_y), text)

    return new_img


def main():
    images = [Image.open(path) for path in IMG_SRC.iterdir()]
    print("Got input Image size", images[0].size)

    # load lines & replace each line's dividers to newline
    lines = [
        line.replace(" - ", "\n") for line in TXT_SRC.read_text("utf8").splitlines()
    ]

    window = tkinter.Tk()
    window.title("write2img preview")
    window.geometry("640x500")

    style = ttk.Style()
    style.configure("BW.TLabel", foreground="black", background="white")

    app = App(window, images[0], lines[0])
    window.bind("<Configure>", )

    window.update_idletasks()
    print(app.image_widget.winfo_width(), app.image_widget.winfo_height())
    window.mainloop()


if __name__ == '__main__':
    # _parser = ArgumentParser()
    # _parser.add_argument(
    #     "images",
    #     type=pathlib.Path,
    #     nargs="+",
    # )

    main()
