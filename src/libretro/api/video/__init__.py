from abc import abstractmethod
from array import array
from enum import IntEnum
from ctypes import *
from typing import Protocol, runtime_checkable, final

from ..system import retro_system_av_info, retro_game_geometry
from ...h import *
from ...retro import FieldsFromTypeHints

retro_video_refresh_t = CFUNCTYPE(None, c_void_p, c_uint, c_uint, c_size_t)

retro_usec_t = c_int64
retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)


class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t


class Rotation(IntEnum):
    NONE = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3

    def __init__(self, value):
        self._type_ = 'I'


class PixelFormat(IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    def __init__(self, value):
        self._type_ = 'I'

    @property
    def bytes_per_pixel(self) -> int:
        match self:
            case self.RGB1555:
                return 2
            case self.XRGB8888:
                return 4
            case self.RGB565:
                return 2
            case _:
                raise ValueError(f"Unknown pixel format: {self}")

class retro_framebuffer(Structure, metaclass=FieldsFromTypeHints):
    data: c_void_p
    width: c_uint
    height: c_uint
    pitch: c_size_t
    format: retro_pixel_format
    access_flags: c_uint
    memory_flags: c_uint

@runtime_checkable
class VideoCallbacks(Protocol):
    @abstractmethod
    def refresh(self, data: c_void_p, width: int, height: int, pitch: int) -> None: ...


@runtime_checkable
class VideoState(VideoCallbacks, Protocol):
    @abstractmethod
    def set_rotation(self, rotation: int) -> bool: ...

    @abstractmethod
    def can_dupe(self) -> bool: ...

    @abstractmethod
    def set_pixel_format(self, format: PixelFormat) -> bool: ...

    @abstractmethod
    def set_system_av_info(self, av_info: retro_system_av_info) -> None: ...

    @abstractmethod
    def set_geometry(self, geometry: retro_game_geometry) -> None: ...


@final
class SoftwareVideoState(VideoState):
    def __init__(self):
        self._frame: array | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None

    @property
    def frame(self) -> array | None:
        return self._frame

    def set_rotation(self, rotation: int) -> bool:
        return False # TODO: Implement

    def can_dupe(self) -> bool:
        return True

    def set_pixel_format(self, format: PixelFormat) -> bool:
        if not isinstance(format, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(format)}")

        if self._pixel_format != format:
            self._frame = None

        self._pixel_format = format
        return True

    def set_system_av_info(self, av_info: retro_system_av_info) -> None:
        system_av_info = retro_system_av_info(av_info)
        geometry: retro_game_geometry = system_av_info.geometry
        if not self._system_av_info or self._system_av_info.geometry.max_width != geometry.max_width \
                or self._system_av_info.geometry.max_height != geometry.max_height:
            self._system_av_info = system_av_info
            self._frame = None

    def set_geometry(self, geometry: retro_game_geometry) -> None:
        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio

    def refresh(self, data: c_void_p, width: int, height: int, pitch: int) -> None:
        if not self._frame or self._frame.buffer_info()[1] * self._frame.itemsize != pitch * height:
            # If we don't have a frame or the frame is not the right size, create a new one
            self._frame = array('B', [0] * (pitch * height))

        # Copy the data into the frame
        memmove(self._frame.buffer_info()[0], data, pitch * height)