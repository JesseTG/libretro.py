import enum

from ._libretro import *


class Rotation(enum.IntEnum):
    NONE = 0
    _90 = 1
    _180 = 2
    _270 = 3


class PixelFormat(enum.IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565


class Region(enum.IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL
