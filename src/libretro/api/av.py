"""
Types to describe the parameters of a core's rendered audio and video.

.. seealso:: :mod:`libretro.drivers.video`, :mod:`libretro.drivers.audio`
"""

from ctypes import Structure, c_double, c_float, c_uint
from dataclasses import dataclass
from enum import CONFORM, IntEnum, IntFlag

RETRO_REGION_NTSC = 0
RETRO_REGION_PAL = 1

retro_av_enable_flags = c_uint
RETRO_AV_ENABLE_VIDEO = 1 << 0
RETRO_AV_ENABLE_AUDIO = 1 << 1
RETRO_AV_ENABLE_FAST_SAVESTATES = 1 << 2
RETRO_AV_ENABLE_HARD_DISABLE_AUDIO = 1 << 3
RETRO_AV_ENABLE_DUMMY = 0x7FFFFFFF


class Region(IntEnum):
    """
    TV region.

    .. seealso::

        :meth:`.Core.get_region`
    """

    NTSC = RETRO_REGION_NTSC
    """
    Corresponds to :c:macro:`RETRO_REGION_NTSC`.

    .. tip::

        Cores may also return this if the NTSC/PAL region isn't applicable,
        e.g. for handhelds or arcade machines.
    """

    PAL = RETRO_REGION_PAL
    """Corresponds to :c:macro:`RETRO_REGION_PAL`."""


class AvEnableFlags(IntFlag, boundary=CONFORM):
    """
    Bit flags that denote whether the loaded :class:`Core`
    should render audio and/or video frames.

    .. tip::

        These flags can be set even if libretro.py isn't literally
        showing audio or video output to the user.

    .. seealso::

        :attr:`.EnvironmentCall.GET_AUDIO_VIDEO_ENABLE`
    """

    VIDEO = RETRO_AV_ENABLE_VIDEO
    """
    If not set, the :class:`.Core` can safely skip rendering the next video frame.

    Corresponds to :c:macro:`RETRO_AV_ENABLE_VIDEO`.
    """

    AUDIO = RETRO_AV_ENABLE_AUDIO
    """
    If not set, the :class:`.Core` can safely skip rendering the next audio frame.

    Corresponds to :c:macro:`RETRO_AV_ENABLE_AUDIO`.
    """

    FAST_SAVESTATES = RETRO_AV_ENABLE_FAST_SAVESTATES
    """
    Indicates that savestates will only be used by this process
    and will not be saved to disk.

    Corresponds to :c:macro:`RETRO_AV_ENABLE_FAST_SAVESTATES`.

    .. seealso::

        :attr:`.EnvironmentCall.GET_SAVESTATE_CONTEXT`
    """

    HARD_DISABLE_AUDIO = RETRO_AV_ENABLE_HARD_DISABLE_AUDIO
    """
    If set, the :class:`.Core` can safely skip rendering audio frames
    for the entire duration of its execution.

    Corresponds to :c:macro:`RETRO_AV_ENABLE_HARD_DISABLE_AUDIO`.
    """

    ALL = VIDEO | AUDIO | FAST_SAVESTATES | HARD_DISABLE_AUDIO
    """
    All other flags are set.

    .. caution::

        If additional flags are added in the future,
        this value will be updated to include them.
        Try not to rely on the exact value of this constant.
    """


@dataclass(init=False, slots=True)
class retro_game_geometry(Structure):
    """
    Describes the expected (and possible) size of the framebuffer.

    Corresponds to :c:type:`retro_game_geometry`.

    .. warning::

        This object is mutable, therefore :class:`.VideoDriver` s
        should not expose or store references to it;
        all access should be done through copies,
        otherwise you run the risk of encountering hard-to-debug issues!

    .. seealso::

        :attr:`.VideoDriver.geometry`
    """

    # Structure subclasses implicitly convert primitive fields
    # to and from their ctypes equivalents, so we can define these
    # as their natural types for better type checking and readability.
    base_width: int
    """
    Nominal video width in pixels.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.
    """

    base_height: int
    """
    Nominal video height in pixels.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.
    """

    max_width: int
    """
    Maximum possible video width in pixels.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.
    """

    max_height: int
    """
    Maximum possible video height in pixels.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.
    """

    aspect_ratio: float
    """
    Nominal aspect ratio.
    ``0.0`` indicates that it should be calculated
    from :attr:`base_width` and :attr:`base_height`.

    Assigned values will be converted to a C :c:expr:`float`.
    """

    _fields_ = (
        ("base_width", c_uint),
        ("base_height", c_uint),
        ("max_width", c_uint),
        ("max_height", c_uint),
        ("aspect_ratio", c_float),
    )

    # ctypes structures don't natively support deepcopy, so we have to implement it ourselves.
    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_game_geometry
        >>> geom = retro_game_geometry(base_width=320, base_height=240, max_width=640, max_height=480, aspect_ratio=0.0)
        >>> geom2 = copy.deepcopy(geom)
        >>> geom == geom2
        True
        >>> geom is geom2
        False
        """
        return retro_game_geometry(
            base_width=self.base_width,
            base_height=self.base_height,
            max_width=self.max_width,
            max_height=self.max_height,
            aspect_ratio=self.aspect_ratio,
        )

    @property
    def base_size(self) -> tuple[int, int]:
        """
        The base (nominal) resolution as ``(width, height)``.

        >>> from libretro.api import retro_game_geometry
        >>> geom = retro_game_geometry(base_width=256, base_height=224, max_width=256, max_height=224)
        >>> geom.base_size
        (256, 224)
        >>> (geom.base_width, geom.base_height) == geom.base_size
        True
        """
        return self.base_width, self.base_height

    @property
    def max_size(self) -> tuple[int, int]:
        """
        The maximum possible resolution as ``(width, height)``.

        >>> from libretro.api import retro_game_geometry
        >>> geom = retro_game_geometry(base_width=256, base_height=224, max_width=512, max_height=448)
        >>> geom.max_size
        (512, 448)
        >>> (geom.max_width, geom.max_height) == geom.max_size
        True
        """
        return self.max_width, self.max_height


@dataclass(init=False, slots=True)
class retro_system_timing(Structure):
    """
    Describes the timing of the emulated system's video and audio output.

    Corresponds to :c:type:`retro_system_timing` in ``libretro.h``.
    """

    fps: float
    """
    The :class:`.Core`'s video refresh rate in frames per second.

    Assigned values will be converted to a C :c:expr:`double`.
    """

    sample_rate: float
    """
    The :class:`.Core`'s audio output rate in Hz.

    Assigned values will be converted to a C :c:expr:`double`.
    """

    _fields_ = (
        ("fps", c_double),
        ("sample_rate", c_double),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_system_timing
        >>> timing = retro_system_timing(fps=60.0, sample_rate=44100.0)
        >>> copy.deepcopy(timing).sample_rate
        44100.0
        """
        return retro_system_timing(self.fps, self.sample_rate)


@dataclass(init=False, slots=True)
class retro_system_av_info(Structure):
    """
    Bundles the system's geometry and timing information.

    Corresponds to :c:type:`retro_system_av_info` in ``libretro.h``.

    .. warning::

        This object is mutable, therefore :class:`.VideoDriver` s and :class:`.AudioDriver` s
        should not expose or store references to it;
        all access should be done through copies,
        otherwise you run the risk of encountering hard-to-debug issues!

    >>> from libretro.api import retro_system_av_info, retro_game_geometry, retro_system_timing
    >>> geom = retro_game_geometry(base_width=320, base_height=240, max_width=320, max_height=240)
    >>> timing = retro_system_timing(fps=60.0, sample_rate=32000.0)
    >>> av = retro_system_av_info(geom, timing)
    >>> av.geometry.base_width
    320
    >>> av.timing.fps
    60.0

    .. seealso::

        :attr:`.Core.get_system_av_info`
    """

    geometry: retro_game_geometry
    """Video output geometry."""

    timing: retro_system_timing
    """Audio/video timing information."""

    _fields_ = (
        ("geometry", retro_game_geometry),
        ("timing", retro_system_timing),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_system_av_info, retro_game_geometry, retro_system_timing
        >>> geom = retro_game_geometry(base_width=320, base_height=240, max_width=320, max_height=240)
        >>> timing = retro_system_timing(fps=60.0, sample_rate=32000.0)
        >>> av = retro_system_av_info(geom, timing)
        >>> av2 = copy.deepcopy(av)
        >>> av2.timing.sample_rate
        32000.0
        """
        return retro_system_av_info(self.geometry, self.timing)


__all__ = [
    "Region",
    "AvEnableFlags",
    "retro_game_geometry",
    "retro_system_timing",
    "retro_system_av_info",
    "retro_av_enable_flags",
]
