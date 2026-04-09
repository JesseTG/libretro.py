import itertools
from array import array
from copy import deepcopy
from dataclasses import dataclass
from typing import final, override
from warnings import warn

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.video import MemoryAccess, PixelFormat, Rotation, retro_framebuffer

from ..driver import FrameBufferSpecial, Screenshot
from .base import SoftwareVideoDriver


@dataclass(frozen=True)
class FramebufferDimensions:
    width: int
    height: int
    pitch: int

    @property
    def length(self) -> int:
        return self.height * self.pitch


@final
class ArrayVideoDriver(SoftwareVideoDriver):
    def __init__(self):
        self._frame: array[int] | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._rotation: Rotation = Rotation.NONE
        self._frame_dims: FramebufferDimensions | None = None

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        requested_size = height * pitch
        match data:
            case memoryview() if self._frame is None:
                self._frame = array("B", itertools.repeat(0, requested_size))

            case memoryview() if self._frame:
                if len(data) > len(self._frame):
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

        self._frame_dims = FramebufferDimensions(width=width, height=height, pitch=pitch)

    @property
    @override
    def needs_reinit(self) -> bool:
        return self._frame is None

    @override
    def reinit(self) -> None:
        if not self._system_av_info:
            raise RuntimeError("Cannot reinitialize video driver without system AV info from core")

        geometry = self._system_av_info.geometry
        bufsize = geometry.max_width * geometry.max_height * self._pixel_format.bytes_per_pixel
        self._frame = array("B", itertools.repeat(0, bufsize))

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

        self._pixel_format = format

    @override
    def screenshot(self, prerotate: bool = True) -> Screenshot | None:
        if not (self._frame and self._frame_dims):
            return None

        last_frame_length = self._frame_dims.length
        screen = self._frame[:last_frame_length]
        screen_out = bytearray(self._frame_dims.width * self._frame_dims.height * 4)
        pixel_buf = array("B", (0, 0, 0, 255))

        rot = self._rotation if prerotate else Rotation.NONE

        # Select rotation coefficients
        # NOTE: output buffer is assumed to be four bytes per pixel (ABGR)
        match rot:
            case Rotation.NONE:
                start_y = 0
                delta_x = 4
                delta_y = self._frame_dims.width * 4
                is_sideways = False
            case Rotation.NINETY:
                start_y = (self._frame_dims.width - 4) * self._frame_dims.height * 4
                delta_x = self._frame_dims.height * -4
                delta_y = 4
                is_sideways = True
            case Rotation.ONE_EIGHTY:
                start_y = self._frame_dims.width * self._frame_dims.height * 4 - 4
                delta_x = -4
                delta_y = self._frame_dims.width * -4
                is_sideways = False
            case Rotation.TWO_SEVENTY:
                start_y = self._frame_dims.height * 4 - 4
                delta_x = self._frame_dims.height * 4
                delta_y = -4
                is_sideways = True

        # Copy from input buffer to output buffer, converting the pixel format
        #   and taking into account rotation (if prerotate is True).
        if self._pixel_format == PixelFormat.XRGB8888:
            for y in range(self._frame_dims.height):
                i = y * self._frame_dims.pitch
                o = start_y + y * delta_y
                for _ in range(self._frame_dims.width):
                    next_i = i + 3
                    pixel_buf[2::-1] = screen[i:next_i]
                    screen_out[o : o + 4] = pixel_buf
                    i = next_i + 1
                    o += delta_x
        elif self._pixel_format == PixelFormat.RGB565:
            for y in range(self._frame_dims.height):
                i = y * self._frame_dims.pitch
                o = start_y + y * delta_y
                for _ in range(self._frame_dims.width):
                    next_i = i + 2
                    b, r = screen[i:next_i]
                    g = ((b & 0xE0) >> 3) | ((r & 0x07) << 5)
                    b = (b & 0x1F) << 3
                    pixel_buf[0] = (r & 0xF8) | (r >> 5)
                    pixel_buf[1] = g | (g >> 6)
                    pixel_buf[2] = b | (b >> 5)
                    screen_out[o : o + 4] = pixel_buf
                    i = next_i
                    o += delta_x
        elif self._pixel_format == PixelFormat.RGB1555:
            for y in range(self._frame_dims.height):
                i = y * self._frame_dims.pitch
                o = start_y + y * delta_y
                for _ in range(self._frame_dims.width):
                    next_i = i + 2
                    b, g = screen[i:next_i]
                    r = (g & 0x7C) << 1
                    g = ((b & 0xE0) >> 2) | ((g & 0x03) << 6)
                    b = (b & 0x1F) << 3
                    pixel_buf[0] = r | (r >> 5)
                    pixel_buf[1] = g | (g >> 5)
                    pixel_buf[2] = b | (b >> 5)
                    screen_out[o : o + 4] = pixel_buf
                    i = next_i
                    o += delta_x

        # Swap width and height if buffer is rotated 90 or 270 degrees.
        if is_sideways:
            return Screenshot(
                memoryview(screen_out),
                self._frame_dims.height,
                self._frame_dims.width,
                self._rotation,
                self._pixel_format,
            )
        return Screenshot(
            memoryview(screen_out),
            self._frame_dims.width,
            self._frame_dims.height,
            self._rotation,
            self._pixel_format,
        )

    @override
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        pass  # TODO: Implement by returning a pointer to the internal frame buffer, and reinitializing it if the size has changed

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

        if not self._system_av_info:
            raise RuntimeError("Cannot set geometry without system AV info from core")

        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio


__all__ = ["ArrayVideoDriver"]
