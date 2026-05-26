"""Unit tests for :mod:`libretro.api.location`."""

from __future__ import annotations

import copy

from libretro.api import retro_location_callback


def test_retro_location_callback_defaults_all_null() -> None:
    cb = retro_location_callback()
    assert not cb.start
    assert not cb.stop
    assert not cb.get_position
    assert not cb.set_interval
    assert not cb.initialized
    assert not cb.deinitialized


def test_retro_location_callback_deepcopy() -> None:
    cb = retro_location_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.start
