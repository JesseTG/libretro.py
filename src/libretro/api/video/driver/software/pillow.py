import math
from copy import deepcopy
from typing import final

import PIL.Image
from PIL.Image import Image

from .base import AbstractSoftwareVideoDriver
from ...defs import MemoryAccess, retro_framebuffer, PixelFormat, Rotation
from ....av import retro_game_geometry, retro_system_av_info


@final
class PillowVideoDriver(AbstractSoftwareVideoDriver):
    def __init__(self):
        self._framebuffer: Image | None = None
        self._rotation: Rotation = Rotation.NONE
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._should_reinit_framebuffer = True

    def _refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        if self._should_reinit_framebuffer:
            self.__reinit_framebuffer()

        if data:
            pillow_mode = self._pixel_format.pillow_mode
            image = PIL.Image.frombuffer(pillow_mode, (width, height), data, "raw", pillow_mode, 0, 1)
            # TODO: Rotate image if needed

            self._framebuffer.paste(image)

    def get_rotation(self) -> Rotation:
        return self._rotation

    def set_rotation(self, rotation: Rotation) -> bool:
        if not isinstance(rotation, Rotation):
            raise TypeError(f"Expected a Rotation, got {type(rotation).__name__}")

        if rotation not in Rotation:
            raise ValueError(f"Invalid rotation: {rotation}")

        #self._rotation = rotation
        return False

    @property
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    def pixel_format(self, format: PixelFormat) -> None:
        if format not in PixelFormat:
            raise ValueError(f"Invalid pixel format: {format}")

        if not isinstance(format, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(format).__name__}")

        if not self._framebuffer or self._pixel_format != format:
            # If we haven't initialized the frame buffer yet, or if the pixel format has changed...
            self._pixel_format = format
            self._should_reinit_framebuffer = True

    def get_system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info) if self._system_av_info else None

    def set_system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        if not self._framebuffer or not self._system_av_info or self._system_av_info.geometry != av_info.geometry:
            # If we haven't initialized the system AV info yet, or if the geometry has changed...
            self._should_reinit_framebuffer = True

        self._system_av_info = deepcopy(av_info)

    def set_geometry(self, geometry: retro_game_geometry) -> None:
        if not isinstance(geometry, retro_game_geometry):
            raise TypeError(f"Expected a retro_game_geometry, got {type(geometry).__name__}")

        if not self._system_av_info:
            raise RuntimeError("Cannot set geometry until system AV info is initialized")

        if geometry.base_width > self._system_av_info.geometry.max_width:
            raise ValueError(f"Base width {geometry.base_width} exceeds max width {self._system_av_info.geometry.max_width}")

        if geometry.base_height > self._system_av_info.geometry.max_height:
            raise ValueError(f"Base height {geometry.base_height} exceeds max height {self._system_av_info.geometry.max_height}")

        if not math.isfinite(float(geometry.aspect_ratio)):
            raise ValueError(f"Invalid aspect ratio: {geometry.aspect_ratio}")

        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio
        # TODO: Recompute aspect ratio

    def get_geometry(self) -> retro_game_geometry:
        if not self._system_av_info:
            raise RuntimeError("Cannot get geometry until system AV info is initialized")

        return deepcopy(self._system_av_info.geometry)

    def get_software_framebuffer(self, width: int, height: int, flags: MemoryAccess) -> retro_framebuffer | None:
        return None  # TODO: Implement

    def get_frame(self) -> Image:
        if not self._system_av_info or not self._framebuffer:
            raise RuntimeError("Cannot get frame until system AV info is initialized")

        geometry = self._system_av_info.geometry
        cropped = self._framebuffer.crop((0, 0, int(geometry.base_width), int(geometry.base_height)))
        r, g, b, _ = cropped.split()

        return PIL.Image.merge("RGB", (b, g, r))
        # TODO: Optimize get_frame!

    def get_frame_max(self) -> Image:
        if not self._system_av_info or not self._framebuffer:
            raise RuntimeError("Cannot get framebuffer until system AV info is initialized")

        r, g, b, _ = self._framebuffer.split()

        return PIL.Image.merge("RGB", (b, g, r))
        # TODO: Optimize get_frame_max!

    def __reinit_framebuffer(self):
        if not self._should_reinit_framebuffer:
            return

        size = (int(self._system_av_info.geometry.max_width), int(self._system_av_info.geometry.max_height))
        self._framebuffer = PIL.Image.new(self._pixel_format.pillow_mode, size)
        self._should_reinit_framebuffer = False


__all__ = [
    "PillowVideoDriver",
]
