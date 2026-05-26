"""Unit tests for :mod:`libretro.api.disk`."""

from __future__ import annotations

import copy

from libretro.api import retro_disk_control_callback, retro_disk_control_ext_callback


def test_retro_disk_control_callback_defaults_all_null() -> None:
    cb = retro_disk_control_callback()
    assert not cb.set_eject_state
    assert not cb.get_eject_state
    assert not cb.get_image_index
    assert not cb.set_image_index
    assert not cb.get_num_images
    assert not cb.replace_image_index
    assert not cb.add_image_index


def test_retro_disk_control_callback_deepcopy() -> None:
    cb = retro_disk_control_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.set_eject_state


def test_retro_disk_control_ext_callback_has_ext_fields() -> None:
    cb = retro_disk_control_ext_callback()
    assert not cb.set_initial_image
    assert not cb.get_image_path
    assert not cb.get_image_label


def test_retro_disk_control_ext_callback_is_subclass_of_base() -> None:
    cb = retro_disk_control_ext_callback()
    assert isinstance(cb, retro_disk_control_callback)


def test_retro_disk_control_ext_callback_deepcopy() -> None:
    cb = retro_disk_control_ext_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.set_initial_image
