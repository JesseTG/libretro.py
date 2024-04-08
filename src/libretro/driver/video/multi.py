from array import array
from collections.abc import Mapping, Callable

from .driver import VideoDriver
from libretro.api.video import (
    retro_hw_render_callback,
    retro_hw_render_interface,
    retro_framebuffer,
    Rotation,
    PixelFormat,
    MemoryAccess,
    HardwareContext,
)
from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t

DriverMap = Mapping[HardwareContext, Callable[[retro_hw_render_callback], VideoDriver]]


class MultiVideoDriver(VideoDriver):
    def __init__(self, drivers: DriverMap):
        self._current: VideoDriver | None = None
        self._drivers = drivers
        self._pixel_format = PixelFormat.RGB1555

    def _refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        pass

    def init_callback(self, callback: retro_hw_render_callback) -> bool:
        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        context_type = HardwareContext(callback.context_type)
        if context_type not in self._drivers:
            raise ValueError(f"Unsupported context type for driver: {context_type}")

        if self._current:
            self._current.context_destroy()
            del self._current

        self._current = self._drivers[context_type](callback)
        self._current.context_reset()

        pass

    def set_rotation(self, rotation: Rotation) -> bool:
        pass

    @property
    def can_dupe(self) -> bool:
        if not self._current:
            raise RuntimeError("No driver initialized")

        return self._current.can_dupe

    def set_pixel_format(self, format: PixelFormat) -> bool:
        if format not in PixelFormat:
            raise ValueError(f"Invalid pixel format: {format}")

        if not self._current:
            raise RuntimeError("No driver initialized")

        self._pixel_format = format
        return self._current.set_pixel_format(format)

    def get_hw_framebuffer(self) -> int:
        if not self._current:
            raise RuntimeError("No driver initialized")

        return self._current.get_hw_framebuffer()

    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if not self._current:
            raise RuntimeError("No driver initialized")

        return self._current.get_proc_address(sym)

    def set_system_av_info(self, av_info: retro_system_av_info) -> None:
        if not self._current:
            raise RuntimeError("No driver initialized")

        self._current.set_system_av_info(av_info)

    def set_geometry(self, geometry: retro_game_geometry) -> None:
        if not self._current:
            raise RuntimeError("No driver initialized")

        self._current.set_geometry(geometry)

    def get_software_framebuffer(self, width: int, size: int, flags: MemoryAccess) -> retro_framebuffer | None:
        pass

    @property
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        pass

    def capture_frame(self) -> array:
        pass

    def set_shared_context(self) -> None:
        pass

    def context_reset(self) -> None:
        pass

    def context_destroy(self) -> None:
        pass
