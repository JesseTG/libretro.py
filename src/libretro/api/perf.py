from ctypes import *

from ..h import retro_time_t, retro_perf_tick_t
from ..retro import FieldsFromTypeHints, UNCHECKED


class retro_perf_counter(Structure, metaclass=FieldsFromTypeHints):
    ident: c_char_p
    start: retro_perf_tick_t
    total: retro_perf_tick_t
    call_cnt: retro_perf_tick_t
    registered: c_bool


retro_perf_get_time_usec_t = CFUNCTYPE(UNCHECKED(retro_time_t), )
retro_perf_get_counter_t = CFUNCTYPE(UNCHECKED(retro_perf_tick_t), )
retro_get_cpu_features_t = CFUNCTYPE(c_uint64, )
retro_perf_log_t = CFUNCTYPE(None, )
retro_perf_register_t = CFUNCTYPE(None, POINTER(retro_perf_counter))
retro_perf_start_t = CFUNCTYPE(None, POINTER(retro_perf_counter))
retro_perf_stop_t = CFUNCTYPE(None, POINTER(retro_perf_counter))

class retro_perf_callback(Structure, metaclass=FieldsFromTypeHints):
    get_time_usec: retro_perf_get_time_usec_t
    get_cpu_features: retro_get_cpu_features_t
    get_perf_counter: retro_perf_get_counter_t
    perf_register: retro_perf_register_t
    perf_start: retro_perf_start_t
    perf_stop: retro_perf_stop_t
    perf_log: retro_perf_log_t
