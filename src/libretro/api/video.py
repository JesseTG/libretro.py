from abc import abstractmethod
from array import array
from ctypes import *
from typing import Protocol, runtime_checkable, final

from ..retro import *
from ..defs import PixelFormat


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
            self._frame = array(self._pixel_format.typecode, [0] * (pitch * height))

        # Copy the data into the frame
        memmove(self._frame.buffer_info()[0], data, pitch * height)