from ctypes import *
from dataclasses import dataclass
from enum import IntEnum, IntFlag

from ..._utils import FieldsFromTypeHints
from ...h import *

retro_video_refresh_t = CFUNCTYPE(None, c_void_p, c_uint, c_uint, c_size_t)
retro_usec_t = c_int64
retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


@dataclass(init=False)
class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t

    def __deepcopy__(self, _):
        return retro_frame_time_callback(self.callback, int(self.reference))


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

    @property
    def pixel_typecode(self) -> str:
        match self:
            case self.RGB1555:
                return 'H'
            case self.XRGB8888:
                return 'L'
            case self.RGB565:
                return 'H'
            case _:
                raise ValueError(f"Unknown pixel format: {self}")

    @property
    def pillow_mode(self) -> str:
        match self:
            case self.RGB1555:
                return 'BGR;15'
            case self.XRGB8888:
                return 'RGBX'
            case self.RGB565:
                return 'BGR;16'
            case _:
                raise ValueError(f"Unknown pixel format: {self}")


class MemoryAccess(IntFlag):
    NONE = 0
    WRITE = RETRO_MEMORY_ACCESS_WRITE
    READ = RETRO_MEMORY_ACCESS_READ


class MemoryType(IntFlag):
    NONE = 0
    CACHED = RETRO_MEMORY_TYPE_CACHED


@dataclass(init=False)
class retro_framebuffer(Structure, metaclass=FieldsFromTypeHints):
    data: c_void_p
    width: c_uint
    height: c_uint
    pitch: c_size_t
    format: retro_pixel_format
    access_flags: c_uint
    memory_flags: c_uint


__all__ = [
    'retro_video_refresh_t',
    'retro_usec_t',
    'retro_frame_time_callback_t',
    'retro_frame_time_callback',
    'Rotation',
    'PixelFormat',
    'MemoryAccess',
    'MemoryType',
    'retro_framebuffer',
]
