from ctypes import (
    CFUNCTYPE,
    POINTER,
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

from libretro.api._utils import FieldsFromTypeHints

retro_camera_buffer = c_int
RETRO_CAMERA_BUFFER_OPENGL_TEXTURE = 0
RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER = RETRO_CAMERA_BUFFER_OPENGL_TEXTURE + 1
RETRO_CAMERA_BUFFER_DUMMY = 0x7FFFFFFF


retro_camera_start_t = CFUNCTYPE(c_bool)
retro_camera_stop_t = CFUNCTYPE(None)
retro_camera_lifetime_status_t = CFUNCTYPE(None)
retro_camera_frame_raw_framebuffer_t = CFUNCTYPE(None, POINTER(c_uint32), c_uint, c_uint, c_size_t)
retro_camera_frame_opengl_texture_t = CFUNCTYPE(None, c_uint, c_uint, POINTER(c_float))


class CameraCapabilities(IntEnum):
    OPENGL_TEXTURE = RETRO_CAMERA_BUFFER_OPENGL_TEXTURE
    RAW_FRAMEBUFFER = RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER

    def flag(self) -> int:
        return 1 << self.value


class CameraCapabilityFlags(IntFlag):
    OPENGL_TEXTURE = 1 << CameraCapabilities.OPENGL_TEXTURE
    RAW_FRAMEBUFFER = 1 << CameraCapabilities.RAW_FRAMEBUFFER


@dataclass(init=False)
class retro_camera_callback(Structure, metaclass=FieldsFromTypeHints):
    caps: c_uint64
    width: c_uint
    height: c_uint
    start: retro_camera_start_t
    stop: retro_camera_stop_t
    frame_raw_framebuffer: retro_camera_frame_raw_framebuffer_t
    frame_opengl_texture: retro_camera_frame_opengl_texture_t
    initialized: retro_camera_lifetime_status_t
    deinitialized: retro_camera_lifetime_status_t

    def __deepcopy__(self, _):
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
