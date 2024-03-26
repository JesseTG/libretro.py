from array import array
from copy import deepcopy
from ctypes import memmove
from typing import final

from .base import AbstractSoftwareVideoDriver
from ...defs import MemoryAccess, Rotation, retro_framebuffer, PixelFormat
from ....av.defs import retro_system_av_info, retro_game_geometry


@final
class ArrayVideoDriver(AbstractSoftwareVideoDriver):




    def __init__(self):
        self._frame: array | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._recreate_frame = True

    def _refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        # TODO: Recreate the frame buffer based on the pixel format and system AV info
        if not self._frame or self._frame.buffer_info()[1] * self._frame.itemsize != pitch * height:
            # If we don't have a frame or the frame is not the right size, create a new one
            self._frame = array('B', [0] * (pitch * height))

        # Copy the data into the frame
        memmove(self._frame.buffer_info()[0], data, pitch * height)

    def get_pixel_format(self) -> PixelFormat:
        pass

    def set_pixel_format(self, format: PixelFormat) -> bool:
        pass

    def get_frame(self):
        pass

    @property
    def get_frame_max(self):
        pass

    def get_system_av_info(self) -> retro_system_av_info | None:
        pass

    def get_geometry(self) -> retro_game_geometry:
        pass

    def get_software_framebuffer(self, width: int, height: int, flags: MemoryAccess) -> retro_framebuffer | None:
        pass

    def set_rotation(self, rotation: Rotation) -> bool:
        return False

    def get_rotation(self) -> Rotation:
        return Rotation.NONE

    def set_system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info)}")

        system_av_info = deepcopy(av_info)
        geometry: retro_game_geometry = system_av_info.geometry
        if not self._system_av_info or self._system_av_info.geometry.max_width != geometry.max_width \
                or self._system_av_info.geometry.max_height != geometry.max_height:
            self._system_av_info = system_av_info
            self._frame = None

        # TODO: Recreate the frame buffer

    def set_geometry(self, geometry: retro_game_geometry) -> None:
        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio

        # TODO: Recreate the frame buffer


__all__ = ['ArrayVideoDriver']
