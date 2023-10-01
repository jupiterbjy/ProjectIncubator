"""
Script to convert Armada Tank's DF font format to bitmap fnt.
"""

import pathlib

from PIL import Image


HEADER = """
info face="Arial" size=32 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0
common lineHeight=32 base=26 scaleW=256 scaleH=256 pages=1 packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0
"""


DF_PATH = pathlib.Path(r"D:\Armada Tanks\game data\BaseT\Texture\FontDesc\FontAdv_FD_224.df")


def df_line_gen():
    data = DF_PATH.read_text().splitlines()
    print(f"{}")
    for line in data:
        pass


def draw_marker():
    img_path = r"E:\github\ProjectIncubator\Random Tools\ImageFontSplitter\font_images\black.png"

    img = Image.open(img_path).convert()


