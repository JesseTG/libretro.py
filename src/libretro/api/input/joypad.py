from dataclasses import dataclass
from enum import IntEnum

from .device import InputDeviceState

RETRO_DEVICE_ID_JOYPAD_B = 0
RETRO_DEVICE_ID_JOYPAD_Y = 1
RETRO_DEVICE_ID_JOYPAD_SELECT = 2
RETRO_DEVICE_ID_JOYPAD_START = 3
RETRO_DEVICE_ID_JOYPAD_UP = 4
RETRO_DEVICE_ID_JOYPAD_DOWN = 5
RETRO_DEVICE_ID_JOYPAD_LEFT = 6
RETRO_DEVICE_ID_JOYPAD_RIGHT = 7
RETRO_DEVICE_ID_JOYPAD_A = 8
RETRO_DEVICE_ID_JOYPAD_X = 9
RETRO_DEVICE_ID_JOYPAD_L = 10
RETRO_DEVICE_ID_JOYPAD_R = 11
RETRO_DEVICE_ID_JOYPAD_L2 = 12
RETRO_DEVICE_ID_JOYPAD_R2 = 13
RETRO_DEVICE_ID_JOYPAD_L3 = 14
RETRO_DEVICE_ID_JOYPAD_R3 = 15
RETRO_DEVICE_ID_JOYPAD_MASK = 256


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
        self._type_ = "H"


@dataclass(frozen=True, slots=True)
class JoypadState(InputDeviceState):
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

    def __getitem__(self, item) -> bool | int:
        match item:
            case DeviceIdJoypad.B:
                return self.b
            case DeviceIdJoypad.Y:
                return self.y
            case DeviceIdJoypad.SELECT:
                return self.select
            case DeviceIdJoypad.START:
                return self.start
            case DeviceIdJoypad.UP:
                return self.up
            case DeviceIdJoypad.DOWN:
                return self.down
            case DeviceIdJoypad.LEFT:
                return self.left
            case DeviceIdJoypad.RIGHT:
                return self.right
            case DeviceIdJoypad.A:
                return self.a
            case DeviceIdJoypad.X:
                return self.x
            case DeviceIdJoypad.L:
                return self.l
            case DeviceIdJoypad.R:
                return self.r
            case DeviceIdJoypad.L2:
                return self.l2
            case DeviceIdJoypad.R2:
                return self.r2
            case DeviceIdJoypad.L3:
                return self.l3
            case DeviceIdJoypad.R3:
                return self.r3
            case DeviceIdJoypad.MASK:
                return self.mask
            case int():
                raise IndexError(f"Index {item} is not a valid DeviceIdJoypad")
            case _:
                raise TypeError(f"Expected an int or DeviceIdJoypad, got {item!r}")

    @property
    def mask(self) -> int:
        return (
            (self.b << 0)
            | (self.y << 1)
            | (self.select << 2)
            | (self.start << 3)
            | (self.up << 4)
            | (self.down << 5)
            | (self.left << 6)
            | (self.right << 7)
            | (self.a << 8)
            | (self.x << 9)
            | (self.l << 10)
            | (self.r << 11)
            | (self.l2 << 12)
            | (self.r2 << 13)
            | (self.l3 << 14)
            | (self.r3 << 15)
        )


__all__ = ["DeviceIdJoypad", "JoypadState"]
