# These tests intentionally call the composite driver's protected env handlers;
# the TypedPointer casts are runtime-equivalent to the handlers' annotations.
# pyright: reportPrivateUsage=false, reportArgumentType=false

from ctypes import POINTER, cast, pointer

import pytest

from libretro.api.video import (
    ContextNegotiationInterfaceType,
    HardwareContext,
    retro_hw_render_context_negotiation_interface,
    retro_hw_render_context_negotiation_interface_vulkan,
)
from libretro.drivers.audio import ArrayAudioDriver
from libretro.drivers.environment.composite import CompositeEnvironmentDriver
from libretro.drivers.input import IterableInputDriver
from libretro.drivers.video import ArrayVideoDriver, MultiVideoDriver, VideoDriver


def _vulkan_negotiation_iface() -> retro_hw_render_context_negotiation_interface_vulkan:
    return retro_hw_render_context_negotiation_interface_vulkan(
        interface_type=ContextNegotiationInterfaceType.VULKAN,
        interface_version=2,
    )


def _composite(video: VideoDriver) -> CompositeEnvironmentDriver:
    return CompositeEnvironmentDriver(
        audio=ArrayAudioDriver(),
        input=IterableInputDriver(),
        video=video,
    )


def test_software_driver_rejects_negotiation_interface():
    driver = ArrayVideoDriver()
    assert driver.context_negotiation_interface is None

    with pytest.raises(NotImplementedError):
        driver.context_negotiation_interface = _vulkan_negotiation_iface()


def test_composite_returns_false_when_driver_rejects():
    env = _composite(ArrayVideoDriver())
    iface = _vulkan_negotiation_iface()
    ptr = cast(pointer(iface), POINTER(retro_hw_render_context_negotiation_interface))

    assert env._set_hw_render_context_negotiation_interface(ptr) is False


def test_multi_driver_stores_negotiation_interface():
    driver = MultiVideoDriver({HardwareContext.NONE: ArrayVideoDriver})
    iface = _vulkan_negotiation_iface()

    driver.context_negotiation_interface = iface
    assert driver.context_negotiation_interface is iface


def test_composite_accepts_interface_with_multi_driver():
    env = _composite(MultiVideoDriver({HardwareContext.NONE: ArrayVideoDriver}))
    iface = _vulkan_negotiation_iface()
    ptr = cast(pointer(iface), POINTER(retro_hw_render_context_negotiation_interface))

    assert env._set_hw_render_context_negotiation_interface(ptr) is True
    stored = env._video.context_negotiation_interface
    assert stored is not None
    assert stored.interface_type == ContextNegotiationInterfaceType.VULKAN
    assert stored.interface_version == 2


def test_negotiation_support_reports_version_for_vulkan_capable_driver():
    # A driver map claiming Vulkan support is enough for the env call
    driver = MultiVideoDriver(
        {HardwareContext.NONE: ArrayVideoDriver, HardwareContext.VULKAN: ArrayVideoDriver}
    )
    env = _composite(driver)
    query = retro_hw_render_context_negotiation_interface(
        interface_type=ContextNegotiationInterfaceType.VULKAN,
        interface_version=0,
    )
    ptr = cast(pointer(query), POINTER(retro_hw_render_context_negotiation_interface))

    assert env._get_hw_render_context_negotiation_interface_support(ptr) is True
    assert query.interface_version == 2


def test_vulkan_driver_registered_when_available():
    pytest.importorskip("vulkan", reason="the libretro.py[vulkan] extra is not installed")
    from libretro.drivers.video import DEFAULT_DRIVER_MAP
    from libretro.drivers.video.vulkan import VulkanVideoDriver

    assert HardwareContext.VULKAN in DEFAULT_DRIVER_MAP
    assert DEFAULT_DRIVER_MAP[HardwareContext.VULKAN] is VulkanVideoDriver


def test_negotiation_support_false_without_vulkan_driver():
    env = _composite(MultiVideoDriver({HardwareContext.NONE: ArrayVideoDriver}))
    query = retro_hw_render_context_negotiation_interface(
        interface_type=ContextNegotiationInterfaceType.VULKAN,
        interface_version=0,
    )
    ptr = cast(pointer(query), POINTER(retro_hw_render_context_negotiation_interface))

    assert env._get_hw_render_context_negotiation_interface_support(ptr) is False
