"""
Resizable tk image widget demo using PIL, with resize cooldown timer implemented.
Uses image from web to make this standalone, while not making this script large.
"""

import tkinter
from io import BytesIO
from typing import Sequence
from urllib import request
from tkinter import ttk

from PIL import Image, ImageTk


IMAGE_URL_LIST = [
    "https://imgur.com/JaxDbJJ.png",
    "https://imgur.com/e6u4WgF.png",
    "https://imgur.com/6bkJgav.png",
]


class ScalingImageWidget(ttk.Label):
    def __init__(self, master, image: Image.Image = None, resize_wait_ms=500, margin_px=10):
        """
        Args:
            master: Parent widget/window
            image: Initial displayed image if any
            resize_wait_ms: Time to wait after resizing event before resizing image
            margin_px: Margin around image
        """

        # without anchor="center" it won't ever center inside label.
        super().__init__(master, compound="image", anchor="center")

        # source image without modification
        self._src: Image.Image | None = image

        self._resize_wait = resize_wait_ms
        self._margin = margin_px

        # current displayed image.
        # without reference keeping image gets GC-ed and not show up.
        self._displayed: ImageTk.PhotoImage | None = None

        # bind resize event
        master.bind("<Configure>", self._on_resize)

        # resize event cooldown timer's ID
        self._active_timer_id = ""

    def _on_resize(self, _event):
        """Callback for resize event. Schedules resize in timeout_ms.
        Resets timer when another resize event fires, to reduce resizing calculations.
        """

        # if already scheduled, cancel and restart
        if self._active_timer_id:
            self.after_cancel(self._active_timer_id)

        self._active_timer_id = self.after(self._resize_wait, self._on_timeout)

    def _on_timeout(self):
        """Scheduled task for actual resizing."""

        self._active_timer_id = ""
        self._resize()

    def _resize(self):
        """Resize image to fit within current widget's width & height."""

        if self._src is None:
            return

        # subtract margin, or border keeps up triggering resizing events.
        width = self.winfo_width() - self._margin
        height = self.winfo_height() - self._margin

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


# --- Below is demo usage of above widget ---


class DemoApp(ttk.Frame):
    def __init__(self, master, images: Sequence[Image.Image]):
        super().__init__(master)

        self.pack(fill="both", expand=True)

        # some grid layout setups
        self.x_spin = ttk.Label(self, text="grid(0, 0)")
        self.x_spin.grid(column=0, row=0)

        self.y_spin = ttk.Label(self, text="grid(0, 1)")
        self.y_spin.grid(column=1, row=0)

        self.start_btn = ttk.Button(self, text="Change image", command=self.change_image)
        self.start_btn.grid(column=2, row=0)

        self.image_widget = ScalingImageWidget(self)
        self.image_widget.grid(column=0, row=1, columnspan=3, sticky="NSWE")

        # images to display & current displayed image's idx
        self.src_images = images
        self.image_idx = -1

        # need to keep ref or gets GCed and doesn't show up
        self.displayed_img: ImageTk.PhotoImage | None = None

        # schedule update, widget size isn't ready yet
        self.after_idle(self.change_image)

        # configure bottom widget(image) weight to 1
        self.grid_rowconfigure(1, weight=1)

        # letting all columns expand freely
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

    def change_image(self):
        """Cycles displayed image."""

        self.image_idx = (self.image_idx + 1) % len(self.src_images)
        self.image_widget.update_img(self.src_images[self.image_idx])


def main():
    images = [
        Image.open(BytesIO(request.urlopen(url).read())) for url in IMAGE_URL_LIST
    ]

    window = tkinter.Tk()
    window.title("Auto resizing image widget Demo")
    window.geometry("640x500")

    app = DemoApp(window, images)
    window.mainloop()


if __name__ == '__main__':
    main()
