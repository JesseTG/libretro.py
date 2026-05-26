"""Unit tests for :mod:`libretro.api.camera`."""

from __future__ import annotations

import copy

from libretro.api import (
    CameraCapabilities,
    CameraCapabilityFlags,
    retro_camera_callback,
)


def test_retro_camera_callback_kwarg_init() -> None:
    cb = retro_camera_callback(caps=CameraCapabilityFlags.RAW_FRAMEBUFFER, width=640, height=480)
    assert cb.caps == CameraCapabilityFlags.RAW_FRAMEBUFFER
    assert cb.width == 640
    assert cb.height == 480
    assert not cb.start
    assert not cb.stop


def test_retro_camera_callback_default_fields_are_zero_or_null() -> None:
    cb = retro_camera_callback()
    assert cb.caps == 0
    assert cb.width == 0
    assert cb.height == 0
    assert not cb.start
    assert not cb.stop
    assert not cb.frame_raw_framebuffer
    assert not cb.frame_opengl_texture
    assert not cb.initialized
    assert not cb.deinitialized


def test_retro_camera_callback_deepcopy() -> None:
    cb = retro_camera_callback(caps=1, width=640, height=480)
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert dup.caps == cb.caps
    assert dup.width == cb.width
    assert dup.height == cb.height


def test_camera_capabilities_flag_method() -> None:
    assert CameraCapabilities.OPENGL_TEXTURE.flag() == 1
    assert CameraCapabilities.RAW_FRAMEBUFFER.flag() == 2


def test_camera_capability_flags_combine() -> None:
    both = CameraCapabilityFlags.RAW_FRAMEBUFFER | CameraCapabilityFlags.OPENGL_TEXTURE
    assert CameraCapabilityFlags.RAW_FRAMEBUFFER in both
    assert CameraCapabilityFlags.OPENGL_TEXTURE in both
    assert int(both) == 3
