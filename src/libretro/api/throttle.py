from ctypes import *

from ..retro import FieldsFromTypeHints


class retro_fastforwarding_override(Structure, metaclass=FieldsFromTypeHints):
    ratio: c_float
    fastforward: c_bool
    notification: c_bool
    inhibit_toggle: c_bool


class retro_throttle_state(Structure, metaclass=FieldsFromTypeHints):
    mode: c_uint
    rate: c_float