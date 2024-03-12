from ctypes import *

from ..h import retro_rumble_effect
from .._utils import FieldsFromTypeHints

retro_set_rumble_state_t = CFUNCTYPE(c_bool, c_uint, retro_rumble_effect, c_uint16)


class retro_rumble_interface(Structure, metaclass=FieldsFromTypeHints):
    set_rumble_state: retro_set_rumble_state_t
