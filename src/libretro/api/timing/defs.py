from ctypes import *
from dataclasses import dataclass
from enum import IntEnum

from ..._utils import FieldsFromTypeHints
from ...h import *

retro_usec_t = c_int64
retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


@dataclass(init=False)
class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t

    def __call__(self):
        if self.callback:
            self.callback(self.reference)

    def __deepcopy__(self, _):
        return retro_frame_time_callback(self.callback, int(self.reference))


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

    def __deepcopy__(self, _):
        return retro_fastforwarding_override(
            self.ratio,
            self.fastforward,
            self.notification,
            self.inhibit_toggle
        )


@dataclass(init=False)
class retro_throttle_state(Structure, metaclass=FieldsFromTypeHints):
    mode: c_uint
    rate: c_float

    def __deepcopy__(self, _):
        return retro_throttle_state(self.mode, self.rate)


__all__ = [
    'ThrottleMode',
    'retro_fastforwarding_override',
    'retro_throttle_state',
    'retro_frame_time_callback',
    'retro_usec_t',
    'retro_frame_time_callback_t',
]
