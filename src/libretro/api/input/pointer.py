from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple, Sequence

from ...h import *


class DeviceIdPointer(IntEnum):
    X = RETRO_DEVICE_ID_POINTER_X
    Y = RETRO_DEVICE_ID_POINTER_Y
    PRESSED = RETRO_DEVICE_ID_POINTER_PRESSED
    COUNT = RETRO_DEVICE_ID_POINTER_COUNT

    def __init__(self, value: int):
        self._type_ = 'H'


@dataclass
class Pointer(NamedTuple):
    x: int = 0
    y: int = 0
    pressed: bool = False


@dataclass
class PointerState(NamedTuple):
    pointers: Sequence[Pointer] = ()