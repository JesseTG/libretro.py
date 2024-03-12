from ctypes import CFUNCTYPE, POINTER, c_bool, c_double, c_uint, Structure

from ..retro import FieldsFromTypeHints

retro_location_set_interval_t = CFUNCTYPE(None, c_uint, c_uint)
retro_location_start_t = CFUNCTYPE(c_bool, )
retro_location_stop_t = CFUNCTYPE(None, )
retro_location_get_position_t = CFUNCTYPE(c_bool, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double))
retro_location_lifetime_status_t = CFUNCTYPE(None, )


class retro_location_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_location_start_t
    stop: retro_location_stop_t
    get_position: retro_location_get_position_t
    set_interval: retro_location_set_interval_t
    initialized: retro_location_lifetime_status_t
    deinitialized: retro_location_lifetime_status_t
