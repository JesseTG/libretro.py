from array import array
from collections.abc import Callable, Mapping, Set
from typing import final, override

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

from .driver import FrameBufferSpecial, VideoDriver, VideoDriverInitArgs

DriverMap = Mapping[HardwareContext, Callable[[VideoDriverInitArgs], VideoDriver]]

_INITIAL_CALLBACK = retro_hw_render_callback(HardwareContext.NONE)


@final
class MultiVideoDriver(VideoDriver):
    """
    A video driver that delegates to one of several possible video drivers,
    depending on what the core or frontend requests.

    This class is useful for cores that support multiple hardware contexts,
    especially if it can switch between them at runtime.
    """

    def __init__(self, drivers: DriverMap, preferred: HardwareContext = HardwareContext.NONE):
        """
        Initializes a new multi-video driver with the preferred hardware context.
        A hardware rendering context may be initialized,
        but it will only be exposed to the cores that use ``EnvironmentCall.SET_HW_RENDER``.

        :param drivers: A map of hardware context types to callables;
          each callable should accept a ``retro_hw_render_callback``
          and return a new video driver instance.
        :param preferred: The initial hardware context type to use.
        :raises TypeError: If any parameter is not consistent with its documented types.
        :raises ValueError: If ``preferred`` does not exist in ``drivers``.
        """
        if not isinstance(drivers, Mapping):
            raise TypeError(
                f"Expected a mapping of hardware contexts to callables, got {type(drivers).__name__}"
            )

        if preferred not in HardwareContext:
            raise ValueError(f"Invalid hardware context: {preferred}")

        if preferred not in drivers:
            raise ValueError(f"No video driver for preferred hardware context: {preferred}")

        if not all(isinstance(k, HardwareContext) for k in drivers.keys()):
            raise TypeError("All keys in 'drivers' must be HardwareContext instances")

        if not all(callable(v) for v in drivers.values()):
            raise TypeError("All values in 'drivers' must be callable")

        self._preferred = preferred
        self._drivers = dict(drivers)
        self._supported_contexts = frozenset(self._drivers.keys())
        self._current = self._drivers[preferred](_INITIAL_CALLBACK)

        if not isinstance(self._current, VideoDriver):
            raise TypeError(
                f"Expected the callable mapped to {preferred} to return a VideoDriver, got {type(self._current).__name__}"
            )
        self._current: VideoDriver | None = None

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        self._current.refresh(data, width, height, pitch)

    @property
    @override
    def needs_reinit(self) -> bool:
        if not self._current:
            return True

        return self._current.needs_reinit

    @override
    def reinit(self) -> None:
        # TODO: Use self._drivers[preferred]
        pass
        # TODO: If no video driver or if switching to a new API, reinit
        # TODO: If using the same API, call reinit on the current video driver


    @property
    @override
    def supported_contexts(self) -> Set[HardwareContext]:
        return self._supported_contexts

    @property
    @override
    def active_context(self) -> HardwareContext:
        return self._current.active_context

    @property
    @override
    def preferred_context(self) -> HardwareContext | None:
        return self._preferred

    @preferred_context.setter
    @override
    def preferred_context(self, context: HardwareContext) -> None:
        if not isinstance(context, HardwareContext):
            raise TypeError(f"Expected a HardwareContext, got {type(context).__name__}")

        if context not in self._supported_contexts:
            raise ValueError(f"Unsupported hardware context: {context}")

        self._preferred = context

    @preferred_context.deleter
    @override
    def preferred_context(self) -> None:
        self._preferred = None

    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        pass



    @property
    @override
    def rotation(self) -> Rotation:
        return self._current.rotation

    @rotation.setter
    @override
    def rotation(self, value: Rotation) -> None:
        self._current.rotation = value

    @property
    @override
    def can_dupe(self) -> bool | None:
        return self._current.can_dupe

    @can_dupe.setter
    @override
    def can_dupe(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Expected a bool, got {type(value).__name__}")

        self._current.can_dupe = value

    @can_dupe.deleter
    @override
    def can_dupe(self) -> None:
        del self._current.can_dupe

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._current.pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, value: PixelFormat) -> None:
        if not isinstance(value, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(value).__name__}")

        self._current.pixel_format = value

    @property
    @override
    def system_av_info(self) -> retro_system_av_info:
        return self._current.system_av_info

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        self._current.system_av_info = av_info

    @property
    @override
    def geometry(self) -> retro_game_geometry:
        return self._current.geometry

    @geometry.setter
    @override
    def geometry(self, value: retro_game_geometry) -> None:
        self._current.geometry = value

    @override
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        return self._current.get_software_framebuffer(width, height, flags)

    @property
    @override
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        return self._current.hw_render_interface

    @property
    @override
    def shared_context(self) -> bool:
        return self._current.shared_context

    @shared_context.setter
    @override
    def shared_context(self, value: bool) -> None:
        self._current.shared_context = value

    @property
    @override
    def screenshot(self) -> array:
        return self._current.screenshot


__all__ = [
    "MultiVideoDriver",
    "DriverMap",
]
