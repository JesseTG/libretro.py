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
retro_camera_stop_t = TypedFunctionPointer[None, []]
retro_camera_lifetime_status_t = TypedFunctionPointer[None, []]
retro_camera_frame_raw_framebuffer_t = TypedFunctionPointer[
    None, [TypedPointer[c_uint32], CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_size_t]]
]
retro_camera_frame_opengl_texture_t = TypedFunctionPointer[
    None, [CIntArg[c_uint], CIntArg[c_uint], TypedPointer[c_float]]
]


class CameraCapabilities(IntEnum):
    OPENGL_TEXTURE = RETRO_CAMERA_BUFFER_OPENGL_TEXTURE
    RAW_FRAMEBUFFER = RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER

    def flag(self) -> int:
        return 1 << self.value


class CameraCapabilityFlags(IntFlag):
    OPENGL_TEXTURE = 1 << CameraCapabilities.OPENGL_TEXTURE
    RAW_FRAMEBUFFER = 1 << CameraCapabilities.RAW_FRAMEBUFFER


@dataclass(init=False, slots=True)
class retro_camera_callback(Structure):
    caps: int
    width: int
    height: int
    start: retro_camera_start_t | None
    stop: retro_camera_stop_t | None
    frame_raw_framebuffer: retro_camera_frame_raw_framebuffer_t | None
    frame_opengl_texture: retro_camera_frame_opengl_texture_t | None
    initialized: retro_camera_lifetime_status_t | None
    deinitialized: retro_camera_lifetime_status_t | None

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
