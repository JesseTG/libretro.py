from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple

from ...h import *


class DeviceIdMouse(IntEnum):
    X = RETRO_DEVICE_ID_MOUSE_X
    Y = RETRO_DEVICE_ID_MOUSE_Y
    LEFT = RETRO_DEVICE_ID_MOUSE_LEFT
    RIGHT = RETRO_DEVICE_ID_MOUSE_RIGHT
    WHEELUP = RETRO_DEVICE_ID_MOUSE_WHEELUP
    WHEELDOWN = RETRO_DEVICE_ID_MOUSE_WHEELDOWN
    MIDDLE = RETRO_DEVICE_ID_MOUSE_MIDDLE
    HORIZ_WHEELUP = RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELUP
    HORIZ_WHEELDOWN = RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELDOWN
    BUTTON_4 = RETRO_DEVICE_ID_MOUSE_BUTTON_4
    BUTTON_5 = RETRO_DEVICE_ID_MOUSE_BUTTON_5

    def __init__(self, value: int):
        self._type_ = 'H'


@dataclass(frozen=True)
class MouseState(NamedTuple):
    x: int = 0
    y: int = 0
    left: bool = False
    right: bool = False
    wheel_up: bool = False
    wheel_down: bool = False
    middle: bool = False
    horizontal_wheel_up: bool = False
    horizontal_wheel_down: bool = False
    button4: bool = False
    button5: bool = False
