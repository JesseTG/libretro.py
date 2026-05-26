"""Unit tests for :mod:`libretro.api.timing`."""

# pyright: reportUnknownMemberType=false

from __future__ import annotations

import copy

import pytest

from libretro.api import (
    ThrottleMode,
    retro_fastforwarding_override,
    retro_frame_time_callback,
    retro_throttle_state,
)


def test_retro_frame_time_callback_default() -> None:
    cb = retro_frame_time_callback()
    assert not cb.callback
    assert cb.reference == 0


def test_retro_frame_time_callback_kwarg_init() -> None:
    cb = retro_frame_time_callback(reference=16667)
    assert cb.reference == 16667
    assert not cb.callback


def test_retro_frame_time_callback_deepcopy() -> None:
    cb = retro_frame_time_callback(reference=16667)
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert dup.reference == cb.reference


def test_retro_frame_time_callback_call_when_unset_is_noop() -> None:
    cb = retro_frame_time_callback()
    cb()  # no-op


def test_retro_fastforwarding_override_kwarg_init() -> None:
    ff = retro_fastforwarding_override(
        ratio=4.0, fastforward=True, notification=False, inhibit_toggle=True
    )
    assert ff.ratio == pytest.approx(4.0)
    assert ff.fastforward is True
    assert ff.notification is False
    assert ff.inhibit_toggle is True


def test_retro_fastforwarding_override_defaults() -> None:
    ff = retro_fastforwarding_override()
    assert ff.ratio == 0.0
    assert ff.fastforward is False
    assert ff.notification is False
    assert ff.inhibit_toggle is False


def test_retro_fastforwarding_override_deepcopy() -> None:
    ff = retro_fastforwarding_override(ratio=2.0, fastforward=True)
    dup = copy.deepcopy(ff)
    assert dup is not ff
    assert dup.ratio == ff.ratio
    assert dup.fastforward == ff.fastforward


def test_retro_throttle_state_kwarg_init() -> None:
    ts = retro_throttle_state(mode=ThrottleMode.FAST_FORWARD, rate=2.5)
    assert ts.mode == ThrottleMode.FAST_FORWARD
    assert ts.rate == pytest.approx(2.5)


def test_retro_throttle_state_default() -> None:
    ts = retro_throttle_state()
    assert ts.mode == ThrottleMode.NONE
    assert ts.rate == 0.0


def test_retro_throttle_state_deepcopy() -> None:
    ts = retro_throttle_state(mode=ThrottleMode.SLOW_MOTION, rate=0.5)
    dup = copy.deepcopy(ts)
    assert dup is not ts
    assert dup.mode == ts.mode
    assert dup.rate == ts.rate


def test_throttle_mode_enum_values() -> None:
    assert ThrottleMode.NONE.value == 0
    assert ThrottleMode.FRAME_STEPPING.value == 1
    assert ThrottleMode.FAST_FORWARD.value == 2
    assert ThrottleMode.SLOW_MOTION.value == 3
    assert ThrottleMode.REWINDING.value == 4
    assert ThrottleMode.VSYNC.value == 5
    assert ThrottleMode.UNBLOCKED.value == 6
