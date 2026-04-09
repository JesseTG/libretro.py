from typing import override

from libretro.api.camera import (
    CameraCapabilityFlags,
    retro_camera_frame_opengl_texture_t,
    retro_camera_frame_raw_framebuffer_t,
    retro_camera_lifetime_status_t,
)

from .driver import CameraDriver


class CameraFrame:
    pass
    # TODO: Add a buffer
    # TODO: Add dimensions


class IterableCameraDriver(CameraDriver):
    def __init__(self):
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def caps(self) -> CameraCapabilityFlags:
        raise NotImplementedError("Will be implemented later")

    @caps.setter
    @override
    def caps(self, value: CameraCapabilityFlags) -> None:
        raise NotImplementedError("Will be implemented later")

    @override
    def start(self) -> bool:
        raise NotImplementedError("Will be implemented later")

    @override
    def stop(self) -> None:
        raise NotImplementedError("Will be implemented later")

    @override
    def poll(self) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def width(self) -> int:
        raise NotImplementedError("Will be implemented later")

    @width.setter
    @override
    def width(self, value: int) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def height(self) -> int:
        raise NotImplementedError("Will be implemented later")

    @height.setter
    @override
    def height(self, value: int) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def frame_raw_framebuffer(self) -> retro_camera_frame_raw_framebuffer_t | None:
        raise NotImplementedError("Will be implemented later")

    @frame_raw_framebuffer.setter
    @override
    def frame_raw_framebuffer(self, value: retro_camera_frame_raw_framebuffer_t | None) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def frame_opengl_texture(self) -> retro_camera_frame_opengl_texture_t | None:
        raise NotImplementedError("Will be implemented later")

    @frame_opengl_texture.setter
    @override
    def frame_opengl_texture(self, value: retro_camera_frame_opengl_texture_t | None) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def initialized(self) -> retro_camera_lifetime_status_t | None:
        raise NotImplementedError("Will be implemented later")

    @initialized.setter
    @override
    def initialized(self, value: retro_camera_lifetime_status_t | None) -> None:
        raise NotImplementedError("Will be implemented later")

    @property
    @override
    def deinitialized(self) -> retro_camera_lifetime_status_t | None:
        raise NotImplementedError("Will be implemented later")

    @deinitialized.setter
    @override
    def deinitialized(self, value: retro_camera_lifetime_status_t | None) -> None:
        raise NotImplementedError("Will be implemented later")


__all__ = [
    "IterableCameraDriver",
]
