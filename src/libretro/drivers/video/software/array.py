from array import array
from copy import deepcopy
from typing import final, override

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.video import MemoryAccess, PixelFormat, Rotation, retro_framebuffer
from libretro.error import UnsupportedEnvCall

from .base import AbstractSoftwareVideoDriver


@final
class ArrayVideoDriver(AbstractSoftwareVideoDriver):
    def __init__(self):
        self._frame: array | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._recreate_frame = True

    @override
    def refresh(
        self, data: memoryview | None, width: int, height: int, pitch: int
    ) -> None:
        if self._recreate_frame:
            # If we don't have a frame or the frame is not the right size, create a new one
            if not self._system_av_info:
                raise RuntimeError("System AV info is not set")

            geometry = self._system_av_info.geometry
            bufsize = (
                geometry.max_width
                * geometry.max_height
                * self._pixel_format.bytes_per_pixel
            )
            self._frame = array("B", [0] * bufsize)
            self._recreate_frame = False

        if data:
            frameview = memoryview(self._frame)
            max_width = self._system_av_info.geometry.max_width
            for i in range(height):
                # For each row of the frame to render...
                frame_start_offset = max_width * self._pixel_format.bytes_per_pixel * i
                frameview[frame_start_offset : frame_start_offset + pitch] = data[
                    pitch * i : pitch * i + pitch
                ]

    @property
    @override
    def rotation(self) -> Rotation:
        return Rotation.NONE

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        raise UnsupportedEnvCall("Rotation is not supported")

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, format: PixelFormat) -> None:
        if format not in PixelFormat:
            raise ValueError(f"Invalid pixel format: {format}")

        if not isinstance(format, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(format).__name__}")

        if self._pixel_format != format:
            # If the pixel format has changed, recreate the frame buffer
            self._recreate_frame = True

        self._pixel_format = format

    @property
    @override
    def frame(self) -> array | None:
        if not self._frame:
            return None

        frame = array("B")
        width = int(self._system_av_info.geometry.base_width)
        height = int(self._system_av_info.geometry.base_height)
        max_width = self._system_av_info.geometry.max_width
        for i in range(height):
            frame_offset = max_width * i * self._pixel_format.bytes_per_pixel
            row = self._frame[
                frame_offset : frame_offset + width * self._pixel_format.bytes_per_pixel
            ]
            frame.frombytes(row)

        return frame

    @property
    @override
    def frame_max(self):
        return (
            array(self._pixel_format.pixel_typecode, self._frame)
            if self._frame
            else None
        )

    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        pass

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info) if self._system_av_info else None

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(
                f"Expected a retro_system_av_info, got {type(av_info).__name__}"
            )

        geometry: retro_game_geometry = av_info.geometry
        if (
            not self._system_av_info
            or self._system_av_info.geometry.max_width != geometry.max_width
            or self._system_av_info.geometry.max_height != geometry.max_height
        ):
            self._system_av_info = deepcopy(av_info)
            self._recreate_frame = True

    @property
    @override
    def geometry(self) -> retro_game_geometry:
        return deepcopy(self._system_av_info.geometry)

    @geometry.setter
    @override
    def geometry(self, geometry: retro_game_geometry) -> None:
        if not isinstance(geometry, retro_game_geometry):
            raise TypeError(
                f"Expected a retro_game_geometry, got {type(geometry).__name__}"
            )
        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio


__all__ = ["ArrayVideoDriver"]
