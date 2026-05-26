"""Unit tests for :mod:`libretro.api.video` (frame, context, render, negotiate)."""

from __future__ import annotations

import copy

import pytest

from libretro.api.video import (
    ContextNegotiationInterfaceType,
    HardwareContext,
    HardwareRenderInterfaceType,
    MemoryAccess,
    MemoryType,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_render_callback,
    retro_hw_render_context_negotiation_interface,
    retro_hw_render_interface,
)


def test_retro_framebuffer_default() -> None:
    fb = retro_framebuffer()
    assert not fb.data
    assert fb.width == 0
    assert fb.height == 0
    assert fb.pitch == 0


def test_retro_framebuffer_kwarg_init() -> None:
    fb = retro_framebuffer(width=320, height=240, pitch=1280, format=PixelFormat.XRGB8888)
    assert fb.width == 320
    assert fb.height == 240
    assert fb.pitch == 1280
    assert fb.format == PixelFormat.XRGB8888


def test_retro_framebuffer_deepcopy_with_no_data() -> None:
    fb = retro_framebuffer(width=64, height=64, pitch=256, format=PixelFormat.XRGB8888)
    dup = copy.deepcopy(fb)
    assert dup is not fb
    assert dup.width == fb.width
    assert dup.height == fb.height
    assert dup.pitch == fb.pitch


@pytest.mark.parametrize(
    ("fmt", "bpp"),
    [
        (PixelFormat.RGB1555, 2),
        (PixelFormat.XRGB8888, 4),
        (PixelFormat.RGB565, 2),
    ],
)
def test_pixel_format_bytes_per_pixel(fmt: PixelFormat, bpp: int) -> None:
    assert fmt.bytes_per_pixel == bpp


@pytest.mark.parametrize(
    ("fmt", "typecode"),
    [
        (PixelFormat.RGB1555, "H"),
        (PixelFormat.XRGB8888, "L"),
        (PixelFormat.RGB565, "H"),
    ],
)
def test_pixel_format_typecode(fmt: PixelFormat, typecode: str) -> None:
    assert fmt.pixel_typecode == typecode


def test_memory_access_flags_combine() -> None:
    rw = MemoryAccess.READ | MemoryAccess.WRITE
    assert MemoryAccess.READ in rw
    assert MemoryAccess.WRITE in rw


def test_memory_type_cached_flag() -> None:
    assert MemoryType.CACHED.value == 1
    assert MemoryType.NONE.value == 0


def test_retro_hw_render_callback_default_is_no_context() -> None:
    cb = retro_hw_render_callback()
    assert cb.context_type == HardwareContext.NONE
    assert cb.depth is False
    assert cb.stencil is False
    assert cb.version_major == 0
    assert cb.version_minor == 0


def test_retro_hw_render_callback_kwarg_init() -> None:
    cb = retro_hw_render_callback(
        context_type=HardwareContext.OPENGL_CORE,
        depth=True,
        stencil=True,
        version_major=4,
        version_minor=3,
        debug_context=True,
    )
    assert cb.context_type == HardwareContext.OPENGL_CORE
    assert cb.depth is True
    assert cb.stencil is True
    assert cb.version_major == 4
    assert cb.version_minor == 3
    assert cb.debug_context is True


def test_retro_hw_render_callback_deepcopy() -> None:
    cb = retro_hw_render_callback(context_type=HardwareContext.OPENGL, version_major=2)
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert dup.context_type == cb.context_type
    assert dup.version_major == cb.version_major


def test_retro_hw_render_interface_default() -> None:
    iface = retro_hw_render_interface()
    assert iface.interface_version == 0


def test_retro_hw_render_context_negotiation_interface_default() -> None:
    iface = retro_hw_render_context_negotiation_interface()
    assert iface.interface_version == 0


@pytest.mark.parametrize(
    ("rot", "value"),
    [
        (Rotation.NONE, 0),
        (Rotation.NINETY, 1),
        (Rotation.ONE_EIGHTY, 2),
        (Rotation.TWO_SEVENTY, 3),
    ],
)
def test_rotation_enum_values(rot: Rotation, value: int) -> None:
    assert rot.value == value


def test_hardware_context_enum_includes_known_apis() -> None:
    assert HardwareContext.NONE.value == 0
    assert HardwareContext.OPENGL.value == 1
    assert HardwareContext.OPENGLES2.value == 2
    assert HardwareContext.OPENGL_CORE.value == 3
    assert HardwareContext.VULKAN.value == 6


def test_hardware_render_interface_type_enum() -> None:
    assert HardwareRenderInterfaceType.VULKAN.value == 0


def test_context_negotiation_interface_type_enum() -> None:
    assert ContextNegotiationInterfaceType.VULKAN.value == 0
