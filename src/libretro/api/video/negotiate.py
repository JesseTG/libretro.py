"""Hardware rendering context negotiation types.

Corresponds to :c:type:`retro_hw_render_context_negotiation_interface`
in ``libretro.h``.
"""

from ctypes import Structure, c_int, c_uint
from dataclasses import dataclass
from enum import IntEnum

retro_hw_render_context_negotiation_interface_type = c_int
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN = 0
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_DUMMY = 0x7FFFFFFF


class ContextNegotiationInterfaceType(IntEnum):
    """Type of context negotiation interface.

    Corresponds to the ``RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_*``
    constants in ``libretro.h``.
    """

    VULKAN = RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN


@dataclass(init=False, slots=True)
class retro_hw_render_context_negotiation_interface(Structure):
    """Corresponds to :c:type:`retro_hw_render_context_negotiation_interface`
    in ``libretro.h``.

    >>> from libretro.api.video import retro_hw_render_context_negotiation_interface
    >>> iface = retro_hw_render_context_negotiation_interface()
    >>> iface.interface_version
    0
    """

    interface_type: ContextNegotiationInterfaceType
    """Rendering API this negotiation interface is for."""
    interface_version: int
    """Version of this negotiation interface."""

    _fields_ = (
        ("interface_type", retro_hw_render_context_negotiation_interface_type),
        ("interface_version", c_uint),
    )


__all__ = [
    "ContextNegotiationInterfaceType",
    "retro_hw_render_context_negotiation_interface",
    "retro_hw_render_context_negotiation_interface_type",
]
