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
    @property
    @abstractmethod
    def caps(self) -> CameraCapabilityFlags: ...

    @caps.setter
    @abstractmethod
    def caps(self, value: CameraCapabilityFlags) -> None: ...

    @abstractmethod
    def start(self) -> bool: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def poll(self) -> None: ...

    @property
    @abstractmethod
    def width(self) -> int: ...

    @width.setter
    @abstractmethod
    def width(self, value: int) -> None: ...

    @property
    @abstractmethod
    def height(self) -> int: ...

    @height.setter
    @abstractmethod
    def height(self, value: int) -> None: ...

    @property
    @abstractmethod
    def frame_raw_framebuffer(self) -> retro_camera_frame_raw_framebuffer_t | None: ...

    @frame_raw_framebuffer.setter
    @abstractmethod
    def frame_raw_framebuffer(
        self, value: retro_camera_frame_raw_framebuffer_t | None
    ) -> None: ...

    @property
    @abstractmethod
    def frame_opengl_texture(self) -> retro_camera_frame_opengl_texture_t | None: ...

    @frame_opengl_texture.setter
    @abstractmethod
    def frame_opengl_texture(self, value: retro_camera_frame_opengl_texture_t | None) -> None: ...

    @property
    @abstractmethod
    def initialized(self) -> retro_camera_lifetime_status_t | None: ...

    @initialized.setter
    @abstractmethod
    def initialized(self, value: retro_camera_lifetime_status_t | None) -> None: ...

    @property
    @abstractmethod
    def deinitialized(self) -> retro_camera_lifetime_status_t | None: ...

    @deinitialized.setter
    @abstractmethod
    def deinitialized(self, value: retro_camera_lifetime_status_t | None) -> None: ...


__all__ = ["CameraDriver"]
