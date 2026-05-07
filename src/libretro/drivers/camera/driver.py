"""
:class:`~typing.Protocol` definition for emulated camera input drivers.

.. seealso::

    :mod:`libretro.api.camera`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.camera import (
    CameraCapabilityFlags,
    retro_camera_frame_opengl_texture_t,
    retro_camera_frame_raw_framebuffer_t,
    retro_camera_lifetime_status_t,
)


@runtime_checkable
class CameraDriver(Protocol):
    """
    Protocol for drivers that supply emulated camera input frames.

    .. seealso::

        :mod:`libretro.api.camera`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def caps(self) -> CameraCapabilityFlags:
        """
        The camera capabilities requested by the core.

        Set from the ``caps`` field of the :class:`.retro_camera_callback`
        registered via ``RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE``.

        :param value: The capability flags requested by the core.

        .. seealso::

            :class:`~libretro.api.camera.CameraCapabilityFlags`
                Bit flags describing which buffer formats the driver must support.
        """
        ...

    @caps.setter
    @abstractmethod
    def caps(self, value: CameraCapabilityFlags) -> None:
        """See :attr:`caps`."""
        ...

    @abstractmethod
    def start(self) -> bool:
        """
        Begin capturing frames from the emulated camera.

        Called by the core through the :attr:`.retro_camera_callback.start`
        function pointer when it wants the camera to start producing frames.

        :return: :obj:`True` if the camera started successfully, :obj:`False` otherwise.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_start_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """
        Stop capturing frames from the emulated camera.

        Called by the core through the :attr:`.retro_camera_callback.stop`
        function pointer when it no longer needs camera input.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_stop_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def poll(self) -> None:
        """
        Advance the camera by one frame, delivering any newly available frame to the core.

        Called once per frame by the session before :meth:`.Core.run`,
        so that any pending frame is dispatched
        through :attr:`frame_raw_framebuffer` or :attr:`frame_opengl_texture`.
        """
        ...

    @property
    @abstractmethod
    def width(self) -> int:
        """
        The width of camera frames in pixels, as requested by the core.

        A value of ``0`` lets the driver pick its preferred width.
        Set from the ``width`` field of the :class:`.retro_camera_callback`.

        :param value: The frame width in pixels requested by the core.
        """
        ...

    @width.setter
    @abstractmethod
    def width(self, value: int) -> None:
        """See :attr:`width`."""
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        """
        The height of camera frames in pixels, as requested by the core.

        A value of ``0`` lets the driver pick its preferred height.
        Set from the ``height`` field of the :class:`.retro_camera_callback`.

        :param value: The frame height in pixels requested by the core.
        """
        ...

    @height.setter
    @abstractmethod
    def height(self, value: int) -> None:
        """See :attr:`height`."""
        ...

    @property
    @abstractmethod
    def frame_raw_framebuffer(self) -> retro_camera_frame_raw_framebuffer_t | None:
        """
        Callback the driver invokes to deliver a frame backed by a raw framebuffer.

        Registered by the core through
        :attr:`.retro_camera_callback.frame_raw_framebuffer`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke for raw framebuffer frames,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_frame_raw_framebuffer_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @frame_raw_framebuffer.setter
    @abstractmethod
    def frame_raw_framebuffer(self, value: retro_camera_frame_raw_framebuffer_t | None) -> None:
        """See :attr:`frame_raw_framebuffer`."""
        ...

    @property
    @abstractmethod
    def frame_opengl_texture(self) -> retro_camera_frame_opengl_texture_t | None:
        """
        Callback the driver invokes to deliver a frame backed by an OpenGL texture.

        Registered by the core through
        :attr:`.retro_camera_callback.frame_opengl_texture`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke for OpenGL texture frames,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_frame_opengl_texture_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @frame_opengl_texture.setter
    @abstractmethod
    def frame_opengl_texture(self, value: retro_camera_frame_opengl_texture_t | None) -> None:
        """See :attr:`frame_opengl_texture`."""
        ...

    @property
    @abstractmethod
    def initialized(self) -> retro_camera_lifetime_status_t | None:
        """
        Callback the driver invokes after it finishes initializing.

        Registered by the core through :attr:`.retro_camera_callback.initialized`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke after initialization,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_lifetime_status_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @initialized.setter
    @abstractmethod
    def initialized(self, value: retro_camera_lifetime_status_t | None) -> None:
        """See :attr:`initialized`."""
        ...

    @property
    @abstractmethod
    def deinitialized(self) -> retro_camera_lifetime_status_t | None:
        """
        Callback the driver invokes immediately before it deinitializes.

        Registered by the core through :attr:`.retro_camera_callback.deinitialized`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke before deinitialization,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.camera.retro_camera_lifetime_status_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @deinitialized.setter
    @abstractmethod
    def deinitialized(self, value: retro_camera_lifetime_status_t | None) -> None:
        """See :attr:`deinitialized`."""
        ...


__all__ = ["CameraDriver"]
