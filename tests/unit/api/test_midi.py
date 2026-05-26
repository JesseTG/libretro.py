"""Unit tests for :mod:`libretro.api.midi`."""

from __future__ import annotations

import copy

from libretro.api import retro_midi_interface


def test_retro_midi_interface_defaults_all_none() -> None:
    iface = retro_midi_interface()
    assert not iface.input_enabled
    assert not iface.output_enabled
    assert not iface.read
    assert not iface.write
    assert not iface.flush


def test_retro_midi_interface_deepcopy() -> None:
    iface = retro_midi_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.read
