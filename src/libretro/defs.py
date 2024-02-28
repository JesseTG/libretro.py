from enum import Enum

from ._libretro import *


class Rotation(Enum):
    NONE = 0
    _90 = 1
    _180 = 2
    _270 = 3


class PixelFormat(Enum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565