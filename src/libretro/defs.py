from enum import Enum

from ._libretro import *


class Rotation(Enum):
    NONE = 0
    _90 = 1
    _180 = 2
    _270 = 3
