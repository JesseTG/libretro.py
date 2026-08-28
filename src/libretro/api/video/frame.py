"""
Pixel format and software framebuffer types.

Corresponds to the ``retro_pixel_format`` and ``retro_framebuffer`` types
in ``libretro.h``.
"""

from ctypes import Structure, c_int, c_size_t, c_uint
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Literal

from libretro.api._utils import NullPointerToNoneMixin, deepcopy_buffer
from libretro.ctypes import CIntArg, TypedFunctionPointer, c_void_ptr

retro_pixel_format = c_int
RETRO_PIXEL_FORMAT_0RGB1555 = 0
RETRO_PIXEL_FORMAT_XRGB8888 = 1
RETRO_PIXEL_FORMAT_RGB565 = 2
RETRO_PIXEL_FORMAT_XRGB2101010 = 3
RETRO_PIXEL_FORMAT_HDR10_2101010 = 4
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

    XRGB2101010 = RETRO_PIXEL_FORMAT_XRGB2101010
    """
    10 bits per channel, packed into 32 bits in native byte order:
    two ignored high bits, then red in bits 29-20, green in 19-10, and blue in 9-0.

    Standard-dynamic-range content, for cores that decode 10-bit sources
    and would rather not narrow them to 8 bits.
    A frontend is free to accept this format
    and then transparently down-convert it to :attr:`XRGB8888`
    when its video driver can't present a 10-bit surface,
    so a core cannot assume the whole display path is 10-bit.

    .. seealso::

        :attr:`.EnvironmentCall.GET_SCREEN_10BPC_CAPABLE`
            The environment call that reports whether 10 bits survive to the display.
    """

    HDR10_2101010 = RETRO_PIXEL_FORMAT_HDR10_2101010
    """
    HDR10: the same bit layout as :attr:`XRGB2101010`, but a different encoding.

    Samples are SMPTE ST.2084 (PQ) over Rec.2020 primaries, covering 0 to 10000 nits,
    exactly as HDR10 video does.
    Because the core chooses absolute luminance per pixel,
    highlights can sit well above SDR paper white
    while the rest of the image stays where it was.

    A frontend that accepts this format must pass the samples through unchanged;
    one that can't present HDR10 natively must reject it outright,
    since silently narrowing PQ samples to SDR looks badly wrong.
    Cores should therefore keep an SDR path to fall back to.

    .. seealso::

        :attr:`.EnvironmentCall.GET_HDR_PAPER_WHITE_NITS`
            The luminance the frontend treats as SDR white,
            which a core should map its ordinary output to.
    """

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
            case self.XRGB2101010:
                return 4
            case self.HDR10_2101010:
                return 4
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
            case self.XRGB2101010:
                return "L"
            case self.HDR10_2101010:
                return "L"
            case _:
                raise ValueError(f"Unknown pixel format: {self}")


retro_hdr_expand_gamut = c_uint
"""The type the frontend writes a :class:`HdrExpandGamut` value through."""

retro_hdr_output_mode = c_uint
"""The type the frontend writes a :class:`HdrOutputMode` value through."""


class HdrExpandGamut(IntEnum):
    """
    How the frontend widens the colour gamut of SDR content when presenting HDR.

    Only meaningful alongside :attr:`.PixelFormat.HDR10_2101010`.
    A core emitting that format performs its own Rec.709 to Rec.2020 rotation,
    and has to make the same choice the frontend makes for SDR content;
    otherwise a scene changes saturation
    when the user switches the core between an SDR format and HDR10.

    .. note::
        ``libretro.h`` documents these values in prose without naming them,
        so this enumeration is a libretro.py convenience
        rather than a mirror of a C type.

    .. seealso::

        :attr:`.EnvironmentCall.GET_HDR_EXPAND_GAMUT`
            The environment call that reports this setting.

    >>> from libretro.api import HdrExpandGamut
    >>> HdrExpandGamut.ACCURATE
    <HdrExpandGamut.ACCURATE: 0>
    """

    ACCURATE = 0
    """A faithful Rec.709 to Rec.2020 conversion, with no boost."""

    EXPANDED = 1
    """Rec.709 mapped into a slightly wider space than it started in."""

    WIDE = 2
    """Rec.709 mapped into DCI-P3."""

    SUPER = 3
    """
    No rotation at all.

    Values stay in Rec.709, and the boost comes from the display
    interpreting them as Rec.2020.
    """


class HdrOutputMode(IntEnum):
    """
    Which HDR output path the frontend is presenting through.

    Only meaningful alongside :attr:`.PixelFormat.HDR10_2101010`.
    Both output modes accept the same PQ Rec.2020 frame
    but do not treat its primaries identically,
    so a core that encodes its own gamut has to know which one it is feeding.

    .. note::
        ``libretro.h`` documents these values in prose without naming them,
        so this enumeration is a libretro.py convenience
        rather than a mirror of a C type.

    .. seealso::

        :attr:`.EnvironmentCall.GET_HDR_OUTPUT_MODE`
            The environment call that reports this setting.

    >>> from libretro.api import HdrOutputMode
    >>> HdrOutputMode.SCRGB
    <HdrOutputMode.SCRGB: 2>
    """

    OFF = 0
    """HDR output is disabled."""

    HDR10 = 1
    """A PQ Rec.2020 swapchain, which presents the core's samples unchanged."""

    SCRGB = 2
    """
    A linear FP16 Rec.709 swapchain.

    The frontend applies a Rec.2020 to Rec.709 rotation to the decoded samples,
    so a core that has already chosen its own gamut must compensate for it here.
    """


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
class retro_framebuffer(Structure, NullPointerToNoneMixin):
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
    "retro_hdr_expand_gamut",
    "retro_hdr_output_mode",
    "HdrExpandGamut",
    "HdrOutputMode",
]
