from ctypes import CFUNCTYPE, POINTER, c_bool, c_double, c_uint, Structure

from ..._utils import FieldsFromTypeHints

c_double_p = POINTER(c_double)
retro_location_set_interval_t = CFUNCTYPE(None, c_uint, c_uint)
retro_location_start_t = CFUNCTYPE(c_bool)
retro_location_stop_t = CFUNCTYPE(None)
retro_location_get_position_t = CFUNCTYPE(c_bool, c_double_p, c_double_p, c_double_p, c_double_p)
retro_location_lifetime_status_t = CFUNCTYPE(None)


class retro_location_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_location_start_t
    stop: retro_location_stop_t
    get_position: retro_location_get_position_t
    set_interval: retro_location_set_interval_t
    initialized: retro_location_lifetime_status_t
    deinitialized: retro_location_lifetime_status_t


__all__ = [
    'retro_location_callback',
    'retro_location_get_position_t',
    'retro_location_lifetime_status_t',
    'retro_location_set_interval_t',
    'retro_location_start_t',
    'retro_location_stop_t',
]
