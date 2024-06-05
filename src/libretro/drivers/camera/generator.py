from libretro._typing import override

from ... import (
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


class GeneratorCameraDriver(CameraDriver):
    @override
    def __init__(self):
        super().__init__()

        # TODO: Accept a generator for camera frames

    @property
    def caps(self) -> CameraCapabilityFlags:
        pass

    def start(self) -> bool:
        pass

    def stop(self) -> None:
        pass

    def poll(self) -> None:
        pass

    @property
    def width(self) -> int:
        pass

    @property
    def height(self) -> int:
        pass

    @property
    def frame_raw_framebuffer(self) -> retro_camera_frame_raw_framebuffer_t | None:
        pass

    @property
    def frame_opengl_texture(self) -> retro_camera_frame_opengl_texture_t | None:
        pass

    @property
    def initialized(self) -> retro_camera_lifetime_status_t | None:
        pass

    @property
    def deinitialized(self) -> retro_camera_lifetime_status_t | None:
        pass


__all__ = [
    "GeneratorCameraDriver",
]
