from ctypes import CFUNCTYPE, Structure, c_bool, c_int, c_uint, c_uint16
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints

retro_rumble_effect = c_int
RETRO_RUMBLE_STRONG = 0
RETRO_RUMBLE_WEAK = 1
RETRO_RUMBLE_DUMMY = 0x7FFFFFFF

retro_set_rumble_state_t = CFUNCTYPE(c_bool, c_uint, retro_rumble_effect, c_uint16)


class RumbleEffect(IntEnum):
    STRONG = RETRO_RUMBLE_STRONG
    WEAK = RETRO_RUMBLE_WEAK


@dataclass(init=False)
class retro_rumble_interface(Structure, metaclass=FieldsFromTypeHints):
    set_rumble_state: retro_set_rumble_state_t

    def __deepcopy__(self, _):
        return retro_rumble_interface(self.set_rumble_state)


__all__ = [
    "retro_set_rumble_state_t",
    "RumbleEffect",
    "retro_rumble_interface",
    "retro_rumble_effect",
]
