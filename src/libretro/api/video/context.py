from ctypes import Structure, c_bool, c_int, c_uint, c_void_p, cast
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import c_uintptr
from libretro.ctypes import CStringArg, TypedFunctionPointer, c_void_ptr

RETRO_HW_FRAME_BUFFER_VALID = cast((-1), c_void_p)

retro_hw_context_type = c_int
RETRO_HW_CONTEXT_NONE = 0
RETRO_HW_CONTEXT_OPENGL = 1
RETRO_HW_CONTEXT_OPENGLES2 = 2
RETRO_HW_CONTEXT_OPENGL_CORE = 3
RETRO_HW_CONTEXT_OPENGLES3 = 4
RETRO_HW_CONTEXT_OPENGLES_VERSION = 5
RETRO_HW_CONTEXT_VULKAN = 6
RETRO_HW_CONTEXT_D3D11 = 7
RETRO_HW_CONTEXT_D3D10 = 8
RETRO_HW_CONTEXT_D3D12 = 9
RETRO_HW_CONTEXT_D3D9 = 10
RETRO_HW_CONTEXT_DUMMY = 0x7FFFFFFF

HW_FRAME_BUFFER_VALID = RETRO_HW_FRAME_BUFFER_VALID


class HardwareContext(IntEnum):
    NONE = RETRO_HW_CONTEXT_NONE
    OPENGL = RETRO_HW_CONTEXT_OPENGL
    OPENGLES2 = RETRO_HW_CONTEXT_OPENGLES2
    OPENGL_CORE = RETRO_HW_CONTEXT_OPENGL_CORE
    OPENGLES3 = RETRO_HW_CONTEXT_OPENGLES3
    OPENGLES_VERSION = RETRO_HW_CONTEXT_OPENGLES_VERSION
    VULKAN = RETRO_HW_CONTEXT_VULKAN
    DIRECT3D = 7
    D3D11 = RETRO_HW_CONTEXT_D3D11
    D3D10 = RETRO_HW_CONTEXT_D3D10
    D3D12 = RETRO_HW_CONTEXT_D3D12
    D3D9 = RETRO_HW_CONTEXT_D3D9


retro_hw_context_reset_t = TypedFunctionPointer[None, []]
retro_hw_get_current_framebuffer_t = TypedFunctionPointer[c_uintptr, []]
retro_hw_get_proc_address_t = TypedFunctionPointer[c_void_ptr, [CStringArg]]
# Workaround for ctypes not allowing callbacks to return function pointers


@dataclass(init=False, slots=True)
class retro_hw_render_callback(Structure):
    context_type: HardwareContext
    context_reset: retro_hw_context_reset_t | None
    get_current_framebuffer: retro_hw_get_current_framebuffer_t | None
    get_proc_address: retro_hw_get_proc_address_t | None
    depth: bool
    stencil: bool
    bottom_left_origin: bool
    version_major: int
    version_minor: int
    cache_context: bool
    context_destroy: retro_hw_context_reset_t | None
    debug_context: bool

    _fields_ = (
        ("context_type", retro_hw_context_type),
        ("context_reset", retro_hw_context_reset_t),
        ("get_current_framebuffer", retro_hw_get_current_framebuffer_t),
        ("get_proc_address", retro_hw_get_proc_address_t),
        ("depth", c_bool),
        ("stencil", c_bool),
        ("bottom_left_origin", c_bool),
        ("version_major", c_uint),
        ("version_minor", c_uint),
        ("cache_context", c_bool),
        ("context_destroy", retro_hw_context_reset_t),
        ("debug_context", c_bool),
    )

    def __init__(
        self,
        context_type: HardwareContext = HardwareContext.NONE,
        context_reset: retro_hw_context_reset_t | None = None,
        get_current_framebuffer: retro_hw_get_current_framebuffer_t | None = None,
        get_proc_address: retro_hw_get_proc_address_t | None = None,
        depth: bool = False,
        stencil: bool = False,
        bottom_left_origin: bool = False,
        version_major: int = 0,
        version_minor: int = 0,
        cache_context: bool = False,
        context_destroy: retro_hw_context_reset_t | None = None,
        debug_context: bool = False,
    ):
        super().__init__(
            context_type=context_type,
            context_reset=context_reset or retro_hw_context_reset_t(),
            get_current_framebuffer=get_current_framebuffer
            or retro_hw_get_current_framebuffer_t(),
            get_proc_address=get_proc_address or retro_hw_get_proc_address_t(),
            depth=depth,
            stencil=stencil,
            bottom_left_origin=bottom_left_origin,
            version_major=version_major,
            version_minor=version_minor,
            cache_context=cache_context,
            context_destroy=context_destroy or retro_hw_context_reset_t(),
            debug_context=debug_context,
        )

    def __deepcopy__(self, _):
        return retro_hw_render_callback(
            self.context_type,
            self.context_reset,
            self.get_current_framebuffer,
            self.get_proc_address,
            self.depth,
            self.stencil,
            self.bottom_left_origin,
            self.version_major,
            self.version_minor,
            self.cache_context,
            self.context_destroy,
            self.debug_context,
        )


__all__ = [
    "HardwareContext",
    "retro_hw_context_reset_t",
    "retro_hw_get_current_framebuffer_t",
    "retro_hw_get_proc_address_t",
    "retro_hw_render_callback",
    "HW_FRAME_BUFFER_VALID",
    "retro_hw_context_type",
]
