"""Unit tests for :mod:`libretro.api.led`."""

from __future__ import annotations

import copy

from libretro.api import retro_led_interface


def test_retro_led_interface_default() -> None:
    iface = retro_led_interface()
    assert not iface.set_led_state


def test_retro_led_interface_deepcopy() -> None:
    iface = retro_led_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.set_led_state
