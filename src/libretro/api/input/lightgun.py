from dataclasses import dataclass
from enum import IntEnum

from .device import InputDeviceState

RETRO_DEVICE_ID_LIGHTGUN_SCREEN_X = 13
RETRO_DEVICE_ID_LIGHTGUN_SCREEN_Y = 14
RETRO_DEVICE_ID_LIGHTGUN_IS_OFFSCREEN = 15
RETRO_DEVICE_ID_LIGHTGUN_TRIGGER = 2
RETRO_DEVICE_ID_LIGHTGUN_RELOAD = 16
RETRO_DEVICE_ID_LIGHTGUN_AUX_A = 3
RETRO_DEVICE_ID_LIGHTGUN_AUX_B = 4
RETRO_DEVICE_ID_LIGHTGUN_START = 6
RETRO_DEVICE_ID_LIGHTGUN_SELECT = 7
RETRO_DEVICE_ID_LIGHTGUN_AUX_C = 8
RETRO_DEVICE_ID_LIGHTGUN_DPAD_UP = 9
RETRO_DEVICE_ID_LIGHTGUN_DPAD_DOWN = 10
RETRO_DEVICE_ID_LIGHTGUN_DPAD_LEFT = 11
RETRO_DEVICE_ID_LIGHTGUN_DPAD_RIGHT = 12
RETRO_DEVICE_ID_LIGHTGUN_X = 0
RETRO_DEVICE_ID_LIGHTGUN_Y = 1
RETRO_DEVICE_ID_LIGHTGUN_CURSOR = 3
RETRO_DEVICE_ID_LIGHTGUN_TURBO = 4
RETRO_DEVICE_ID_LIGHTGUN_PAUSE = 5


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
        self._type_ = "H"

    @property
    def is_button(self) -> bool:
        return self not in (
            self.SCREEN_X,
            self.SCREEN_Y,
            self.IS_OFFSCREEN,
            self.X,
            self.Y,
        )


@dataclass(frozen=True, slots=True)
class LightGunState(InputDeviceState):
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

    def __getitem__(self, item) -> int | bool:
        match item:
            case DeviceIdLightgun.SCREEN_X:
                return self.screen_x
            case DeviceIdLightgun.SCREEN_Y:
                return self.screen_y
            case DeviceIdLightgun.IS_OFFSCREEN:
                return self.is_offscreen
            case DeviceIdLightgun.TRIGGER:
                return self.trigger
            case DeviceIdLightgun.RELOAD:
                return self.reload
            case DeviceIdLightgun.AUX_A:
                return self.aux_a
            case DeviceIdLightgun.AUX_B:
                return self.aux_b
            case DeviceIdLightgun.START:
                return self.start
            case DeviceIdLightgun.SELECT:
                return self.select
            case DeviceIdLightgun.AUX_C:
                return self.aux_c
            case DeviceIdLightgun.DPAD_UP:
                return self.dpad_up
            case DeviceIdLightgun.DPAD_DOWN:
                return self.dpad_down
            case DeviceIdLightgun.DPAD_LEFT:
                return self.dpad_left
            case DeviceIdLightgun.DPAD_RIGHT:
                return self.dpad_right
            case DeviceIdLightgun.X:
                return self.x
            case DeviceIdLightgun.Y:
                return self.y
            case int():
                raise IndexError(f"Index {item!r} is not a valid DeviceIdLightgun")
            case _:
                raise KeyError(f"Expected an int or DeviceIdLightgun, got {item!r}")


__all__ = ["DeviceIdLightgun", "LightGunState"]
