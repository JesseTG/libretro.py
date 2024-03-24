from ctypes import Structure, c_uint
from enum import IntEnum

from ...._utils import FieldsFromTypeHints
from ....h import *


class ContextNegotiationInterfaceType(IntEnum):
    VULKAN = RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN


class retro_hw_render_context_negotiation_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_context_negotiation_interface_type
    interface_version: c_uint


__all__ = [
    "ContextNegotiationInterfaceType",
    "retro_hw_render_context_negotiation_interface",
]
