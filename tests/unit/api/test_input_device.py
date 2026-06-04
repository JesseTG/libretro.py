"""Unit tests for :mod:`libretro.api.input.device`."""

from __future__ import annotations

import copy
from collections.abc import Sequence

import pytest

from libretro.api import (
    InputDevice,
    InputDeviceFlag,
    retro_controller_description,
    retro_controller_info,
    retro_input_descriptor,
)
from libretro.api.input.device import RETRO_DEVICE_SUBCLASS


def test_input_device_subclass_helper() -> None:
    # subclass id format: ((sub + 1) << 8) | base
    expected = (3 << 8) | InputDevice.JOYPAD.value
    assert RETRO_DEVICE_SUBCLASS(InputDevice.JOYPAD.value, 2) == expected


def test_input_device_to_flag() -> None:
    assert InputDevice.JOYPAD.flag == InputDeviceFlag.JOYPAD
    assert InputDevice.MOUSE.flag == InputDeviceFlag.MOUSE


def test_input_device_flag_all_covers_known_devices() -> None:
    for flag in (
        InputDeviceFlag.JOYPAD,
        InputDeviceFlag.MOUSE,
        InputDeviceFlag.KEYBOARD,
        InputDeviceFlag.LIGHTGUN,
        InputDeviceFlag.ANALOG,
        InputDeviceFlag.POINTER,
    ):
        assert flag in InputDeviceFlag.ALL


def test_retro_input_descriptor_kwarg_init() -> None:
    desc = retro_input_descriptor(
        port=0, device=InputDevice.JOYPAD.value, index=0, id=5, description=b"Button A"
    )
    assert desc.port == 0
    assert desc.device == InputDevice.JOYPAD.value
    assert desc.index == 0
    assert desc.id == 5
    assert desc.description == b"Button A"


def test_retro_input_descriptor_deepcopy() -> None:
    desc = retro_input_descriptor(port=1, description=b"L2")
    dup = copy.deepcopy(desc)
    assert dup is not desc
    assert dup.port == desc.port
    assert dup.description == desc.description


def test_retro_controller_description_kwarg_init() -> None:
    d = retro_controller_description(desc=b"Game Pad", id=5)
    assert d.desc == b"Game Pad"
    assert d.id == 5


def test_retro_controller_description_deepcopy() -> None:
    d = retro_controller_description(b"Analog", 2)
    dup = copy.deepcopy(d)
    assert dup is not d
    assert dup.desc == d.desc
    assert dup.id == d.id


def test_retro_controller_info_sequence_protocol() -> None:
    info = retro_controller_info()
    assert isinstance(info, Sequence)


def test_retro_controller_info_indexing_no_types_raises() -> None:
    info = retro_controller_info()
    with pytest.raises(ValueError):
        info[0]


def test_retro_controller_info_index_out_of_range() -> None:
    descs = (retro_controller_description * 1)(retro_controller_description(b"x", 0))
    info = retro_controller_info(descs, 1)
    with pytest.raises(IndexError):
        info[5]


def test_retro_controller_info_deepcopy_preserves_entries() -> None:
    descs = (retro_controller_description * 1)(retro_controller_description(b"Pad", 1))
    info = retro_controller_info(descs, 1)
    dup = copy.deepcopy(info)
    assert dup is not info
    assert len(dup) == 1
    assert dup[0].desc == b"Pad"
