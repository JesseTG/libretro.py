from dataclasses import dataclass
from enum import IntEnum

from .device import InputDeviceState

RETRO_DEVICE_ID_MOUSE_X = 0
RETRO_DEVICE_ID_MOUSE_Y = 1
RETRO_DEVICE_ID_MOUSE_LEFT = 2
RETRO_DEVICE_ID_MOUSE_RIGHT = 3
RETRO_DEVICE_ID_MOUSE_WHEELUP = 4
RETRO_DEVICE_ID_MOUSE_WHEELDOWN = 5
RETRO_DEVICE_ID_MOUSE_MIDDLE = 6
RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELUP = 7
RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELDOWN = 8
RETRO_DEVICE_ID_MOUSE_BUTTON_4 = 9
RETRO_DEVICE_ID_MOUSE_BUTTON_5 = 10


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
        self._type_ = "H"


@dataclass(frozen=True, slots=True)
class MouseState(InputDeviceState):
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

    def __getitem__(self, item) -> bool | int:
        match item:
            case DeviceIdMouse.X:
                return self.x
            case DeviceIdMouse.Y:
                return self.y
            case DeviceIdMouse.LEFT:
                return self.left
            case DeviceIdMouse.RIGHT:
                return self.right
            case DeviceIdMouse.WHEELUP:
                return self.wheel_up
            case DeviceIdMouse.WHEELDOWN:
                return self.wheel_down
            case DeviceIdMouse.MIDDLE:
                return self.middle
            case DeviceIdMouse.HORIZ_WHEELUP:
                return self.horizontal_wheel_up
            case DeviceIdMouse.HORIZ_WHEELDOWN:
                return self.horizontal_wheel_down
            case DeviceIdMouse.BUTTON_4:
                return self.button4
            case DeviceIdMouse.BUTTON_5:
                return self.button5
            case int():
                raise IndexError(f"Index {item!r} is not a valid DeviceIdMouse")
            case _:
                raise KeyError(f"Expected an int or DeviceIdMouse, got {item!r}")


__all__ = ["DeviceIdMouse", "MouseState"]
