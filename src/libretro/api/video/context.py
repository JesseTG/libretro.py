"""
Types that describe hardware rendering contexts and callbacks for using them.
"""

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
"""
Passed to :class:`.retro_video_refresh_t` to signal that the next video frame
should be rendered with the GPU context state instead of a framebuffer.
"""


class HardwareContext(IntEnum):
    """
    Denotes a hardware rendering API supported by libretro.
    Hardware rendering context type.

    Corresponds to :c:type:`retro_hw_context_type` in ``libretro.h``.

    .. seealso::
        :class:`.VideoDriver`
            The :class:`~typing.Protocol` that implements one or more of these context types.
    """

    NONE = RETRO_HW_CONTEXT_NONE
    """
    Software rendering only.

    .. note::
        The active :class:`.VideoDriver` may still use a hardware rendering API,
        but it won't be exposed to the core.
    """

    OPENGL = RETRO_HW_CONTEXT_OPENGL
    """OpenGL 2.x, or a newer OpenGL version with the compatibility profile."""

    OPENGLES2 = RETRO_HW_CONTEXT_OPENGLES2
    """OpenGL ES 2.0."""

    OPENGL_CORE = RETRO_HW_CONTEXT_OPENGL_CORE
    """OpenGL 3.2+ core profile."""

    OPENGLES3 = RETRO_HW_CONTEXT_OPENGLES3
    """OpenGL ES 3.0."""

    OPENGLES_VERSION = RETRO_HW_CONTEXT_OPENGLES_VERSION
    """OpenGL ES with version specified by :attr:`.version_major` and :attr:`.version_minor`."""

    VULKAN = RETRO_HW_CONTEXT_VULKAN
    """
    Vulkan.

    .. note::
        libretro.py doesn't currently support Vulkan contexts.
    """

    DIRECT3D = 7
    D3D11 = RETRO_HW_CONTEXT_D3D11
    """Direct3D 11."""
    D3D10 = RETRO_HW_CONTEXT_D3D10
    """Direct3D 10."""
    D3D12 = RETRO_HW_CONTEXT_D3D12
    """Direct3D 12."""
    D3D9 = RETRO_HW_CONTEXT_D3D9
    """Direct3D 9."""


retro_hw_context_reset_t = TypedFunctionPointer[None, []]
"""
Context reset/destroy callback.
"""

retro_hw_get_current_framebuffer_t = TypedFunctionPointer[c_uintptr, []]
"""
Returns the current hardware framebuffer,
if applicable for the current rendering API and context state.

.. note::
    This callback exists for historical reasons and is only meaningful for OpenGL contexts.
"""

retro_hw_get_proc_address_t = TypedFunctionPointer[c_void_ptr, [CStringArg]]
"""Looks up a hardware rendering procedure by name."""
# Workaround for ctypes not allowing callbacks to return function pointers


@dataclass(init=False, slots=True)
class retro_hw_render_callback(Structure):
    """
    Describes the hardware rendering context a core requires
    and provides callbacks for reacting to or querying the context.

    Corresponds to :c:type:`retro_hw_render_callback` in ``libretro.h``.


    >>> from libretro.api.video import retro_hw_render_callback, HardwareContext
    >>> cb = retro_hw_render_callback()
    >>> cb.context_type == HardwareContext.NONE
    True
    """

    context_type: HardwareContext
    """Hardware rendering API to use."""

    context_reset: retro_hw_context_reset_t | None
    """
    Called when the rendering context is created or reset.

    .. seealso::
        :meth:`.VideoDriver.reinit`
            The suggested method to call this callback.
    """

    get_current_framebuffer: retro_hw_get_current_framebuffer_t | None
    """
    Returns the current hardware framebuffer. Set by the frontend.

    .. note::
        This callback exists for historical reasons and is only meaningful for OpenGL contexts.

    .. seealso::
        :meth:`.VideoDriver.get_current_framebuffer`
    """

    get_proc_address: retro_hw_get_proc_address_t | None
    """
    Looks up a rendering API function by name. Set by the frontend.

    .. seealso::
        :meth:`.VideoDriver.get_proc_address`
            The suggested method to implement this callback.
    """

    depth: bool
    """
    Whether the framebuffer should have a depth component.

    .. note::
        This field exists for historical reasons and is only meaningful for OpenGL contexts.
    """

    stencil: bool
    """
    Whether the framebuffer should have a stencil component.

    .. note::
        This field exists for historical reasons and is only meaningful for OpenGL contexts.
    """

    bottom_left_origin: bool
    """Whether to use bottom-left origin convention."""

    version_major: int
    """Major version number for the rendering context."""

    version_minor: int
    """Minor version number for the rendering context."""

    cache_context: bool
    """
    Whether the frontend should avoid resetting the context.
    """

    context_destroy: retro_hw_context_reset_t | None
    """
    Called before the context is destroyed.
    """

    debug_context: bool
    """Whether to create a debug rendering context."""

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
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
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
