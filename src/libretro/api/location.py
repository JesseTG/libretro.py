from ctypes import CFUNCTYPE, Structure, c_bool, c_double, c_uint
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libretro.api._utils import c_double_p

if TYPE_CHECKING:
    from libretro.typing import CoreFunctionPointer, FrontendFunctionPointer, Pointer

    retro_location_set_interval_t = FrontendFunctionPointer[None, [c_uint, c_uint]]
    retro_location_start_t = FrontendFunctionPointer[c_bool, []]
    retro_location_stop_t = FrontendFunctionPointer[None, []]
    retro_location_get_position_t = FrontendFunctionPointer[
        c_bool,
        [
            Pointer[c_double] | None,
            Pointer[c_double] | None,
            Pointer[c_double] | None,
            Pointer[c_double] | None,
        ],
    ]
    retro_location_lifetime_status_t = CoreFunctionPointer[None, []]
else:
    retro_location_set_interval_t = CFUNCTYPE(None, c_uint, c_uint)
    retro_location_start_t = CFUNCTYPE(c_bool)
    retro_location_stop_t = CFUNCTYPE(None)
    retro_location_get_position_t = CFUNCTYPE(
        c_bool, c_double_p, c_double_p, c_double_p, c_double_p
    )
    retro_location_lifetime_status_t = CFUNCTYPE(None)


@dataclass(init=False)
class retro_location_callback(Structure):
    start: retro_location_start_t | None
    stop: retro_location_stop_t | None
    get_position: retro_location_get_position_t | None
    set_interval: retro_location_set_interval_t | None
    initialized: retro_location_lifetime_status_t | None
    deinitialized: retro_location_lifetime_status_t | None

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
