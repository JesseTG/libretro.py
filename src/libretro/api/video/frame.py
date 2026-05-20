"""
Pixel format and software framebuffer types.

Corresponds to the ``retro_pixel_format`` and ``retro_framebuffer`` types
in ``libretro.h``.
"""

from ctypes import Structure, c_int, c_size_t, c_uint
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Literal

from libretro.api._utils import deepcopy_buffer
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
"""
Render a single video frame.

Registered by the :term:`frontend` and called by the :term:`core`
once per :c:func:`retro_run` to deliver a frame of pixel data.
Passing :obj:`None` (or the value of :data:`~libretro.api.video.HW_FRAME_BUFFER_VALID` for hardware rendering)
for ``data`` indicates that the frontend should reuse the previous frame.

:param data: A :class:`~libretro.ctypes.c_void_ptr` to the framebuffer.
    The pixel format is the one most recently set with
    :data:`~libretro.api.environment.RETRO_ENVIRONMENT_SET_PIXEL_FORMAT`,
    defaulting to :attr:`.PixelFormat.RGB1555`.
:param width: Width of the frame, in pixels.
:param height: Height of the frame, in pixels.
:param pitch: Length of one row in ``data``, in bytes.

.. note::
    For best performance the framebuffer should be packed
    (i.e. ``pitch == width * bytes_per_pixel``).

Corresponds to :c:type:`retro_video_refresh_t` in ``libretro.h``.
"""


class PixelFormat(IntEnum):
    """
    Pixel format for video output.

    Corresponds to :c:type:`retro_pixel_format` in ``libretro.h``.

    >>> from libretro.api.video import PixelFormat
    >>> PixelFormat.XRGB8888.bytes_per_pixel
    4
    """

    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    @property
    def bytes_per_pixel(self) -> Literal[2, 4]:
        """Size of a single pixel in this format, in bytes."""
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
        """Typecode for this pixel format, suitable for use with :mod:`array` or :mod:`struct`."""
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
        """PIL-compatible mode string for this pixel format."""
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
    """
    Flags describing allowed memory access for a framebuffer.

    Corresponds to the ``RETRO_MEMORY_ACCESS_*`` constants in ``libretro.h``.
    """

    NONE = 0
    WRITE = RETRO_MEMORY_ACCESS_WRITE
    READ = RETRO_MEMORY_ACCESS_READ


class MemoryType(IntFlag):
    """
    Flags describing the type of memory behind a framebuffer.

    Corresponds to the ``RETRO_MEMORY_TYPE_*`` constants in ``libretro.h``.
    """

    NONE = 0
    CACHED = RETRO_MEMORY_TYPE_CACHED


@dataclass(init=False, slots=True)
class retro_framebuffer(Structure):
    """
    Corresponds to :c:type:`retro_framebuffer` in ``libretro.h``.

    Describes a framebuffer obtained from the frontend.

    >>> from libretro.api.video import retro_framebuffer
    >>> fb = retro_framebuffer()
    >>> fb.data is None
    True
    """

    data: c_void_ptr | None
    """Pointer to the framebuffer's pixel data."""
    width: int
    """Width of the framebuffer in pixels."""
    height: int
    """Height of the framebuffer in pixels."""
    pitch: int
    """Number of bytes per row."""
    format: PixelFormat
    """Pixel format of the framebuffer."""
    access_flags: MemoryAccess
    """Allowed memory access flags."""
    memory_flags: MemoryType
    """Memory type flags."""

    _fields_ = (
        ("data", c_void_ptr),
        ("width", c_uint),
        ("height", c_uint),
        ("pitch", c_size_t),
        ("format", retro_pixel_format),
        ("access_flags", c_uint),
        ("memory_flags", c_uint),
    )

    def __deepcopy__(self, _):
        """
        Create a deep copy of this framebuffer, including the pixel data.
        Intended for use by :func:`copy.deepcopy`.
        """
        return retro_framebuffer(
            deepcopy_buffer(self.data, self.height * self.pitch),
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
