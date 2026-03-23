from ctypes import Structure, c_int, c_uint
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

retro_hw_render_context_negotiation_interface_type = c_int
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN = 0
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_DUMMY = 0x7FFFFFFF


class ContextNegotiationInterfaceType(IntEnum):
    VULKAN = RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN


@dataclass(init=False)
class retro_hw_render_context_negotiation_interface(Structure):
    if TYPE_CHECKING:
        interface_type: ContextNegotiationInterfaceType
        interface_version: int

    _fields_ = [
        ("interface_type", retro_hw_render_context_negotiation_interface_type),
        ("interface_version", c_uint),
    ]


__all__ = [
    "ContextNegotiationInterfaceType",
    "retro_hw_render_context_negotiation_interface",
    "retro_hw_render_context_negotiation_interface_type",
]
