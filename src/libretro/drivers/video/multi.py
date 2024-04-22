from array import array
from collections.abc import Callable, Mapping, Set
from typing import AbstractSet, override

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t
from libretro.api.video import (
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_render_callback,
    retro_hw_render_interface,
)

from .driver import VideoDriver

DriverMap = Mapping[HardwareContext, Callable[[retro_hw_render_callback], VideoDriver]]


class VideoDriverUninitializedError(RuntimeError):
    pass


class MultiVideoDriver(VideoDriver):
    """
    Delegates to one of several video drivers based on the core's requested context type.
    """

    def __init__(self, drivers: DriverMap, active: HardwareContext):
        """
        :param drivers:
        """
        self._current: VideoDriver | None = None
        self._drivers = drivers
        self._pixel_format = PixelFormat.RGB1555

    def refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.refresh(data, width, height, pitch)

    def supported_contexts(self) -> Set[HardwareContext]:
        return frozenset(self._drivers.keys())

    def active_context(self) -> HardwareContext | None:
        if not self._current:
            return None

        return self._current.active_context

    @property
    @override
    def preferred_context(self) -> HardwareContext | None:
        ...

    @preferred_context.setter
    @override
    def preferred_context(self, context: HardwareContext) -> None:
        ...

    @preferred_context.deleter
    @override
    def preferred_context(self) -> None:
        ...

    @override
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        ...

    @override
    def context_reset(self) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.context_reset()

    @override
    def context_destroy(self) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.context_destroy()

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
        self._current.set_context()

        pass

    @property
    @override
    def rotation(self) -> Rotation:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.rotation

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.rotation = rotation

    @property
    def can_dupe(self) -> bool:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.can_dupe

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._current.pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, format: PixelFormat) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        if format not in PixelFormat:
            raise ValueError(f"Invalid pixel format: {format}")

        self._current.pixel_format = PixelFormat(format)

    def get_hw_framebuffer(self) -> int:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.get_hw_framebuffer()

    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.get_proc_address(sym)

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.system_av_info

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.system_av_info = av_info

    @property
    @override
    def geometry(self) -> retro_game_geometry:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.geometry

    @geometry.setter
    @override
    def geometry(self, geometry: retro_game_geometry) -> None:
        if not self._current:
            raise RuntimeError("No driver initialized")

        self._current.geometry = geometry

    @override
    def get_software_framebuffer(
        self, width: int, size: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.get_software_framebuffer(width, size, flags)

    @property
    @override
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.hw_render_interface

    @property
    @override
    def shared_context(self) -> bool:
        if not self._current:
            raise VideoDriverUninitializedError()

        return self._current.shared_context

    @shared_context.setter
    @override
    def shared_context(self, value: bool) -> None:
        if not self._current:
            raise VideoDriverUninitializedError()

        self._current.shared_context = value

    @property
    def frame(self):
        pass

    @property
    def frame_max(self):
        pass


__all__ = ["MultiVideoDriver"]
