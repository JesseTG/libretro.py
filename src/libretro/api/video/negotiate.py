from ctypes import Structure, c_int, c_uint
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints

retro_hw_render_context_negotiation_interface_type = c_int
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN = 0
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_DUMMY = 0x7FFFFFFF


class ContextNegotiationInterfaceType(IntEnum):
    VULKAN = RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN


class retro_hw_render_context_negotiation_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_context_negotiation_interface_type
    interface_version: c_uint


__all__ = [
    "ContextNegotiationInterfaceType",
    "retro_hw_render_context_negotiation_interface",
    "retro_hw_render_context_negotiation_interface_type",
]
