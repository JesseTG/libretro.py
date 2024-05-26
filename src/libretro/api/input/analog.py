from dataclasses import dataclass
from enum import IntEnum

from .device import InputDeviceState
from .joypad import DeviceIdJoypad

RETRO_DEVICE_INDEX_ANALOG_LEFT = 0
RETRO_DEVICE_INDEX_ANALOG_RIGHT = 1
RETRO_DEVICE_INDEX_ANALOG_BUTTON = 2

RETRO_DEVICE_ID_ANALOG_X = 0
RETRO_DEVICE_ID_ANALOG_Y = 1


class DeviceIndexAnalog(IntEnum):
    LEFT = RETRO_DEVICE_INDEX_ANALOG_LEFT
    RIGHT = RETRO_DEVICE_INDEX_ANALOG_RIGHT
    BUTTON = RETRO_DEVICE_INDEX_ANALOG_BUTTON

    def __init__(self, value: int):
        self._type_ = "H"


class DeviceIdAnalog(IntEnum):
    X = RETRO_DEVICE_ID_ANALOG_X
    Y = RETRO_DEVICE_ID_ANALOG_Y

    def __init__(self, value: int):
        self._type_ = "H"


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

    lstick: tuple[int, int] = (0, 0)
    rstick: tuple[int, int] = (0, 0)

    @property
    def left_x(self) -> int:
        return self.lstick[0]

    @property
    def left_y(self) -> int:
        return self.lstick[1]

    @property
    def right_x(self) -> int:
        return self.rstick[0]

    @property
    def right_y(self) -> int:
        return self.rstick[1]

    def __getitem__(self, item) -> int:
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
            case int():
                raise IndexError(f"Index {item} is not a valid DeviceIdJoypad")
            case _:
                raise TypeError(f"Expected an int or DeviceIdJoypad, got {item!r}")


__all__ = ["DeviceIndexAnalog", "DeviceIdAnalog", "AnalogState"]
