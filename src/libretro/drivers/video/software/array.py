import itertools
from array import array
from copy import deepcopy
from typing import final
from warnings import warn

import numpy as np

from libretro._typing import override
from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.video import MemoryAccess, PixelFormat, Rotation, retro_framebuffer

from ..driver import FrameBufferSpecial, Screenshot
from .base import SoftwareVideoDriver


@final
class ArrayVideoDriver(SoftwareVideoDriver):
    def __init__(self):
        self._frame: array | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._rotation: Rotation = Rotation.NONE
        self._last_width: int | None = None
        self._last_height: int | None = None
        self._last_pitch: int | None = None

        # Preallocate buffers
        self.screen_out = None
        self.pixel_buf = np.array([0, 0, 0, 255], dtype=np.uint8)

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        match data:
            case memoryview():
                if self._frame is None or len(data) > len(self._frame):
                    # Reallocate frame buffer
                    self._frame = array("B", itertools.repeat(0, len(data)))
                frameview = memoryview(self._frame)
                frameview[: len(data)] = data

            case FrameBufferSpecial.DUPE:
                pass  # Do nothing

            case FrameBufferSpecial.HARDWARE:
                warn("RETRO_HW_FRAME_BUFFER_VALID passed to software-only video refresh callback")

            case _:
                raise TypeError(
                    f"Expected a memoryview or a FrameBufferSpecial, got {type(data).__name__}"
                )

        self._last_width = width
        self._last_height = height
        self._last_pitch = pitch

    @override
    @property
    def needs_reinit(self) -> bool:
        return self._frame is None

    @override
    def reinit(self) -> None:
        geometry = self._system_av_info.geometry
        bufsize = geometry.max_width * geometry.max_height * self._pixel_format.bytes_per_pixel
        self._frame = array("B", itertools.repeat(0, bufsize))
        self.screen_out = np.zeros((self._last_height or 0, self._last_width or 0, 4), dtype=np.uint8)

    @property
    @override
    def rotation(self) -> Rotation:
        return self._rotation

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        if not isinstance(rotation, Rotation):
            raise TypeError(f"Expected a Rotation, got {type(rotation).__name__}")

        if rotation not in Rotation:
            raise ValueError(f"Invalid rotation: {rotation}")

        self._rotation = rotation

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
            self._frame = None
            self.screen_out = None

        self._pixel_format = format

    @override
    def screenshot(self, prerotate: bool = True) -> Screenshot | None:
        if not self._frame:
            return None

        last_frame_length = self._last_pitch * self._last_height
        screen = np.frombuffer(self._frame, dtype=np.uint8, count=last_frame_length).reshape((self._last_height, self._last_width, -1))

        # Perform rotation if needed
        if prerotate and self._rotation != Rotation.NONE:
            k = self._rotation.value // 90
            screen = np.rot90(screen, k=k)

        # Pixel format conversion
        match self._pixel_format:
            case PixelFormat.XRGB8888:
                # Convert XRGB8888 to RGBA
                screen_out = screen[:, :, [2, 1, 0, 3]]
            case PixelFormat.RGB565:
                # Convert RGB565 to RGBA
                r = ((screen[:, :, 1] & 0xF8)).astype(np.uint8)
                g = (((screen[:, :, 0] & 0xE0) >> 3) | ((screen[:, :, 1] & 0x07) << 5)).astype(np.uint8)
                b = ((screen[:, :, 0] & 0x1F) << 3).astype(np.uint8)
                a = np.full_like(r, 255, dtype=np.uint8)
                screen_out = np.stack((r, g, b, a), axis=-1)
            case PixelFormat.RGB1555:
                # Convert RGB1555 to RGBA
                r = ((screen[:, :, 1] & 0xF8) | (screen[:, :, 1] >> 5)).astype(np.uint8)
                g = (((screen[:, :, 0] & 0xE0) >> 2) | ((screen[:, :, 0] & 0x03) << 6)).astype(np.uint8)
                b = ((screen[:, :, 0] & 0x1F) << 3 | (screen[:, :, 0] >> 5)).astype(np.uint8)
                a = np.full_like(r, 255, dtype=np.uint8)
                screen_out = np.stack((r, g, b, a), axis=-1)
            case _:
                raise ValueError(f"Unsupported pixel format: {self._pixel_format}")

        # Convert to contiguous array and prepare for Screenshot
        screen_out = np.ascontiguousarray(screen_out)
        screen_mv = screen_out.view(dtype=np.uint8)

        # Adjust width and height if rotated sideways
        if self._rotation in [Rotation.NINETY, Rotation.TWO_SEVENTY]:
            return Screenshot(
                memoryview(screen_mv),
                self._last_height,
                self._last_width,
                self._rotation,
                self._pixel_format,
            )
        else:
            return Screenshot(
                memoryview(screen_mv),
                self._last_width,
                self._last_height,
                self._rotation,
                self._pixel_format,
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
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        self._system_av_info = deepcopy(av_info)
        self.reinit()

    @property
    @override
    def geometry(self) -> retro_game_geometry | None:
        if not self._system_av_info:
            return None

        return deepcopy(self._system_av_info.geometry)

    @geometry.setter
    @override
    def geometry(self, geometry: retro_game_geometry) -> None:
        if not isinstance(geometry, retro_game_geometry):
            raise TypeError(f"Expected a retro_game_geometry, got {type(geometry).__name__}")

        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio


__all__ = ["ArrayVideoDriver"]
