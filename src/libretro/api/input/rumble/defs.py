from ctypes import *
from dataclasses import dataclass
from enum import IntEnum

from ....h import retro_rumble_effect, RETRO_RUMBLE_STRONG, RETRO_RUMBLE_WEAK
from ...._utils import FieldsFromTypeHints

retro_set_rumble_state_t = CFUNCTYPE(c_bool, c_uint, retro_rumble_effect, c_uint16)


class RumbleEffect(IntEnum):
    STRONG = RETRO_RUMBLE_STRONG
    WEAK = RETRO_RUMBLE_WEAK


@dataclass(init=False)
class retro_rumble_interface(Structure, metaclass=FieldsFromTypeHints):
    set_rumble_state: retro_set_rumble_state_t


__all__ = [
    'retro_set_rumble_state_t',
    'RumbleEffect',
    'retro_rumble_interface',
]
