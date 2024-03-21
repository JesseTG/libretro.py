from ctypes import *
from dataclasses import dataclass
from enum import IntEnum

from .._utils import FieldsFromTypeHints
from ..h import *


class ThrottleMode(IntEnum):
    NONE = RETRO_THROTTLE_NONE
    FRAME_STEPPING = RETRO_THROTTLE_FRAME_STEPPING
    FAST_FORWARD = RETRO_THROTTLE_FAST_FORWARD
    SLOW_MOTION = RETRO_THROTTLE_SLOW_MOTION
    REWINDING = RETRO_THROTTLE_REWINDING
    VSYNC = RETRO_THROTTLE_VSYNC
    UNBLOCKED = RETRO_THROTTLE_UNBLOCKED

    def __init__(self, value: int):
        self._type_ = 'I'


@dataclass(init=False)
class retro_fastforwarding_override(Structure, metaclass=FieldsFromTypeHints):
    ratio: c_float
    fastforward: c_bool
    notification: c_bool
    inhibit_toggle: c_bool


@dataclass(init=False)
class retro_throttle_state(Structure, metaclass=FieldsFromTypeHints):
    mode: c_uint
    rate: c_float


__all__ = [
    'ThrottleMode',
    'retro_fastforwarding_override',
    'retro_throttle_state'
]
