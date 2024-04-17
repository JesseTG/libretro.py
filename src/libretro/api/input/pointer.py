from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence

from .device import InputDeviceState

RETRO_DEVICE_ID_POINTER_X = 0
RETRO_DEVICE_ID_POINTER_Y = 1
RETRO_DEVICE_ID_POINTER_PRESSED = 2
RETRO_DEVICE_ID_POINTER_COUNT = 3


class DeviceIdPointer(IntEnum):
    X = RETRO_DEVICE_ID_POINTER_X
    Y = RETRO_DEVICE_ID_POINTER_Y
    PRESSED = RETRO_DEVICE_ID_POINTER_PRESSED
    COUNT = RETRO_DEVICE_ID_POINTER_COUNT

    def __init__(self, value: int):
        self._type_ = "H"


@dataclass(frozen=True, slots=True)
class Pointer:
    x: int = 0
    y: int = 0
    pressed: bool = False


@dataclass(frozen=True, slots=True)
class PointerState(InputDeviceState):
    pointers: Sequence[Pointer] = ()


__all__ = ["DeviceIdPointer", "Pointer", "PointerState"]
