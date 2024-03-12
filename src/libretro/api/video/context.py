from ctypes import CFUNCTYPE, c_bool, c_uint, Structure

from ...api.proc import retro_proc_address_t
from ...h import retro_hw_context_type
from ..._utils import FieldsFromTypeHints, String, UNCHECKED, c_uintptr


retro_hw_context_reset_t = CFUNCTYPE(None, )
retro_hw_get_current_framebuffer_t = CFUNCTYPE(c_uintptr, )
retro_hw_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)


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
