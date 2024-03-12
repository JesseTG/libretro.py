from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple

from ...h import *


class DeviceIdJoypad(IntEnum):
    B = RETRO_DEVICE_ID_JOYPAD_B
    Y = RETRO_DEVICE_ID_JOYPAD_Y
    SELECT = RETRO_DEVICE_ID_JOYPAD_SELECT
    START = RETRO_DEVICE_ID_JOYPAD_START
    UP = RETRO_DEVICE_ID_JOYPAD_UP
    DOWN = RETRO_DEVICE_ID_JOYPAD_DOWN
    LEFT = RETRO_DEVICE_ID_JOYPAD_LEFT
    RIGHT = RETRO_DEVICE_ID_JOYPAD_RIGHT
    A = RETRO_DEVICE_ID_JOYPAD_A
    X = RETRO_DEVICE_ID_JOYPAD_X
    L = RETRO_DEVICE_ID_JOYPAD_L
    R = RETRO_DEVICE_ID_JOYPAD_R
    L2 = RETRO_DEVICE_ID_JOYPAD_L2
    R2 = RETRO_DEVICE_ID_JOYPAD_R2
    L3 = RETRO_DEVICE_ID_JOYPAD_L3
    R3 = RETRO_DEVICE_ID_JOYPAD_R3
    MASK = RETRO_DEVICE_ID_JOYPAD_MASK

    def __init__(self, value: int):
        self._type_ = 'H'


@dataclass
class JoypadState(NamedTuple):
    b: bool = False
    y: bool = False
    select: bool = False
    start: bool = False
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    a: bool = False
    x: bool = False
    l: bool = False
    r: bool = False
    l2: bool = False
    r2: bool = False
    l3: bool = False
    r3: bool = False

    @property
    def mask(self) -> int:
        return (self.b << 0) \
            | (self.y << 1) \
            | (self.select << 2) \
            | (self.start << 3) \
            | (self.up << 4) \
            | (self.down << 5) \
            | (self.left << 6) \
            | (self.right << 7) \
            | (self.a << 8) \
            | (self.x << 9) \
            | (self.l << 10) \
            | (self.r << 11) \
            | (self.l2 << 12) \
            | (self.r2 << 13) \
            | (self.l3 << 14) \
            | (self.r3 << 15)
