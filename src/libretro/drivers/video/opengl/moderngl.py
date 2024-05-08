import ctypes
import struct
import warnings
from array import array
from collections.abc import Mapping, Set, Sequence
from copy import deepcopy
from ctypes import c_char_p
from sys import modules
from typing import final, override
from importlib import resources

import moderngl
from moderngl import Context, Framebuffer, Renderbuffer, Texture, create_context, VertexArray

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

from ..driver import FrameBufferSpecial, VideoDriver, VideoDriverInitArgs

_CONTEXTS = frozenset((HardwareContext.NONE, HardwareContext.OPENGL_CORE, HardwareContext.OPENGL))

_DEFAULT_VERT_FILENAME = "moderngl_vertex.glsl"
_DEFAULT_FRAG_FILENAME = "moderngl_frag.glsl"

_vertex = struct.Struct("4f")  # 4 floats (one vec2 for screen coords, one for vec2 coords)
_VERTEXES = b''.join(
    (
        _vertex.pack(0, 0, 0, 1),
        _vertex.pack(1, 0, 1, 1),
        _vertex.pack(0, 1, 0, 0),
        _vertex.pack(1, 1, 1, 0),
    )
)


@final
class ModernGlVideoDriver(VideoDriver):
    def __init__(
            self,
            vertex_shader: str | None = None,
            fragment_shader: str | None = None,
            varyings: Sequence[str] = ("transformedTexCoord",)
    ):
        """
        Initializes the video driver.
        Does not create an OpenGL context; that will occur when ``reinit`` is called.

        This driver uses a basic shader program, but custom shaders can be provided.

        :warning: The shaders are not compiled or linked until the OpenGL context is created,
            so GLSL errors won't be detected until then.

        :param vertex_shader: The GLSL source of the vertex shader to use for rendering,
            or ``None`` to use the built-in default.
        :param fragment_shader: The GLSL source of the fragment shader to use for rendering,
            or ``None`` to use the built-in default.
        :param varyings: The names of the "varyings" (vertex value outputs) to use.
        """
        package_files = resources.files(modules[__name__])
        # TODO: Support passing SPIR-V shaders as bytes
        match vertex_shader:
            case str():
                self._vertex_shader = vertex_shader
            case None:
                self._vertex_shader = (package_files / _DEFAULT_VERT_FILENAME).read_text()
            case _:
                raise TypeError(f"Expected a str or None, got {type(vertex_shader).__name__}")

        match fragment_shader:
            case str():
                self._fragment_shader = fragment_shader
            case None:
                self._fragment_shader = (package_files / _DEFAULT_FRAG_FILENAME).read_text()
            case _:
                raise TypeError(f"Expected a str or None, got {type(fragment_shader).__name__}")

        if not isinstance(varyings, Sequence):
            raise TypeError(f"Expected a sequence of str, got {type(varyings).__name__}")

        if not all(isinstance(v, str) for v in varyings):
            raise TypeError("All elements of 'varyings' must be str")

        self._varyings = tuple(varyings)
        self._callback: retro_hw_render_callback | None = None
        self._prev_callback: retro_hw_render_callback | None = None
        self._pixel_format = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._shared = False
        self._context: Context | None = None
        self._vao: VertexArray | None = None
        self._hw_render_fbo: Framebuffer | None = None
        self._hw_render_texture: Texture | None = None
        self._hw_render_rb_ds: Renderbuffer | None = None
        self._cpu_texture: Texture | None = None
        self._shader_program: moderngl.Program | None = None
        self._get_proc_address = retro_hw_get_proc_address_t(self.__get_proc_address)
        self._get_hw_framebuffer = retro_hw_get_current_framebuffer_t(self.__get_hw_framebuffer)

    def __del__(self):
        del self._hw_render_texture
        del self._hw_render_rb_ds
        del self._hw_render_fbo
        del self._cpu_texture
        del self._vao
        del self._context

    @override
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        if callback is None:
            return None

        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        context_type = HardwareContext(callback.context_type)
        if context_type not in _CONTEXTS:
            return None

        self._prev_callback = self._callback
        self._callback = deepcopy(callback)
        self._callback.get_current_framebuffer = self._get_hw_framebuffer
        self._callback.get_proc_address = self._get_proc_address
        return deepcopy(self._callback)

    def refresh(
            self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:

        match data:
            case FrameBufferSpecial.DUPE:
                # Do nothing, we're re-rendering the previous frame
                pass
            case FrameBufferSpecial.HARDWARE:
                # No special treatment needed if rendering in hardware
                pass

            case memoryview():
                self.__update_cpu_texture(data, width, height, pitch)

            # TODO: Bind the framebuffer, clear it, then render the contents

    @property
    @override
    def needs_reinit(self) -> bool:
        if not self._context:
            return True

        if not self._vao:
            return True

        return False

    @override
    def reinit(self) -> None:
        if not self._system_av_info:
            raise RuntimeError("System AV info not set")

        context_type = HardwareContext(
            self._callback.context_type) if self._callback else HardwareContext.NONE

        if context_type not in _CONTEXTS:
            raise RuntimeError(f"Unsupported hardware context: {context_type}")

        # TODO: Honor cache_context; try to avoid reinitializing the context
        if self._context:
            if self._callback and self._callback.context_destroy:
                # If the core wants to clean up before the context is destroyed...
                self._callback.context_destroy()

            self._context.release()
            del self._context

            del self._hw_render_rb_ds
            del self._hw_render_texture
            del self._hw_render_fbo
            del self._vao
            del self._shader_program
            # Destroy the OpenGL context and create a new one

        match context_type:
            case HardwareContext.NONE:
                # Create a default context with OpenGL 3.3 core profile;
                # do not expose it to the core, only use it for software rendering
                self._context = create_context(standalone=True)
            case HardwareContext.OPENGL:
                self._context = create_context(standalone=True, share=self._shared)
            case HardwareContext.OPENGL_CORE:
                ver = self._callback.version_major * 100 + self._callback.version_minor * 10
                self._context = create_context(require=ver, standalone=True, share=self._shared)

        self._shader_program = self._context.program(
            vertex_shader=self._vertex_shader,
            fragment_shader=self._fragment_shader,
            varyings=self._varyings
        )
        self._vao = self._context.vertex_array()

        # TODO: Honor debug_context; enable debugging features if requested
        if self._callback is not None and context_type != HardwareContext.NONE:
            # If the core specifically wants to render with the OpenGL API...
            self.__init_hw_render()

            if self._callback.context_reset:
                # If the core wants to set up resources after the context is created...
                self._callback.context_reset()

    @override
    @property
    def supported_contexts(self) -> Set[HardwareContext]:
        return _CONTEXTS

    @override
    @property
    def preferred_context(self) -> HardwareContext | None:
        return HardwareContext.OPENGL_CORE

    def active_context(self) -> HardwareContext | None:
        if self._context and self._callback:
            return HardwareContext(self._callback.context_type)

        return HardwareContext.NONE

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

        if not self._system_av_info:
            raise RuntimeError("No system AV info has been set")

        self._system_av_info.geometry.base_width = geometry.base_width
        self._system_av_info.geometry.base_height = geometry.base_height
        self._system_av_info.geometry.aspect_ratio = geometry.aspect_ratio
        # TODO: Set the OpenGL viewport if necessary

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
            self._needs_reinit_buffer = True
            if self._cpu_texture:
                del self._cpu_texture

    @property
    @override
    def rotation(self) -> Rotation:
        pass

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        pass  # TODO: Implement

    @property
    @override
    def system_av_info(self) -> retro_system_av_info:
        return deepcopy(self._system_av_info)

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        self._system_av_info = deepcopy(av_info)

    @property
    @override
    def screenshot(self) -> array | None:
        data = self._hw_render_fbo.read()
        return array("B", data) if data else None

    @property
    @override
    def framebuffer(self):
        pass

    @property
    @override
    def shared_context(self) -> bool:
        return self._shared

    @shared_context.setter
    @override
    def shared_context(self, shared: bool) -> None:
        self._shared = bool(shared)

    @property
    def can_dupe(self) -> bool:
        return True

    def get_software_framebuffer(
            self, width: int, size: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        # TODO: Map the OpenGL texture to a software framebuffer
        pass

    @property
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        # libretro doesn't define one of these for OpenGL, so no need
        return None

    def __init_hw_render(self):
        assert self._context is not None
        assert self._callback is not None
        assert self._system_av_info is not None

        if self._hw_render_fbo:
            del self._hw_render_fbo

        if self._hw_render_texture:
            del self._hw_render_texture

        if self._hw_render_rb_ds:
            del self._hw_render_rb_ds

        # Equivalent to glGetIntegerv
        max_fbo_size = self._context.info["GL_MAX_TEXTURE_SIZE"]
        max_rb_size = self._context.info["GL_MAX_RENDERBUFFER_SIZE"]
        geometry = self._system_av_info.geometry

        width = min(geometry.max_width, max_fbo_size, max_rb_size)
        height = min(geometry.max_height, max_fbo_size, max_rb_size)
        size = (width, height)

        # Similar to glGenTextures, glBindTexture, and glTexImage2D
        self._hw_render_texture = self._context.texture(size, 4)
        if self._callback.depth:
            # If the core is asking for a depth attachment...
            # Similar to glGenRenderbuffers, glBindRenderbuffer, and glRenderbufferStorage
            self._hw_render_rb_ds = self._context.depth_renderbuffer(size)

            if self._callback.stencil:
                warnings.warn(
                    "Core requested stencil attachment, but moderngl lacks support; ignoring")
                # TODO: Implement stencil buffer support in moderngl

        # Similar to glGenFramebuffers, glBindFramebuffer, and glFramebufferTexture2D
        self._hw_render_fbo = self._context.framebuffer(
            self._hw_render_texture,
            self._hw_render_rb_ds
        )
        self._hw_render_fbo.clear()

    def __update_cpu_texture(self, data: memoryview, width: int, height: int, pitch: int):
        if not (self._cpu_texture and self._cpu_texture.size == (width, height)):
            # If we don't have a CPU texture, or we need one of a new size...
            del self._cpu_texture

            # Equivalent to glGenTextures, glBindTexture, glTexImage2D, and glTexParameteri
            match self._pixel_format:
                case PixelFormat.XRGB8888:
                    self._cpu_texture = self._context.texture((width, height), 4, data)  # GL_RGBA8
                    self._cpu_texture.swizzle = "ABGR"
                case PixelFormat.RGB565:
                    GL_RGB565 = 0x8D62
                    self._cpu_texture = self._context.texture(
                        (width, height),
                        3,
                        data,
                        internal_format=GL_RGB565
                    )
                    # moderngl can't natively express GL_RGB565
                case PixelFormat.RGB1555:
                    GL_RGB5 = 0x8050
                    self._cpu_texture = self._context.texture(
                        (width, height),
                        3,
                        data,
                        internal_format=GL_RGB5
                    )
                    # moderngl can't natively express GL_RGB5
        else:
            self._cpu_texture.write(data)

    def __get_hw_framebuffer(self) -> int:
        if self._hw_render_fbo:
            return self._hw_render_fbo.glo

        return 0

    def __get_proc_address(self, sym: bytes) -> int:
        if not sym:
            return 0

        if not self._context:
            raise RuntimeError("OpenGL context not initialized")

        # See here https://github.com/moderngl/glcontext?tab=readme-ov-file#structure
        return self._context.mglo._context.load_opengl_function(sym.decode())


__all__ = ["ModernGlVideoDriver"]
