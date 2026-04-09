from ctypes import Structure, c_bool, c_double, c_uint
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

retro_location_set_interval_t = TypedFunctionPointer[None, [CIntArg[c_uint], CIntArg[c_uint]]]
retro_location_start_t = TypedFunctionPointer[c_bool, []]
retro_location_stop_t = TypedFunctionPointer[None, []]
retro_location_get_position_t = TypedFunctionPointer[
    c_bool,
    [
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
    ],
]
retro_location_lifetime_status_t = TypedFunctionPointer[None, []]


@dataclass(init=False, slots=True)
class retro_location_callback(Structure):
    start: retro_location_start_t | None
    stop: retro_location_stop_t | None
    get_position: retro_location_get_position_t | None
    set_interval: retro_location_set_interval_t | None
    initialized: retro_location_lifetime_status_t | None
    deinitialized: retro_location_lifetime_status_t | None

    _fields_ = (
        ("start", retro_location_start_t),
        ("stop", retro_location_stop_t),
        ("get_position", retro_location_get_position_t),
        ("set_interval", retro_location_set_interval_t),
        ("initialized", retro_location_lifetime_status_t),
        ("deinitialized", retro_location_lifetime_status_t),
    )

    def __deepcopy__(self, _):
        return retro_location_callback(
            self.start,
            self.stop,
            self.get_position,
            self.set_interval,
            self.initialized,
            self.deinitialized,
        )


__all__ = [
    "retro_location_callback",
    "retro_location_get_position_t",
    "retro_location_lifetime_status_t",
    "retro_location_set_interval_t",
    "retro_location_start_t",
    "retro_location_stop_t",
]
