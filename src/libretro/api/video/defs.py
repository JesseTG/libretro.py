from ctypes import *
from enum import IntEnum

from ..proc import retro_proc_address_t
from ..._utils import FieldsFromTypeHints, c_uintptr, UNCHECKED
from ...h import *

retro_video_refresh_t = CFUNCTYPE(None, c_void_p, c_uint, c_uint, c_size_t)
retro_usec_t = c_int64
retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t


class Rotation(IntEnum):
    NONE = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3

    def __init__(self, value):
        self._type_ = 'I'


class PixelFormat(IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    def __init__(self, value):
        self._type_ = 'I'

    @property
    def bytes_per_pixel(self) -> int:
        match self:
            case self.RGB1555:
                return 2
            case self.XRGB8888:
                return 4
            case self.RGB565:
                return 2
            case _:
                raise ValueError(f"Unknown pixel format: {self}")


class retro_framebuffer(Structure, metaclass=FieldsFromTypeHints):
    data: c_void_p
    width: c_uint
    height: c_uint
    pitch: c_size_t
    format: retro_pixel_format
    access_flags: c_uint
    memory_flags: c_uint


retro_hw_context_reset_t = CFUNCTYPE(None)
retro_hw_get_current_framebuffer_t = CFUNCTYPE(c_uintptr)
retro_hw_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), c_char_p)


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
    'retro_video_refresh_t',
    'retro_usec_t',
    'retro_frame_time_callback_t',
    'retro_frame_time_callback',
    'Rotation',
    'PixelFormat',
    'retro_framebuffer',
    'retro_hw_context_reset_t',
    'retro_hw_get_current_framebuffer_t',
    'retro_hw_get_proc_address_t',
    'retro_hw_render_callback',
]
