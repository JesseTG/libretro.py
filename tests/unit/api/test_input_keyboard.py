"""Unit tests for :mod:`libretro.api.input.keyboard`."""

from __future__ import annotations

import copy

import pytest

from libretro.api import Key, KeyModifier, retro_keyboard_callback


def test_retro_keyboard_callback_default() -> None:
    cb = retro_keyboard_callback()
    assert not cb.callback


def test_retro_keyboard_callback_deepcopy() -> None:
    cb = retro_keyboard_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.callback


def test_retro_keyboard_callback_call_noop_when_unset() -> None:
    cb = retro_keyboard_callback()
    # __call__ is a no-op when callback is None, regardless of character form
    cb(True, Key.A, "a", KeyModifier.NONE)
    cb(True, Key.SPACE, ord(" "), KeyModifier.SHIFT)
    cb(True, Key.SPACE, b" ", KeyModifier.NONE)


def test_retro_keyboard_callback_rejects_invalid_character() -> None:
    cb = retro_keyboard_callback()
    with pytest.raises(ValueError):
        cb(True, Key.A, "ab", KeyModifier.NONE)
