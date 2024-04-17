from ctypes import Structure, c_int, c_uint
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints

retro_hw_render_interface_type = c_int
RETRO_HW_RENDER_INTERFACE_VULKAN = 0
RETRO_HW_RENDER_INTERFACE_D3D9 = 1
RETRO_HW_RENDER_INTERFACE_D3D10 = 2
RETRO_HW_RENDER_INTERFACE_D3D11 = 3
RETRO_HW_RENDER_INTERFACE_D3D12 = 4
RETRO_HW_RENDER_INTERFACE_GSKIT_PS2 = 5
RETRO_HW_RENDER_INTERFACE_DUMMY = 0x7FFFFFFF


class Rotation(IntEnum):
    NONE = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3

    def __init__(self, value):
        self._type_ = "I"


class HardwareRenderInterfaceType(IntEnum):
    VULKAN = RETRO_HW_RENDER_INTERFACE_VULKAN
    D3D9 = RETRO_HW_RENDER_INTERFACE_D3D9
    D3D10 = RETRO_HW_RENDER_INTERFACE_D3D10
    D3D11 = RETRO_HW_RENDER_INTERFACE_D3D11
    D3D12 = RETRO_HW_RENDER_INTERFACE_D3D12
    GSKIT_PS2 = RETRO_HW_RENDER_INTERFACE_GSKIT_PS2

    def __init__(self, value):
        self._type_ = "I"


class retro_hw_render_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_interface_type
    interface_version: c_uint


__all__ = [
    "HardwareRenderInterfaceType",
    "retro_hw_render_interface",
    "retro_hw_render_interface_type",
    "Rotation",
]
