from ctypes import *
from dataclasses import dataclass
from enum import IntFlag

from ...h import *
from ..._utils import FieldsFromTypeHints


class CpuFeatures(IntFlag):
    SSE = RETRO_SIMD_SSE
    SSE2 = RETRO_SIMD_SSE2
    VMX = RETRO_SIMD_VMX
    VMX128 = RETRO_SIMD_VMX128
    AVX = RETRO_SIMD_AVX
    NEON = RETRO_SIMD_NEON
    SSE3 = RETRO_SIMD_SSE3
    SSSE3 = RETRO_SIMD_SSSE3
    MMX = RETRO_SIMD_MMX
    MMXEXT = RETRO_SIMD_MMXEXT
    SSE4 = RETRO_SIMD_SSE4
    SSE42 = RETRO_SIMD_SSE42
    AVX2 = RETRO_SIMD_AVX2
    VFPU = RETRO_SIMD_VFPU
    PS = RETRO_SIMD_PS
    AES = RETRO_SIMD_AES
    VFPV3 = RETRO_SIMD_VFPV3
    VFPV4 = RETRO_SIMD_VFPV4
    POPCNT = RETRO_SIMD_POPCNT
    MOVBE = RETRO_SIMD_MOVBE
    CMOV = RETRO_SIMD_CMOV
    ASIMD = RETRO_SIMD_ASIMD


class retro_perf_counter(Structure, metaclass=FieldsFromTypeHints):
    ident: c_char_p
    start: retro_perf_tick_t
    total: retro_perf_tick_t
    call_cnt: retro_perf_tick_t
    registered: c_bool


retro_perf_get_time_usec_t = CFUNCTYPE(retro_time_t)
retro_perf_get_counter_t = CFUNCTYPE(retro_perf_tick_t)
retro_get_cpu_features_t = CFUNCTYPE(c_uint64)
retro_perf_log_t = CFUNCTYPE(None)
retro_perf_register_t = CFUNCTYPE(None, POINTER(retro_perf_counter))
retro_perf_start_t = CFUNCTYPE(None, POINTER(retro_perf_counter))
retro_perf_stop_t = CFUNCTYPE(None, POINTER(retro_perf_counter))


@dataclass(init=False)
class retro_perf_callback(Structure, metaclass=FieldsFromTypeHints):
    get_time_usec: retro_perf_get_time_usec_t
    get_cpu_features: retro_get_cpu_features_t
    get_perf_counter: retro_perf_get_counter_t
    perf_register: retro_perf_register_t
    perf_start: retro_perf_start_t
    perf_stop: retro_perf_stop_t
    perf_log: retro_perf_log_t


__all__ = [
    "CpuFeatures",
    "retro_perf_counter",
    "retro_perf_get_time_usec_t",
    "retro_perf_get_counter_t",
    "retro_get_cpu_features_t",
    "retro_perf_log_t",
    "retro_perf_register_t",
    "retro_perf_start_t",
    "retro_perf_stop_t",
    "retro_perf_callback",
]
