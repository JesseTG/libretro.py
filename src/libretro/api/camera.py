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
"""
Start the camera.

Called by the :term:`core` to begin receiving camera frames from the frontend.
Cameras are disabled by default and must be explicitly started.

:return: :obj:`True` if the camera was successfully started,
    :obj:`False` if no camera is available
    or the frontend lacks permission to access it.

Corresponds to :c:type:`retro_camera_start_t` in ``libretro.h``.
"""

retro_camera_stop_t = TypedFunctionPointer[None, []]
"""
Stop the running camera.

Called by the :term:`core` to halt the delivery of camera frames.

Corresponds to :c:type:`retro_camera_stop_t` in ``libretro.h``.
"""

retro_camera_lifetime_status_t = TypedFunctionPointer[None, []]
"""
Notify the core that the camera driver has been initialized or deinitialized.

Registered by the :term:`core` and called by the :term:`frontend`
right after the camera driver is initialized,
or right before it is deinitialized.

Corresponds to :c:type:`retro_camera_lifetime_status_t` in ``libretro.h``.
"""

retro_camera_frame_raw_framebuffer_t = TypedFunctionPointer[
    None, [TypedPointer[c_uint32], CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_size_t]]
]
"""
Deliver a new camera frame as a raw pixel buffer.

Registered by the :term:`core` and called by the :term:`frontend`
when a new camera frame is available in system memory,
with the top-left corner of the image as the first pixel.

:param buffer: Pointer to the camera's most recent video frame,
    with one ``XRGB8888`` pixel per :c:type:`uint32_t`.
:param width: Width of the frame, in pixels.
:param height: Height of the frame, in pixels.
:param pitch: Length of one row in ``buffer``, in bytes.

.. warning::
    ``buffer`` may be invalidated when this function returns,
    so the core should make its own copy if it needs to retain the data.

Corresponds to :c:type:`retro_camera_frame_raw_framebuffer_t` in ``libretro.h``.
"""

retro_camera_frame_opengl_texture_t = TypedFunctionPointer[
    None, [CIntArg[c_uint], CIntArg[c_uint], TypedPointer[c_float]]
]
"""
Deliver a new camera frame as an OpenGL texture.

Registered by the :term:`core` and called by the :term:`frontend`
when a new camera frame is available as a frontend-owned OpenGL texture.

:param texture_id: ID of the OpenGL texture that holds the frame.
    Owned by the frontend; the core must not modify it.
:param texture_target: OpenGL texture target type
    (e.g. ``GL_TEXTURE_2D`` or ``GL_TEXTURE_RECTANGLE``).
:param affine: Pointer to a 3x3 column-major affine matrix
    that maps pixel coordinates to texture coordinates.

.. warning::
    ``texture_id`` and ``affine`` may be invalidated when this function returns,
    so the core should make its own copy if it needs to retain them.

Corresponds to :c:type:`retro_camera_frame_opengl_texture_t` in ``libretro.h``.
"""


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
        Return this capability as a bitmask flag.

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
    Interface between the :term:`core` and the :class:`.CameraDriver`.

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
    The :term:`core`'s requested width of the camera frame in pixels.
    ``0`` means that the :class:`.CameraDriver` should choose the width.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.

    .. seealso:: :attr:`.CameraDriver.width`
    """

    height: int
    """
    The :term:`core`'s requested height of the camera frame in pixels.
    ``0`` means that the :class:`.CameraDriver` should choose the height.

    Assigned values will be bitwise-masked to fit into an :c:expr:`unsigned int`.

    .. seealso:: :attr:`.CameraDriver.height`
    """

    start: retro_camera_start_t | None
    """
    Called by the :term:`core` to start the camera.

    .. seealso:: :meth:`.CameraDriver.start`
    """

    stop: retro_camera_stop_t | None
    """
    Called by the :term:`core` to stop the camera.

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
        Return a deep copy of this object.
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
