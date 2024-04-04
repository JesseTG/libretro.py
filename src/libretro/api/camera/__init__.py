from ctypes import *

from ..._utils import FieldsFromTypeHints

retro_camera_start_t = CFUNCTYPE(c_bool, )
retro_camera_stop_t = CFUNCTYPE(None, )
retro_camera_lifetime_status_t = CFUNCTYPE(None, )
retro_camera_frame_raw_framebuffer_t = CFUNCTYPE(None, POINTER(c_uint32), c_uint, c_uint, c_size_t)
retro_camera_frame_opengl_texture_t = CFUNCTYPE(None, c_uint, c_uint, POINTER(c_float))


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


__all__ = [
    'retro_camera_start_t',
    'retro_camera_stop_t',
    'retro_camera_lifetime_status_t',
    'retro_camera_frame_raw_framebuffer_t',
    'retro_camera_frame_opengl_texture_t',
    'retro_camera_callback',
]
