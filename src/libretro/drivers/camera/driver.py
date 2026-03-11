from abc import abstractmethod
from typing import Protocol, runtime_checkable
from warnings import deprecated

from libretro.api.camera import (
    CameraCapabilityFlags,
    retro_camera_callback,
    retro_camera_frame_opengl_texture_t,
    retro_camera_frame_raw_framebuffer_t,
    retro_camera_lifetime_status_t,
    retro_camera_start_t,
    retro_camera_stop_t,
)


@runtime_checkable
class CameraDriver(Protocol):
    @property
    @deprecated(
        "Set the function pointers in the EnvironmentDriver instead of in the CameraDriver"
    )
    @abstractmethod
    def _as_parameter_(self) -> retro_camera_callback:
        return retro_camera_callback(
            caps=self.caps,
            width=self.width,
            height=self.height,
            start=retro_camera_start_t(self.start),
            stop=retro_camera_stop_t(self.stop),
            frame_raw_framebuffer=self.frame_raw_framebuffer,
            frame_opengl_texture=self.frame_opengl_texture,
            initialized=self.initialized,
            deinitialized=self.deinitialized,
        )

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
    def frame_raw_framebuffer(self, value: retro_camera_frame_raw_framebuffer_t) -> None: ...

    @property
    @abstractmethod
    def frame_opengl_texture(self) -> retro_camera_frame_opengl_texture_t | None: ...

    @frame_opengl_texture.setter
    @abstractmethod
    def frame_opengl_texture(self, value: retro_camera_frame_opengl_texture_t) -> None: ...

    @property
    @abstractmethod
    def initialized(self) -> retro_camera_lifetime_status_t | None: ...

    @initialized.setter
    @abstractmethod
    def initialized(self, value: retro_camera_lifetime_status_t) -> None: ...

    @property
    @abstractmethod
    def deinitialized(self) -> retro_camera_lifetime_status_t | None: ...

    @deinitialized.setter
    @abstractmethod
    def deinitialized(self, value: retro_camera_lifetime_status_t) -> None: ...


__all__ = ["CameraDriver"]
