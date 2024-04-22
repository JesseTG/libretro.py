from ctypes import CFUNCTYPE, Structure, c_bool, c_float, c_int64, c_uint
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints

RETRO_THROTTLE_NONE = 0
RETRO_THROTTLE_FRAME_STEPPING = 1
RETRO_THROTTLE_FAST_FORWARD = 2
RETRO_THROTTLE_SLOW_MOTION = 3
RETRO_THROTTLE_REWINDING = 4
RETRO_THROTTLE_VSYNC = 5
RETRO_THROTTLE_UNBLOCKED = 6


retro_usec_t = c_int64
retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


@dataclass(init=False)
class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t

    def __call__(self, time: int | None = None):
        if not isinstance(time, int) and time is not None:
            raise TypeError(f"time must be an int or None, not {type(time).__name__}")

        if self.callback:
            if time is None:
                self.callback(self.reference)
            else:
                self.callback(time)

    def __deepcopy__(self, _):
        return retro_frame_time_callback(self.callback, self.reference)


class ThrottleMode(IntEnum):
    NONE = RETRO_THROTTLE_NONE
    FRAME_STEPPING = RETRO_THROTTLE_FRAME_STEPPING
    FAST_FORWARD = RETRO_THROTTLE_FAST_FORWARD
    SLOW_MOTION = RETRO_THROTTLE_SLOW_MOTION
    REWINDING = RETRO_THROTTLE_REWINDING
    VSYNC = RETRO_THROTTLE_VSYNC
    UNBLOCKED = RETRO_THROTTLE_UNBLOCKED

    def __init__(self, value: int):
        self._type_ = "I"


@dataclass(init=False)
class retro_fastforwarding_override(Structure, metaclass=FieldsFromTypeHints):
    ratio: c_float
    fastforward: c_bool
    notification: c_bool
    inhibit_toggle: c_bool

    def __deepcopy__(self, _):
        return retro_fastforwarding_override(
            self.ratio, self.fastforward, self.notification, self.inhibit_toggle
        )


@dataclass(init=False)
class retro_throttle_state(Structure, metaclass=FieldsFromTypeHints):
    mode: c_uint
    rate: c_float

    def __deepcopy__(self, _):
        return retro_throttle_state(self.mode, self.rate)


__all__ = [
    "ThrottleMode",
    "retro_fastforwarding_override",
    "retro_throttle_state",
    "retro_frame_time_callback",
    "retro_usec_t",
    "retro_frame_time_callback_t",
]
