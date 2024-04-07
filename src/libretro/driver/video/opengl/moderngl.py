from array import array
from copy import deepcopy

import moderngl
from glcontext.empty import GLContext

from ..driver import *
from libretro.api.video.context import *
from libretro.api.video.memory import *
from libretro.api.video.render import *
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

    def _refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None:
        # TODO: Recreate the frame buffer based on the pixel format and system AV info
        pass # TODO: Implement

    def init_callback(self, callback: retro_hw_render_callback) -> bool:
        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        match callback.context_type, callback.version_major, callback.version_minor:
            case HardwareContext.OPENGL, _, _:
                self._context = moderngl.create_context(standalone=True, share=self._use_shared_context)
                # TODO: What do the version numbers do here?
            case HardwareContext.OPENGL_CORE, major, minor:
                version = major * 100 + minor * 10
                self._context = moderngl.create_context(require=version, standalone=True, share=self._use_shared_context)
            case _, _, _:
                return False

        callback.get_current_framebuffer = retro_hw_get_current_framebuffer_t(self.get_hw_framebuffer)
        callback.get_proc_address = retro_hw_get_proc_address_t(self.get_proc_address)
        self._hw_render_callback = deepcopy(callback)

        #

        return True

    def set_rotation(self, rotation: Rotation) -> bool:
        raise NotImplementedError() # TODO: Implement

    @property
    def can_dupe(self) -> bool:
        return True

    def set_pixel_format(self, format: PixelFormat) -> bool:
        raise NotImplementedError() # TODO: Implement

    def get_hw_framebuffer(self) -> int:
        raise NotImplementedError() # TODO: Implement

    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if not sym:
            return None

        return retro_proc_address_t(self._context.load_opengl_function(sym))

    def set_system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        # TODO: Set the new AV info, recreate the frame buffer if necessary

    def set_geometry(self, geometry: retro_game_geometry) -> None:
        pass
        # TODO: Crop the OpenGL texture if necessary

    def get_software_framebuffer(self, width: int, size: int, flags: FramebufferMemoryAccess) -> retro_framebuffer | None:
        # TODO: Map the OpenGL texture to a software framebuffer
        pass

    @property
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        return None

    def set_shared_context(self) -> None:
        self._use_shared_context = True

    def context_reset(self) -> None:
        if not self._hw_render_callback:
            raise RuntimeError("No render callback has been initialized")

        if self._hw_render_callback.context_reset:
            self._hw_render_callback.context_reset()

    def context_destroy(self) -> None:
        if not self._context:
            raise RuntimeError("No OpenGL context has been initialized")

        if self._hw_render_callback.context_destroy:
            self._hw_render_callback.context_destroy()

    def capture_frame(self) -> array:
        raise NotImplementedError()

