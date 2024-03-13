from dataclasses import dataclass
from enum import IntEnum

from .info import InputDeviceState
from ...h import *


class DeviceIndexAnalog(IntEnum):
    LEFT = RETRO_DEVICE_INDEX_ANALOG_LEFT
    RIGHT = RETRO_DEVICE_INDEX_ANALOG_RIGHT
    BUTTON = RETRO_DEVICE_INDEX_ANALOG_BUTTON

    def __init__(self, value: int):
        self._type_ = 'H'


class DeviceIdAnalog(IntEnum):
    X = RETRO_DEVICE_ID_ANALOG_X
    Y = RETRO_DEVICE_ID_ANALOG_Y

    def __init__(self, value: int):
        self._type_ = 'H'


@dataclass(frozen=True, slots=True)
class AnalogState(InputDeviceState):
    b: int = 0
    y: int = 0
    select: int = 0
    start: int = 0
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0
    a: int = 0
    x: int = 0
    l: int = 0
    r: int = 0
    l2: int = 0
    r2: int = 0
    l3: int = 0
    r3: int = 0

    left_x: int = 0
    left_y: int = 0
    right_x: int = 0
    right_y: int = 0
