from collections.abc import Callable, Mapping, Set
from copy import deepcopy
from typing import final

from libretro._typing import override
from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t
from libretro.api.video import (
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_get_current_framebuffer_t,
    retro_hw_get_proc_address_t,
    retro_hw_render_callback,
    retro_hw_render_interface,
)
from libretro.error import UnsupportedEnvCall

from .driver import FrameBufferSpecial, Screenshot, VideoDriver

DriverMap = Mapping[HardwareContext, Callable[[], VideoDriver]]


@final
class MultiVideoDriver(VideoDriver):
    """
    A video driver that delegates to one of several possible video drivers,
    depending on what the core or frontend requests.

    This class is useful for a core that supports multiple hardware contexts,
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
        self._pixel_format = PixelFormat.RGB1555
        self._current: VideoDriver | None = None
        self._rotation: Rotation = Rotation.NONE
        self._system_av_info: retro_system_av_info | None = None
        self._callback: retro_hw_render_callback | None = None
        self._can_dupe: bool | None = True
        self._shared_context = False
        self._next_hw_context: HardwareContext | None = HardwareContext.NONE

        # We need to keep these objects alive before we can pass these callbacks to the core,
        # or else they'll be garbage-collected and the core will crash.
        self._get_current_framebuffer = retro_hw_get_current_framebuffer_t(
            lambda: self.current_framebuffer
        )
        self._get_proc_address = retro_hw_get_proc_address_t(self.get_proc_address)

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        self._current.refresh(data, width, height, pitch)

    @property
    @override
    def needs_reinit(self) -> bool:
        if self._current is None:
            return True

        if self._next_hw_context is not None:
            return True

        return self._current.needs_reinit

    @override
    def reinit(self) -> None:
        if self._current is not None and self._current.active_context == self._next_hw_context:
            # If we're not switching to a whole new video driver...
            self._current.reinit()  # ...then just let the driver reinit itself
        else:
            # If we're switching to another hardware rendering API...
            driver = self._drivers[self._next_hw_context]()
            if not driver:
                raise RuntimeError(f"Video driver for {self._next_hw_context} not initialized")

            if self._current is not None:
                # Use the settings of the existing video driver if we're switching to a new one
                pixel_format = self._current.pixel_format
                system_av_info = self._current.system_av_info
                rotation = self._current.rotation
                shared = self._current.shared_context
            else:
                pixel_format = self._pixel_format
                system_av_info = self._system_av_info
                rotation = self._rotation
                shared = self._shared_context

            driver.pixel_format = pixel_format
            try:
                driver.rotation = rotation
            except UnsupportedEnvCall:
                self._rotation = Rotation.NONE

            try:
                driver.shared_context = shared
            except UnsupportedEnvCall:
                self._shared_context = False

            old_driver = self._current
            self._current = driver

            # Must set the callback before setting the system AV info,
            # as setting the system AV info reinitializes the video driver immediately
            # and that requires calling the core-provided callbacks
            driver.set_context(self._callback)

            if system_av_info is not None:
                driver.system_av_info = system_av_info
                # No need to call driver.reinit(); setting the system AV info should do that

            del old_driver
            # TODO: If initializing the new driver fails, keep the old one

        self._next_hw_context = None

    @property
    @override
    def supported_contexts(self) -> Set[HardwareContext]:
        return self._supported_contexts

    @property
    @override
    def active_context(self) -> HardwareContext:
        return self._current.active_context if self._current else HardwareContext.NONE

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

    @override
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        if callback is None:
            return None

        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        context_type = HardwareContext(callback.context_type)
        if context_type not in self._supported_contexts:
            return None

        self._next_hw_context = context_type
        self._callback = deepcopy(callback)
        self._callback.get_current_framebuffer = self._get_current_framebuffer
        self._callback.get_proc_address = self._get_proc_address
        # TODO: What to do if requesting NONE explicitly?

        return deepcopy(self._callback)

    @property
    @override
    def current_framebuffer(self) -> int:
        if self._current is None:
            return 0

        framebuffer = self._current.current_framebuffer
        if framebuffer is None:
            return 0

        return framebuffer

    @override
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if self._current is None:
            return None

        return self._current.get_proc_address(sym)

    @property
    @override
    def rotation(self) -> Rotation:
        return self._rotation

    @rotation.setter
    @override
    def rotation(self, value: Rotation) -> None:
        self._rotation = value

        if self._current:
            self._current.rotation = value

    @property
    @override
    def can_dupe(self) -> bool | None:
        if self._current is not None:
            return self._current.can_dupe

        return self._can_dupe

    @can_dupe.setter
    @override
    def can_dupe(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Expected a bool, got {type(value).__name__}")

        self._can_dupe = value

        if self._current is not None:
            self._current.can_dupe = value

    @can_dupe.deleter
    @override
    def can_dupe(self) -> None:
        self._can_dupe = None

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, value: PixelFormat) -> None:
        if not isinstance(value, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(value).__name__}")

        self._pixel_format = value

        if self._current is not None:
            self._current.pixel_format = value

    @property
    @override
    def system_av_info(self) -> retro_system_av_info:
        if self._current is not None:
            return self._current.system_av_info

        return self._system_av_info

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected retro_system_av_info, got {type(av_info).__name__}")

        self._system_av_info = deepcopy(av_info)
        self.reinit()

    @property
    @override
    def geometry(self) -> retro_game_geometry | None:
        return deepcopy(self._system_av_info.geometry) if self._system_av_info else None

    @geometry.setter
    @override
    def geometry(self, value: retro_game_geometry) -> None:
        if not isinstance(value, retro_game_geometry):
            raise TypeError(f"Expected retro_game_geometry, got {type(value).__name__}")

        self._system_av_info.geometry.base_width = value.base_width
        self._system_av_info.geometry.base_height = value.base_height
        self._system_av_info.geometry.aspect_ratio = value.aspect_ratio

        if self._current is not None:
            self._current.geometry = value

    @override
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        if self._current:
            return self._current.get_software_framebuffer(width, height, flags)

        return None

    @property
    @override
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        if self._current:
            return self._current.hw_render_interface

        return None

    @property
    @override
    def shared_context(self) -> bool:
        if self._current:
            return self._current.shared_context

        return self._shared_context

    @shared_context.setter
    @override
    def shared_context(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value).__name__}")

        self._shared_context = value

        if self._current:
            self._current.shared_context = value

    @override
    def screenshot(self) -> Screenshot | None:
        return self._current.screenshot() if self._current else None


__all__ = [
    "MultiVideoDriver",
    "DriverMap",
]
