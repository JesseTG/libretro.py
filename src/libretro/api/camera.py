"""
Interface and types for providing video input to a :class:`.Core`.

.. seealso::

    :class:`.CameraDriver`
        The protocol that uses these types to implement camera support in libretro.py.

    :mod:`libretro.drivers.camera`
        libretro.py's included :class:`.CameraDriver` implementations.
"""

from ctypes import (
    Structure,
    c_bool,
    c_float,
    c_int,
    c_size_t,
    c_uint,
    c_uint32,
    c_uint64,
)
from dataclasses import dataclass
from enum import IntEnum, IntFlag

from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

retro_camera_buffer = c_int
RETRO_CAMERA_BUFFER_OPENGL_TEXTURE = 0
RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER = RETRO_CAMERA_BUFFER_OPENGL_TEXTURE + 1
RETRO_CAMERA_BUFFER_DUMMY = 0x7FFFFFFF


retro_camera_start_t = TypedFunctionPointer[c_bool, []]
"""Called by the :class:`.Core` to start using the camera. Returns :obj:`True` on success."""

retro_camera_stop_t = TypedFunctionPointer[None, []]
"""Called by the :class:`.Core` to stop using the camera."""

retro_camera_lifetime_status_t = TypedFunctionPointer[None, []]
"""Called by libretro.py when the camera is initialized or deinitialized."""

retro_camera_frame_raw_framebuffer_t = TypedFunctionPointer[
    None, [TypedPointer[c_uint32], CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_size_t]]
]
"""Called by libretro.py when a raw framebuffer frame is available from the camera."""

retro_camera_frame_opengl_texture_t = TypedFunctionPointer[
    None, [CIntArg[c_uint], CIntArg[c_uint], TypedPointer[c_float]]
]
"""Called by libretro.py when an OpenGL texture frame is available from the camera."""


class CameraCapabilities(IntEnum):
    """
    Denotes camera features requested by the :class:`.Core`
    and/or supported by the :class:`.CameraDriver`.

    Corresponds to :c:type:`retro_camera_buffer`.
    """

    OPENGL_TEXTURE = RETRO_CAMERA_BUFFER_OPENGL_TEXTURE
    RAW_FRAMEBUFFER = RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER

    def flag(self) -> int:
        """
        Returns this capability as a bitmask flag.

        Equivalent to ``1 << self.value``.

        >>> from libretro.api import CameraCapabilities
        >>> CameraCapabilities.OPENGL_TEXTURE.flag()
        1
        """
        return 1 << self.value


class CameraCapabilityFlags(IntFlag):
    """
    Bitmask of supported camera driver features.

    >>> from libretro.api import CameraCapabilityFlags
    >>> CameraCapabilityFlags.RAW_FRAMEBUFFER | CameraCapabilityFlags.OPENGL_TEXTURE
    <CameraCapabilityFlags.RAW_FRAMEBUFFER|OPENGL_TEXTURE: 3>
    """

    OPENGL_TEXTURE = 1 << CameraCapabilities.OPENGL_TEXTURE
    RAW_FRAMEBUFFER = 1 << CameraCapabilities.RAW_FRAMEBUFFER


@dataclass(init=False, slots=True)
class retro_camera_callback(Structure):
    """
    Configures the interface between the :class:`.Core` and the :class:`.CameraDriver`.

    Corresponds to :c:type:`retro_camera_callback` in ``libretro.h``.
    """

    caps: int
    """
    Bitmask of requested :class:`CameraCapabilities`.

    Assigned values will be bitwise-masked to fit into a :c:type:`uint64_t`.

    .. seealso:: :attr:`.CameraDriver.caps`
    """

    width: int
    """
    The :class:`.Core`'s requested width of the camera frame in pixels.
    ``0`` means that the :class:`.CameraDriver` should choose the width.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.

    .. seealso:: :attr:`.CameraDriver.width`
    """

    height: int
    """
    The :class:`.Core`'s requested height of the camera frame in pixels.
    ``0`` means that the :class:`.CameraDriver` should choose the height.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.

    .. seealso:: :attr:`.CameraDriver.height`
    """

    start: retro_camera_start_t | None
    """
    Called by the :class:`.Core` to start the camera.

    .. seealso:: :meth:`.CameraDriver.start`
    """

    stop: retro_camera_stop_t | None
    """
    Called by the :class:`.Core` to stop the camera.

    .. seealso:: :meth:`.CameraDriver.stop`
    """

    frame_raw_framebuffer: retro_camera_frame_raw_framebuffer_t | None
    """
    Called by the :class:`.CameraDriver` when it produces a frame backed by a raw framebuffer.
    Set by the :class:`.Core`.

    .. seealso:: :attr:`.CameraDriver.frame_raw_framebuffer`
    """

    frame_opengl_texture: retro_camera_frame_opengl_texture_t | None
    """
    Called by the :class:`.CameraDriver` when it produces a frame backed by an OpenGL texture.
    Set by the :class:`.Core`.

    .. seealso:: :attr:`.CameraDriver.frame_opengl_texture`
    """

    initialized: retro_camera_lifetime_status_t | None
    """
    Called by the :class:`.CameraDriver` after it's initialized. Set by the :class:`.Core`. Optional.

    .. seealso:: :attr:`.CameraDriver.initialized`
    """

    deinitialized: retro_camera_lifetime_status_t | None
    """
    Called by the :class:`.CameraDriver` before it's deinitialized. Set by the :class:`.Core`. Optional.

    .. seealso:: :attr:`.CameraDriver.deinitialized`
    """

    _fields_ = (
        ("caps", c_uint64),
        ("width", c_uint),
        ("height", c_uint),
        ("start", retro_camera_start_t),
        ("stop", retro_camera_stop_t),
        ("frame_raw_framebuffer", retro_camera_frame_raw_framebuffer_t),
        ("frame_opengl_texture", retro_camera_frame_opengl_texture_t),
        ("initialized", retro_camera_lifetime_status_t),
        ("deinitialized", retro_camera_lifetime_status_t),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_camera_callback
        >>> cb = retro_camera_callback(caps=1, width=640, height=480)
        >>> cb2 = copy.deepcopy(cb)
        >>> cb == cb2
        True
        >>> cb is cb2
        False
        """
        return retro_camera_callback(
            caps=self.caps,
            width=self.width,
            height=self.height,
            start=self.start,
            stop=self.stop,
            frame_raw_framebuffer=self.frame_raw_framebuffer,
            frame_opengl_texture=self.frame_opengl_texture,
            initialized=self.initialized,
            deinitialized=self.deinitialized,
        )


__all__ = [
    "retro_camera_start_t",
    "retro_camera_stop_t",
    "retro_camera_lifetime_status_t",
    "retro_camera_frame_raw_framebuffer_t",
    "retro_camera_frame_opengl_texture_t",
    "retro_camera_callback",
    "CameraCapabilities",
    "CameraCapabilityFlags",
    "retro_camera_buffer",
]
