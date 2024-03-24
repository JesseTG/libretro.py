from dataclasses import dataclass
from enum import IntEnum
from ctypes import Structure, c_bool, c_uint, CFUNCTYPE, c_char_p

from ...proc import retro_proc_address_t
from ...._utils import c_uintptr, FieldsFromTypeHints
from ....h import *


class HardwareContext(IntEnum):
    NONE = RETRO_HW_CONTEXT_NONE
    OPENGL = RETRO_HW_CONTEXT_OPENGL
    OENGLES2 = RETRO_HW_CONTEXT_OPENGLES2
    OPENGL_CORE = RETRO_HW_CONTEXT_OPENGL_CORE
    OPENGLES3 = RETRO_HW_CONTEXT_OPENGLES3
    OPENGLES_VERSION = RETRO_HW_CONTEXT_OPENGLES_VERSION
    VULKAN = RETRO_HW_CONTEXT_VULKAN
    DIRECT3D = 7
    D3D11 = RETRO_HW_CONTEXT_D3D11
    D3D10 = RETRO_HW_CONTEXT_D3D10
    D3D12 = RETRO_HW_CONTEXT_D3D12

    def __init__(self, value):
        self._type_ = 'I'


retro_hw_context_reset_t = CFUNCTYPE(None)
retro_hw_get_current_framebuffer_t = CFUNCTYPE(c_uintptr)
retro_hw_get_proc_address_t = CFUNCTYPE(retro_proc_address_t, c_char_p)


@dataclass(init=False)
class retro_hw_render_callback(Structure, metaclass=FieldsFromTypeHints):
    context_type: retro_hw_context_type
    context_reset: retro_hw_context_reset_t
    get_current_framebuffer: retro_hw_get_current_framebuffer_t
    get_proc_address: retro_hw_get_proc_address_t
    depth: c_bool
    stencil: c_bool
    bottom_left_origin: c_bool
    version_major: c_uint
    version_minor: c_uint
    cache_context: c_bool
    context_destroy: retro_hw_context_reset_t
    debug_context: c_bool


__all__ = [
    'HardwareContext',
    'retro_hw_context_reset_t',
    'retro_hw_get_current_framebuffer_t',
    'retro_hw_get_proc_address_t',
    'retro_hw_render_callback',
]
