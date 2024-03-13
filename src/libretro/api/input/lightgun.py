from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple

from ...h import *


@dataclass
class LightGunState(NamedTuple):
    screen_x: int = 0
    screen_y: int = 0
    is_offscreen: bool = False
    trigger: bool = False
    reload: bool = False
    aux_a: bool = False
    aux_b: bool = False
    start: bool = False
    select: bool = False
    aux_c: bool = False
    dpad_up: bool = False
    dpad_down: bool = False
    dpad_left: bool = False
    dpad_right: bool = False
    x: int = 0
    y: int = 0

    @property
    def cursor(self) -> bool:
        return self.aux_a

    @property
    def turbo(self) -> bool:
        return self.aux_b

    @property
    def pause(self) -> bool:
        return self.start


class DeviceIdLightgun(IntEnum):
    SCREEN_X = RETRO_DEVICE_ID_LIGHTGUN_SCREEN_X
    SCREEN_Y = RETRO_DEVICE_ID_LIGHTGUN_SCREEN_Y
    IS_OFFSCREEN = RETRO_DEVICE_ID_LIGHTGUN_IS_OFFSCREEN
    TRIGGER = RETRO_DEVICE_ID_LIGHTGUN_TRIGGER
    RELOAD = RETRO_DEVICE_ID_LIGHTGUN_RELOAD
    AUX_A = RETRO_DEVICE_ID_LIGHTGUN_AUX_A
    AUX_B = RETRO_DEVICE_ID_LIGHTGUN_AUX_B
    START = RETRO_DEVICE_ID_LIGHTGUN_START
    SELECT = RETRO_DEVICE_ID_LIGHTGUN_SELECT
    AUX_C = RETRO_DEVICE_ID_LIGHTGUN_AUX_C
    DPAD_UP = RETRO_DEVICE_ID_LIGHTGUN_DPAD_UP
    DPAD_DOWN = RETRO_DEVICE_ID_LIGHTGUN_DPAD_DOWN
    DPAD_LEFT = RETRO_DEVICE_ID_LIGHTGUN_DPAD_LEFT
    DPAD_RIGHT = RETRO_DEVICE_ID_LIGHTGUN_DPAD_RIGHT

    X = RETRO_DEVICE_ID_LIGHTGUN_X
    Y = RETRO_DEVICE_ID_LIGHTGUN_Y
    CURSOR = RETRO_DEVICE_ID_LIGHTGUN_CURSOR
    TURBO = RETRO_DEVICE_ID_LIGHTGUN_TURBO
    PAUSE = RETRO_DEVICE_ID_LIGHTGUN_PAUSE

    def __init__(self, value: int):
        self._type_ = 'H'

    @property
    def is_button(self) -> bool:
        return self in {
            self.TRIGGER,
            self.RELOAD,
            self.AUX_A,
            self.AUX_B,
            self.START,
            self.SELECT,
            self.AUX_C,
            self.DPAD_UP,
            self.DPAD_DOWN,
            self.DPAD_LEFT,
            self.DPAD_RIGHT,
        }
