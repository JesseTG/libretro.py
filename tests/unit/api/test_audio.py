"""Unit tests for :mod:`libretro.api.audio`."""

from __future__ import annotations

import copy
from ctypes import addressof

from libretro.api import retro_audio_buffer_status_callback, retro_audio_callback


def test_retro_audio_callback_default_fields_are_none() -> None:
    cb = retro_audio_callback()
    assert not cb.callback
    assert not cb.set_state


def test_retro_audio_callback_deepcopy() -> None:
    cb = retro_audio_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert addressof(cb) != addressof(dup)
    assert not dup.callback
    assert not dup.set_state


def test_retro_audio_buffer_status_callback_default() -> None:
    cb = retro_audio_buffer_status_callback()
    assert not cb.callback


def test_retro_audio_buffer_status_callback_noop_when_unset() -> None:
    cb = retro_audio_buffer_status_callback()
    # __call__ with no callback set should be a no-op (no exception)
    cb(True, 50, False)


def test_retro_audio_buffer_status_callback_deepcopy() -> None:
    cb = retro_audio_buffer_status_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert addressof(cb) != addressof(dup)
    assert not dup.callback
