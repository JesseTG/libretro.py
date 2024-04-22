from ctypes import CFUNCTYPE, POINTER, Structure, c_bool, c_char_p, c_int64, c_uint64
from dataclasses import dataclass
from enum import IntFlag

from libretro.api._utils import FieldsFromTypeHints

RETRO_SIMD_SSE = 1 << 0
RETRO_SIMD_SSE2 = 1 << 1
RETRO_SIMD_VMX = 1 << 2
RETRO_SIMD_VMX128 = 1 << 3
RETRO_SIMD_AVX = 1 << 4
RETRO_SIMD_NEON = 1 << 5
RETRO_SIMD_SSE3 = 1 << 6
RETRO_SIMD_SSSE3 = 1 << 7
RETRO_SIMD_MMX = 1 << 8
RETRO_SIMD_MMXEXT = 1 << 9
RETRO_SIMD_SSE4 = 1 << 10
RETRO_SIMD_SSE42 = 1 << 11
RETRO_SIMD_AVX2 = 1 << 12
RETRO_SIMD_VFPU = 1 << 13
RETRO_SIMD_PS = 1 << 14
RETRO_SIMD_AES = 1 << 15
RETRO_SIMD_VFPV3 = 1 << 16
RETRO_SIMD_VFPV4 = 1 << 17
RETRO_SIMD_POPCNT = 1 << 18
RETRO_SIMD_MOVBE = 1 << 19
RETRO_SIMD_CMOV = 1 << 20
RETRO_SIMD_ASIMD = 1 << 21


retro_perf_tick_t = c_uint64
retro_time_t = c_int64


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


@dataclass(init=False)
class retro_perf_counter(Structure, metaclass=FieldsFromTypeHints):
    ident: c_char_p
    start: retro_perf_tick_t
    total: retro_perf_tick_t
    call_cnt: retro_perf_tick_t
    registered: c_bool

    def __deepcopy__(self, _):
        return retro_perf_counter(
            self.ident,
            self.start,
            self.total,
            self.call_cnt,
            self.registered,
        )


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

    def __deepcopy__(self, _):
        return retro_perf_callback(
            self.get_time_usec,
            self.get_cpu_features,
            self.get_perf_counter,
            self.perf_register,
            self.perf_start,
            self.perf_stop,
            self.perf_log,
        )


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
    "retro_time_t",
    "retro_perf_tick_t",
]
