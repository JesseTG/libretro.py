from ctypes import Structure, c_uint
from enum import IntEnum

from ...._utils import FieldsFromTypeHints
from ....h import *


class HardwareRenderInterfaceType(IntEnum):
    VULKAN = RETRO_HW_RENDER_INTERFACE_VULKAN,
    D3D9 = RETRO_HW_RENDER_INTERFACE_D3D9,
    D3D10 = RETRO_HW_RENDER_INTERFACE_D3D10,
    D3D11 = RETRO_HW_RENDER_INTERFACE_D3D11,
    D3D12 = RETRO_HW_RENDER_INTERFACE_D3D12,
    GSKIT_PS2 = RETRO_HW_RENDER_INTERFACE_GSKIT_PS2,

    def __init__(self, value):
        self._type_ = 'I'


class retro_hw_render_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_interface_type
    interface_version: c_uint


__all__ = [
    'HardwareRenderInterfaceType',
    'retro_hw_render_interface',
]
