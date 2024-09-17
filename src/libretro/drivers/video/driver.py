"""
Types and classes for defining how a core renders graphics.
"""

from abc import abstractmethod
from collections.abc import Set
from enum import Enum
from typing import NamedTuple, Protocol, runtime_checkable

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.video import (
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_render_callback,
    retro_hw_render_interface,
)


class FrameBufferSpecial(Enum):
    DUPE = None
    HARDWARE = -1


class Screenshot(NamedTuple):
    data: memoryview
    width: int
    height: int
    rotation: Rotation
    pixel_format: PixelFormat


@runtime_checkable
class VideoDriver(Protocol):
    """
    Describes functionality for rendering video output,
    including essential libretro callbacks
    and environment calls.

    Some of these may not be implemented by all drivers.
    """

    @abstractmethod
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        """
        Updates the framebuffer with the given video data.
        This method is exposed to the core through ``retro_set_video_refresh``.

        :param data: One of the following:

            :class:`memoryview`
                Contains pixel data in the format given by :attr:`pixel_format`.
                Should be read-only.

            :attr:`FrameBufferSpecial.DUPE`
                If the frontend should re-render the previous frame.

            :attr:`FrameBufferSpecial.HARDWARE`
                If the frontend should render the frame
                using the active graphics API context.

        :param width: The width of the frame in ``data``, in pixels.
        :param height: The height of the frame in ``data``, in pixels.
        :param pitch: The width of the frame in ``data``, in bytes.
        :raises TypeError: If any parameter's type is not consistent with this method's signature.
        :raises ValueError: If ``data`` is a :class:`memoryview`
            and its length is not equal to ``pitch * height``.

        .. note::

            Corresponds to :type:`.retro_video_refresh_t`.
        """
        ...

    @property
    @abstractmethod
    def needs_reinit(self) -> bool:
        """
        :obj:`True` if this video driver needs to be reinitialized,
        usually because of core-requested state changes.
        Can also indicate that the driver hasn't yet been initialized at all.

        .. warning::

            :class:`.VideoDriver` implementations aren't necessarily initialized in their constructors.
        """
        ...

    @abstractmethod
    def reinit(self) -> None:
        """
        Reinitializes the video driver,
        applying any changes made to it since the last call to this method.

        The video driver will perform the following steps:

        1. Call the registered :attr:`.retro_hw_render_callback.context_destroy` (if any)
           to tell the core to release any resources associated with the current graphics API.
        2. Release all libretro.py-managed graphics resources.
        3. Release the graphics context if switching to a different graphics API
           or making changes that require a new context.
        4. Initialize a new graphics context if necessary.
        5. Initialize internal resources for libretro.py.
        6. Call the registered :attr:`.retro_hw_render_callback.context_reset` (if any)
           to tell the core it can initialize its graphics API resources.


        .. tip::

            The purpose of :attr:`.retro_hw_render_callback.cache_context`
            is to tell libretro.py to do its best to avoid calling this method.
        """
        ...

    @property
    @abstractmethod
    def supported_contexts(self) -> Set[HardwareContext]:
        """
        The set of all graphics APIs supported by this driver.
        All video drivers must support at least :attr:`.HardwareContext.NONE`,
        which indicates software rendering capabilities.

        .. tip::

            Most drivers won't support more than one kind of graphics context
            (not counting :attr:`~.HardwareContext.NONE`),
            but this isn't a hard requirement.
        """
        ...

    @property
    @abstractmethod
    def active_context(self) -> HardwareContext:
        """
        The hardware context that is currently exposed to the core.
        Must be an element of :attr:`~.VideoDriver.supported_contexts`.

        Will be :attr:`.HardwareContext.NONE` until the core
        successfully requests a graphics context using :attr:`.EnvironmentCall.SET_HW_RENDER`,
        at which point it will be set to the requested context type.

        .. attention::

            This property *does not* necessarily indicate which graphics API is loaded and active;
            it specifically means the context type that the core **requested**.

            For example, a core that uses software rendering
            wouldn't request a hardware context,
            therefore this property would return :attr:`.HardwareContext.NONE`
            regardless of the actual graphics API in use.

            After all, most of RetroArch's video drivers rely on hardware graphics APIs,
            even if the core doesn't request them.
            If the core is only software-rendered, then what difference does it make?
        """
        ...

    @property
    @abstractmethod
    def preferred_context(self) -> HardwareContext | None:
        """
        The preferred hardware context for this driver.
        Cores that support multiple graphics APIs
        can use this to choose one without the player needing to specify it.

        Can be a member of :attr:`~.VideoDriver.supported_contexts`
        (including :attr:`~.HardwareContext.NONE`)
        to indicate preference for that context,
        or :obj:`None` to disable :attr:`.EnvironmentCall.GET_PREFERRED_HW_RENDER`.

        Setting or deleting this property will not affect the active context.

        :raise ValueError: If attempting to set a preferred context
            that this driver doesn't support (i.e. that's not in :attr:`~.VideoDriver.supported_contexts`).
        :raise TypeError: If attempting to set a value that isn't a :class:`.HardwareContext`.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER``.
        """
        ...

    @preferred_context.setter
    @abstractmethod
    def preferred_context(self, context: HardwareContext) -> None: ...

    @preferred_context.deleter
    @abstractmethod
    def preferred_context(self) -> None: ...

    @abstractmethod
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        """
        Requests the use of a particular graphics context,
        including :attr:`.HardwareContext.NONE` to revert to software rendering.
        The driver won't be reinitialized until the next call to :meth:`.reinit`.

        :param callback: A :class:`.retro_hw_render_callback` with the context parameters
            requested by the core,
            plus callbacks to run at certain points in the context's lifecycle.

        :return: If ``callback`` is accepted,
          a new :class:`.retro_hw_render_callback` with values and pointers
          that the core can use to interact with the hardware context.
          Otherwise, :obj:`None`.

        :raises TypeError: If ``callback`` is not a :class:`.retro_hw_render_callback`.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_HW_RENDER``.
        """
        ...

    @property
    @abstractmethod
    def current_framebuffer(self) -> int | None:
        """
        The current framebuffer for the active graphics context.
        The core should use this framebuffer when rendering to the screen.
        Software-rendered graphics will be drawn to this framebuffer.

        :return: An integer identifier for the current framebuffer,
            or :obj:`None` if the driver doesn't support or need this feature.

        .. note::

            Corresponds to :attr:`.retro_hw_render_callback.get_current_framebuffer`.

            This property is generally only used by OpenGL and OpenGL ES,
            but it's part of the general :class:`.retro_hw_render_callback` structure
            for historical reasons.
        """
        ...

    @abstractmethod
    def get_proc_address(self, sym: bytes) -> int | None:
        """
        Returns the address of the graphics API function with the given name.

        :param sym: The name of the function to look up.
        :return: The address of the function if found, :obj:`None` otherwise.
            Will also return :obj:`None` if the driver doesn't support or need this feature.
        :raises TypeError: If ``sym`` is not a :class:`bytes`.

        .. note::

            Corresponds to :attr:`.retro_hw_render_callback.get_proc_address`.

            This property is generally only used by OpenGL and OpenGL ES,
            but it's part of the general :class:`.retro_hw_render_callback` structure
            for historical reasons.
        """
        ...

    @property
    @abstractmethod
    def rotation(self) -> Rotation:
        """
        The angle by which the output should be rotated,
        in increments of 90 degrees.

        If the video driver doesn't support rotation,
        then this property will always return :attr:`.Rotation.NONE`.

        :raise NotImplementedError: If setting or deleting this property
          on a :class:`.VideoDriver` that doesn't support doing so.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_ROTATION``.
        """
        ...

    @rotation.setter
    @abstractmethod
    def rotation(self, rotation: Rotation) -> None: ...

    @property
    @abstractmethod
    def can_dupe(self) -> bool | None:
        """
        Whether the frontend can re-render the previous frame.

        :obj:`True` if frame duping is supported,
        :obj:`False` if not.

        If :obj:`None`, then ``RETRO_ENVIRONMENT_GET_CAN_DUPE`` is unavailable to cores.

        :raise NotImplementedError: If setting or deleting this property
          on a :class:`.VideoDriver` that doesn't support doing so.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_GET_CAN_DUPE``.
        """
        ...

    @can_dupe.setter
    @abstractmethod
    def can_dupe(self, value: bool) -> None: ...

    @can_dupe.deleter
    @abstractmethod
    def can_dupe(self) -> None: ...

    @property
    @abstractmethod
    def pixel_format(self) -> PixelFormat:
        """
        The pixel format that this driver uses for its frame buffer.
        If a driver doesn't support setting the pixel format,
        then this property will always return :attr:`.PixelFormat.RGB1555`.

        :raise TypeError: If trying to set a value that isn't a :class:`.PixelFormat`.
        :raise NotImplementedError: If setting this property
            on a driver that doesn't support :attr:`.EnvironmentCall.SET_PIXEL_FORMAT`.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_PIXEL_FORMAT``.
        """
        ...

    @pixel_format.setter
    @abstractmethod
    def pixel_format(self, format: PixelFormat) -> None: ...

    @property
    @abstractmethod
    def system_av_info(self) -> retro_system_av_info | None:
        """
        The system AV info for the current session.
        May be :obj:`None` if not yet set.

        Initialized from :meth:`.Core.get_system_av_info` some time after this driver is created.
        After being set, this video driver is immediately reinitialized if necessary.

        :raise TypeError: If trying to set a value that isn't a :class:`.retro_system_av_info`.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO``.

            The getter will return a copy of the driver's :class:`.retro_system_av_info` object
            to avoid accidental modification of the original.
        """
        ...

    @system_av_info.setter
    @abstractmethod
    def system_av_info(self, av_info: retro_system_av_info) -> None: ...

    @property
    @abstractmethod
    def geometry(self) -> retro_game_geometry | None:
        """
        The active screen geometry.
        May be :obj:`None` if :attr:`~.VideoDriver.system_av_info` hasn't been set yet.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_GEOMETRY``.

            The getter will return a copy of the driver's :class:`.retro_game_geometry` object
            to avoid accidental modification of the original.

        .. caution::

            When setting this property, this driver's values of
            :attr:`.retro_game_geometry.max_width` and :attr:`.retro_game_geometry.max_height`
            are **not** updated.

            libretro.h guarantees that ``RETRO_ENVIRONMENT_SET_GEOMETRY`` will complete in constant time
            without needing to reinitialize the driver;
            this may not be possible if the driver's framebuffer needs to be reallocated.
        """
        ...

    @geometry.setter
    @abstractmethod
    def geometry(self, geometry: retro_game_geometry) -> None: ...

    @abstractmethod
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        """
        Returns a framebuffer of the given size,
        usually (but not necessarily) mapped directly into GPU memory.
        Can be used to accelerate software rendering,
        as data doesn't need to be copied between the core and the GPU.

        :param width: The width of the framebuffer, in pixels.
        :param height: The height of the framebuffer, in pixels.
        :param flags: Flags that describe how the core will access the framebuffer.

        :return: A :class:`.retro_framebuffer` object with the requested properties,
            or :obj:`None` if not supported by this :class:`.VideoDriver`.

        :raises ValueError: If the framebuffer's width or height is less than 1.
        :raises TypeError: If any parameter's type is not consistent with this method's signature.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER``.
        """
        ...

    @property
    @abstractmethod
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        """
        Returns a :class:`.retro_hw_render_interface` subclass that can be used
        for rendering operations specific to this :class:`.VideoDriver`.

        Will be :obj:`None` if not supported or needed by this driver.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE``.
        """
        ...

    @property
    @abstractmethod
    def shared_context(self) -> bool:
        """
        Whether to create a shared hardware context.
        Takes effect the next time the driver is reinitialized.

        .. note::

            Corresponds to ``RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT``.

            This property is generally only used by OpenGL and OpenGL ES,
            but it has its own environment call
            for historical reasons.
        """
        ...

    @shared_context.setter
    @abstractmethod
    def shared_context(self, value: bool) -> None: ...

    @abstractmethod
    def screenshot(self, prerotate: bool = True) -> Screenshot | None:
        """
        Captures the part of the most recently-rendered frame
        that would be visible to the player
        in a typical libretro frontend.

        This should account for rotation, geometry dimensions, and aspect ratio.

        :param prerotate:
            :obj:`True` if this method should rotate the output buffer's contents
            according to :attr:`~.VideoDriver.rotation`,
            :obj:`False` if it should be left to the frontend.
        """
        ...


__all__ = [
    "VideoDriver",
    "FrameBufferSpecial",
    "Screenshot",
]
