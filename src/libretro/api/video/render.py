"""Hardware rendering interface and screen rotation types.

Corresponds to :c:type:`retro_hw_render_interface` and the rotation constants
in ``libretro.h``.
"""

from ctypes import Structure, c_int, c_uint
from dataclasses import dataclass
from enum import IntEnum

retro_hw_render_interface_type = c_int
RETRO_HW_RENDER_INTERFACE_VULKAN = 0
RETRO_HW_RENDER_INTERFACE_D3D9 = 1
RETRO_HW_RENDER_INTERFACE_D3D10 = 2
RETRO_HW_RENDER_INTERFACE_D3D11 = 3
RETRO_HW_RENDER_INTERFACE_D3D12 = 4
RETRO_HW_RENDER_INTERFACE_GSKIT_PS2 = 5
RETRO_HW_RENDER_INTERFACE_DUMMY = 0x7FFFFFFF


class Rotation(IntEnum):
    """Screen rotation angle.

    >>> from libretro.api.video import Rotation
    >>> Rotation.NONE
    <Rotation.NONE: 0>
    """

    NONE = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3


class HardwareRenderInterfaceType(IntEnum):
    """Type of hardware rendering interface.

    Corresponds to :c:type:`retro_hw_render_interface_type` in ``libretro.h``.
    """

    VULKAN = RETRO_HW_RENDER_INTERFACE_VULKAN
    D3D9 = RETRO_HW_RENDER_INTERFACE_D3D9
    D3D10 = RETRO_HW_RENDER_INTERFACE_D3D10
    D3D11 = RETRO_HW_RENDER_INTERFACE_D3D11
    D3D12 = RETRO_HW_RENDER_INTERFACE_D3D12
    GSKIT_PS2 = RETRO_HW_RENDER_INTERFACE_GSKIT_PS2


@dataclass(init=False, slots=True)
class retro_hw_render_interface(Structure):
    """Corresponds to :c:type:`retro_hw_render_interface` in ``libretro.h``.

    Base type for hardware-specific render interfaces.

    >>> from libretro.api.video import retro_hw_render_interface
    >>> iface = retro_hw_render_interface()
    >>> iface.interface_version
    0
    """

    interface_type: HardwareRenderInterfaceType
    """Rendering API this interface is for."""
    interface_version: int
    """Version of this rendering interface."""

    _fields_ = (
        ("interface_type", retro_hw_render_interface_type),
        ("interface_version", c_uint),
    )


__all__ = [
    "HardwareRenderInterfaceType",
    "retro_hw_render_interface",
    "retro_hw_render_interface_type",
    "Rotation",
]
