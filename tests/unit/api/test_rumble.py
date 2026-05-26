"""Unit tests for :mod:`libretro.api.rumble`."""

from __future__ import annotations

import copy

from libretro.api import RumbleEffect, retro_rumble_interface


def test_retro_rumble_interface_default() -> None:
    iface = retro_rumble_interface()
    assert not iface.set_rumble_state


def test_retro_rumble_interface_deepcopy() -> None:
    iface = retro_rumble_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.set_rumble_state


def test_rumble_effect_enum_values() -> None:
    assert RumbleEffect.STRONG.value == 0
    assert RumbleEffect.WEAK.value == 1
