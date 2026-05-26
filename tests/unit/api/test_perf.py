"""Unit tests for :mod:`libretro.api.perf`."""

from __future__ import annotations

import copy

from libretro.api import CpuFeatures, retro_perf_callback, retro_perf_counter


def test_retro_perf_counter_kwarg_init() -> None:
    c = retro_perf_counter(ident=b"hot_loop", start=100, total=1000, call_cnt=42, registered=True)
    assert c.ident == b"hot_loop"
    assert c.start == 100
    assert c.total == 1000
    assert c.call_cnt == 42
    assert c.registered is True


def test_retro_perf_counter_defaults() -> None:
    c = retro_perf_counter()
    assert c.ident is None
    assert c.start == 0
    assert c.total == 0
    assert c.call_cnt == 0
    assert c.registered is False


def test_retro_perf_counter_deepcopy() -> None:
    c = retro_perf_counter(ident=b"x", start=1, total=2, call_cnt=3, registered=True)
    dup = copy.deepcopy(c)
    assert dup is not c
    assert dup.ident == c.ident
    assert dup.total == c.total
    assert dup.registered == c.registered


def test_retro_perf_callback_defaults_all_null() -> None:
    cb = retro_perf_callback()
    assert not cb.get_time_usec
    assert not cb.get_cpu_features
    assert not cb.get_perf_counter
    assert not cb.perf_register
    assert not cb.perf_start
    assert not cb.perf_stop
    assert not cb.perf_log


def test_retro_perf_callback_deepcopy() -> None:
    cb = retro_perf_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.get_time_usec


def test_cpu_features_combine() -> None:
    flags = CpuFeatures.SSE | CpuFeatures.SSE2 | CpuFeatures.AVX
    assert CpuFeatures.SSE in flags
    assert CpuFeatures.SSE2 in flags
    assert CpuFeatures.AVX in flags
    assert CpuFeatures.NEON not in flags
