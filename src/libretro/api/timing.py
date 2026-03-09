from ctypes import CFUNCTYPE, Structure, c_bool, c_float, c_int64, c_uint
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

RETRO_THROTTLE_NONE = 0
RETRO_THROTTLE_FRAME_STEPPING = 1
RETRO_THROTTLE_FAST_FORWARD = 2
RETRO_THROTTLE_SLOW_MOTION = 3
RETRO_THROTTLE_REWINDING = 4
RETRO_THROTTLE_VSYNC = 5
RETRO_THROTTLE_UNBLOCKED = 6


retro_usec_t = c_int64

if TYPE_CHECKING:
    from libretro.typing import ConvertibleToInteger, CoreFunctionPointer

    retro_frame_time_callback_t = CoreFunctionPointer[None, [ConvertibleToInteger[retro_usec_t]]]
else:
    retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


@dataclass(init=False)
class retro_frame_time_callback(Structure):
    if TYPE_CHECKING:
        callback: retro_frame_time_callback_t | None
        reference: int
    else:
        _fields_ = [
            ("callback", retro_frame_time_callback_t),
            ("reference", c_uint),
        ]

    def __call__(self, time: ConvertibleToInteger[retro_usec_t] | None = None):
        """
        Calls the callback with the given time, or with the reference if time is None.
        Does nothing if the callback is unset.
        """

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


@dataclass(init=False)
class retro_fastforwarding_override(Structure):
    if TYPE_CHECKING:
        ratio: float
        fastforward: bool
        notification: bool
        inhibit_toggle: bool
    else:
        _fields_ = [
            ("ratio", c_float),
            ("fastforward", c_bool),
            ("notification", c_bool),
            ("inhibit_toggle", c_bool),
        ]

    def __deepcopy__(self, _):
        return retro_fastforwarding_override(
            self.ratio, self.fastforward, self.notification, self.inhibit_toggle
        )


@dataclass(init=False)
class retro_throttle_state(Structure):
    if TYPE_CHECKING:
        mode: ThrottleMode
        rate: float
    else:
        _fields_ = [
            ("mode", c_uint),
            ("rate", c_float),
        ]

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
