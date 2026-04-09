from ctypes import Structure, c_int, c_size_t, c_uint
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Literal

from libretro.ctypes import CIntArg, TypedFunctionPointer, c_void_ptr

retro_pixel_format = c_int
RETRO_PIXEL_FORMAT_0RGB1555 = 0
RETRO_PIXEL_FORMAT_XRGB8888 = 1
RETRO_PIXEL_FORMAT_RGB565 = 2
RETRO_PIXEL_FORMAT_UNKNOWN = 0x7FFFFFFF
RETRO_MEMORY_ACCESS_WRITE = 1 << 0
RETRO_MEMORY_ACCESS_READ = 1 << 1
RETRO_MEMORY_TYPE_CACHED = 1 << 0


retro_video_refresh_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_size_t]]
]


class PixelFormat(IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    @property
    def bytes_per_pixel(self) -> Literal[2, 4]:
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
    def pixel_typecode(self) -> Literal["H", "L"]:
        match self:
            case self.RGB1555:
                return "H"
            case self.XRGB8888:
                return "L"
            case self.RGB565:
                return "H"
            case _:
                raise ValueError(f"Unknown pixel format: {self}")

    @property
    def pillow_mode(self) -> Literal["BGR;15", "RGBX", "BGR;16"]:
        match self:
            case self.RGB1555:
                return "BGR;15"
            case self.XRGB8888:
                return "RGBX"
            case self.RGB565:
                return "BGR;16"
            case _:
                raise ValueError(f"Unknown pixel format: {self}")


class MemoryAccess(IntFlag):
    NONE = 0
    WRITE = RETRO_MEMORY_ACCESS_WRITE
    READ = RETRO_MEMORY_ACCESS_READ


class MemoryType(IntFlag):
    NONE = 0
    CACHED = RETRO_MEMORY_TYPE_CACHED


@dataclass(init=False, slots=True)
class retro_framebuffer(Structure):
    data: c_void_ptr | None
    width: int
    height: int
    pitch: int
    format: PixelFormat
    access_flags: MemoryAccess
    memory_flags: MemoryType

    _fields_ = (
        ("data", c_void_ptr),
        ("width", c_uint),
        ("height", c_uint),
        ("pitch", c_size_t),
        ("format", retro_pixel_format),
        ("access_flags", c_uint),
        ("memory_flags", c_uint),
    )

    # TODO: Copy the framebuffer, but also implement plain copy()
    def __deepcopy__(self, _):
        return retro_framebuffer(
            self.data,
            self.width,
            self.height,
            self.pitch,
            self.format,
            self.access_flags,
            self.memory_flags,
        )


__all__ = [
    "retro_video_refresh_t",
    "PixelFormat",
    "MemoryAccess",
    "MemoryType",
    "retro_framebuffer",
    "retro_pixel_format",
]
