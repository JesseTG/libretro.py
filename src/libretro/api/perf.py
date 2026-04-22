"""
Performance counter and SIMD feature detection types.

Corresponds to :c:type:`retro_perf_callback`, :c:type:`retro_perf_counter`,
and the ``RETRO_SIMD_*`` constants in ``libretro.h``.

.. seealso::
    :class:`.PerfDriver`
        The :class:`~typing.Protocol` that uses these types
        to expose performance counting functionality to the :class:`.Core`.

    :mod:`libretro.drivers.perf`
        libretro.py's included :class:`.PerfDriver` implementations.
"""

from ctypes import Structure, c_bool, c_char_p, c_int64, c_uint64
from dataclasses import dataclass
from enum import IntFlag

from libretro.ctypes import TypedFunctionPointer, TypedPointer

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
"""A performance counter tick value."""

retro_time_t = c_int64
"""A timestamp in microseconds."""


class CpuFeatures(IntFlag):
    """
    SIMD instruction set flags reported by the host CPU.

    Corresponds to the ``RETRO_SIMD_*`` constants in ``libretro.h``.

    >>> from libretro.api import CpuFeatures
    >>> CpuFeatures.SSE
    <CpuFeatures.SSE: 1>
    """

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


@dataclass(init=False, slots=True)
class retro_perf_counter(Structure):
    """
    A named performance counter for profiling hot code paths within a :class:`.Core`.

    Corresponds to :c:type:`retro_perf_counter` in ``libretro.h``.

    >>> from libretro.api import retro_perf_counter
    >>> c = retro_perf_counter()
    >>> c.registered
    False
    """

    ident: bytes | None
    """Human-readable identifier for this counter."""
    start: int
    """Tick value at the most recent start of measurement."""
    total: int
    """Total accumulated ticks for this counter."""
    call_cnt: int
    """Number of times this counter has been started."""
    registered: bool
    """Whether this counter has been registered with the frontend."""

    _fields_ = (
        ("ident", c_char_p),
        ("start", retro_perf_tick_t),
        ("total", retro_perf_tick_t),
        ("call_cnt", retro_perf_tick_t),
        ("registered", c_bool),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object,
        including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_perf_counter(
            self.ident,
            self.start,
            self.total,
            self.call_cnt,
            self.registered,
        )


retro_perf_get_time_usec_t = TypedFunctionPointer[retro_time_t, []]
"""Returns the current time in microseconds."""

retro_perf_get_counter_t = TypedFunctionPointer[retro_perf_tick_t, []]
"""Returns the current performance counter value."""

retro_get_cpu_features_t = TypedFunctionPointer[c_uint64, []]
"""Returns a bitmask of :class:`CpuFeatures`."""

retro_perf_log_t = TypedFunctionPointer[None, []]
"""Logs all registered performance counters."""

retro_perf_register_t = TypedFunctionPointer[None, [TypedPointer[retro_perf_counter]]]
"""Registers a performance counter for tracking."""

retro_perf_start_t = TypedFunctionPointer[None, [TypedPointer[retro_perf_counter]]]
"""Starts timing a performance counter."""

retro_perf_stop_t = TypedFunctionPointer[None, [TypedPointer[retro_perf_counter]]]
"""Stops timing a performance counter."""


@dataclass(init=False, slots=True)
class retro_perf_callback(Structure):
    """
    Provides functions for performance profiling and CPU feature detection.

    Corresponds to :c:type:`retro_perf_callback` in ``libretro.h``.
    """

    get_time_usec: retro_perf_get_time_usec_t | None
    """Returns the current time in microseconds."""
    get_cpu_features: retro_get_cpu_features_t | None
    """Returns a bitmask of :class:`CpuFeatures`."""
    get_perf_counter: retro_perf_get_counter_t | None
    """Returns the current performance counter tick value."""
    perf_register: retro_perf_register_t | None
    """Registers a performance counter."""
    perf_start: retro_perf_start_t | None
    """Starts a performance counter."""
    perf_stop: retro_perf_stop_t | None
    """Stops a performance counter."""
    perf_log: retro_perf_log_t | None
    """Logs all registered performance counters."""

    _fields_ = (
        ("get_time_usec", retro_perf_get_time_usec_t),
        ("get_cpu_features", retro_get_cpu_features_t),
        ("get_perf_counter", retro_perf_get_counter_t),
        ("perf_register", retro_perf_register_t),
        ("perf_start", retro_perf_start_t),
        ("perf_stop", retro_perf_stop_t),
        ("perf_log", retro_perf_log_t),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_perf_callback
        >>> copy.deepcopy(retro_perf_callback()).get_time_usec is None
        True
        """
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
