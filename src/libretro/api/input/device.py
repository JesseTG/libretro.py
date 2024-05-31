from ctypes import CFUNCTYPE, POINTER, Structure, c_char_p, c_int16, c_uint
from dataclasses import dataclass
from enum import CONFORM, IntEnum, IntFlag
from typing import NewType, Sequence, overload

from libretro.api._utils import FieldsFromTypeHints, deepcopy_array

Port = NewType("Port", int)

RETRO_DEVICE_NONE = 0
RETRO_DEVICE_JOYPAD = 1
RETRO_DEVICE_MOUSE = 2
RETRO_DEVICE_KEYBOARD = 3
RETRO_DEVICE_LIGHTGUN = 4
RETRO_DEVICE_ANALOG = 5
RETRO_DEVICE_POINTER = 6

retro_input_poll_t = CFUNCTYPE(None)
retro_input_state_t = CFUNCTYPE(c_int16, c_uint, c_uint, c_uint, c_uint)


RETRO_DEVICE_TYPE_SHIFT = 8
RETRO_DEVICE_MASK = (1 << RETRO_DEVICE_TYPE_SHIFT) - 1


def RETRO_DEVICE_SUBCLASS(base: int, id: int) -> int:
    return ((id + 1) << RETRO_DEVICE_TYPE_SHIFT) | base


class InputDeviceFlag(IntFlag, boundary=CONFORM):
    NONE = 1 << RETRO_DEVICE_NONE
    JOYPAD = 1 << RETRO_DEVICE_JOYPAD
    MOUSE = 1 << RETRO_DEVICE_MOUSE
    KEYBOARD = 1 << RETRO_DEVICE_KEYBOARD
    LIGHTGUN = 1 << RETRO_DEVICE_LIGHTGUN
    ANALOG = 1 << RETRO_DEVICE_ANALOG
    POINTER = 1 << RETRO_DEVICE_POINTER

    ALL = JOYPAD | MOUSE | KEYBOARD | LIGHTGUN | ANALOG | POINTER


class InputDevice(IntEnum):
    NONE = RETRO_DEVICE_NONE
    JOYPAD = RETRO_DEVICE_JOYPAD
    MOUSE = RETRO_DEVICE_MOUSE
    KEYBOARD = RETRO_DEVICE_KEYBOARD
    LIGHTGUN = RETRO_DEVICE_LIGHTGUN
    ANALOG = RETRO_DEVICE_ANALOG
    POINTER = RETRO_DEVICE_POINTER

    def __init__(self, value: int):
        self._type_ = "H"

    @property
    def flag(self) -> InputDeviceFlag:
        return InputDeviceFlag(1 << self.value)


@dataclass(init=False)
class retro_input_descriptor(Structure, metaclass=FieldsFromTypeHints):
    port: c_uint
    device: c_uint
    index: c_uint
    id: c_uint
    description: c_char_p

    def __deepcopy__(self, _):
        return retro_input_descriptor(
            port=self.port,
            device=self.device,
            index=self.index,
            id=self.id,
            description=self.description,
        )


@dataclass(init=False)
class retro_controller_description(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    id: c_uint

    def __deepcopy__(self, _):
        return retro_controller_description(self.desc, self.id)


@dataclass(init=False)
class retro_controller_info(Structure, metaclass=FieldsFromTypeHints):
    types: POINTER(retro_controller_description)
    num_types: c_uint

    def __deepcopy__(self, memo):
        return retro_controller_info(
            types=(deepcopy_array(self.types, self.num_types, memo) if self.types else None),
            num_types=self.num_types,
        )

    @overload
    def __getitem__(self, index: int) -> retro_controller_description: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[retro_controller_description]: ...

    def __getitem__(self, index):
        if not self.types:
            raise ValueError("No controller types available")

        match index:
            case int(i):
                if not (0 <= i < self.num_types):
                    raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
                return self.types[i]

            case slice() as s:
                s: slice
                return self.types[s]

            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __len__(self):
        return int(self.num_types)


class InputDeviceState:
    """
    Empty marker class for identifying input device states.
    """

    pass


__all__ = [
    "InputDeviceFlag",
    "InputDevice",
    "retro_input_poll_t",
    "retro_input_state_t",
    "retro_input_descriptor",
    "retro_controller_description",
    "retro_controller_info",
    "InputDeviceState",
    "Port",
]
