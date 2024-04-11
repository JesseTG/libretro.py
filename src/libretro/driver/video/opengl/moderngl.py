from array import array
from collections.abc import Set
from copy import deepcopy
from ctypes import c_char_p
from typing import override

import moderngl
from glcontext.empty import GLContext

from ..driver import VideoDriver
from libretro.api.video import (
    retro_hw_render_callback,
    retro_hw_render_interface,
    retro_framebuffer,
    Rotation,
    PixelFormat,
    MemoryAccess,
    HardwareContext,
    retro_hw_get_current_framebuffer_t,
    retro_hw_get_proc_address_t,
)

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t


class ModernGlVideoDriver(VideoDriver):

    def __init__(self, callback: retro_hw_render_callback | None = None):
        self._context: GLContext | None = None
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._hw_render_callback = callback
        self._use_shared_context = False
        self._needs_recreate = True

    def __del__(self):
        if self._context:
            self._context.release()

            del self._context

    def refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        # TODO: Recreate the frame buffer based on the pixel format and system AV info
        pass # TODO: Implement

    def supported_contexts(self) -> Set[HardwareContext]:
        pass

    @property
    def preferred_context(self) -> HardwareContext | None:
        pass

    def active_context(self) -> HardwareContext | None:
        if self._context:
            return HardwareContext.OPENGL

        return HardwareContext.NONE

    @override
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        self._hw_render_callback = deepcopy(callback)
        self._hw_render_callback.get_current_framebuffer = retro_hw_get_current_framebuffer_t(self.get_hw_framebuffer)
        self._hw_render_callback.get_proc_address = retro_hw_get_proc_address_t(self.__get_proc_address)

        return self._hw_render_callback

    @property
    @override
    def geometry(self) -> retro_game_geometry:
        if not self._system_av_info:
            raise RuntimeError("No system AV info has been set")

        return deepcopy(self._system_av_info.geometry)

    @geometry.setter
    @override
    def geometry(self, geometry: retro_game_geometry) -> None:
        if not isinstance(geometry, retro_game_geometry):
            raise TypeError(f"Expected a retro_game_geometry, got {type(geometry).__name__}")

        self._system_av_info.geometry = geometry
        # TODO: Crop the OpenGL texture if necessary

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, format: PixelFormat) -> None:
        if not isinstance(format, PixelFormat):
            raise TypeError(f"Expected a PixelFormat, got {type(format).__name__}")

        if format not in PixelFormat:
            raise ValueError(f"Invalid pixel format: {format}")

        if self._pixel_format != format:
            self._pixel_format = format
            self._needs_recreate = True

    @property
    @override
    def rotation(self) -> Rotation:
        pass

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        pass # TODO: Implement

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info) if self._system_av_info else None

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        self._system_av_info = av_info
        self._needs_recreate = True

    @property
    def frame(self):
        pass

    @property
    def frame_max(self):
        pass

    @property
    @override
    def shared_context(self) -> bool:
        return self._use_shared_context

    @shared_context.setter
    @override
    def shared_context(self, shared: bool) -> None:
        self._use_shared_context = bool(shared)

    def set_rotation(self, rotation: Rotation) -> bool:
        raise NotImplementedError() # TODO: Implement

    @property
    def can_dupe(self) -> bool:
        return True

    def get_hw_framebuffer(self) -> int:
        raise NotImplementedError() # TODO: Implement

    def __get_proc_address(self, sym: c_char_p) -> retro_proc_address_t:
        return self.get_proc_address(bytes(sym))

    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if not sym:
            return None

        if not self._context:
            raise RuntimeError("No OpenGL context has been initialized")

        return retro_proc_address_t(self._context.load_opengl_function(sym))

    def get_software_framebuffer(self, width: int, size: int, flags: MemoryAccess) -> retro_framebuffer | None:
        # TODO: Map the OpenGL texture to a software framebuffer
        pass

    @property
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        # libretro doesn't define one of these for OpenGL, so no need
        return None

    def context_reset(self) -> None:
        pass # TODO: Implement

    def context_destroy(self) -> None:
        if not self._context:
            raise RuntimeError("No OpenGL context has been initialized")

        if self._hw_render_callback.context_destroy:
            self._hw_render_callback.context_destroy()


__all__ = ['ModernGlVideoDriver']
