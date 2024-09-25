import struct
import warnings
from array import array
from collections.abc import Callable, Iterator, Sequence, Set
from contextlib import contextmanager
from copy import deepcopy
from importlib import resources
from sys import modules
from typing import final

import moderngl
from OpenGL import GL

try:
    import moderngl_window
    from moderngl_window.context.base import BaseWindow

    # These features require moderngl_window,
    # but I don't want to require that it be installed
except ImportError:
    moderngl_window = None
    BaseWindow = None

from moderngl import (
    Buffer,
    Context,
    Framebuffer,
    Program,
    Query,
    Renderbuffer,
    Sampler,
    Texture,
    VertexArray,
    create_context,
)

from libretro._typing import override
from libretro.api.av import retro_game_geometry, retro_system_av_info
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

from ..driver import FrameBufferSpecial, Screenshot, VideoDriver

_CONTEXTS = frozenset((HardwareContext.NONE, HardwareContext.OPENGL_CORE, HardwareContext.OPENGL))

_DEFAULT_VERT_FILENAME = "moderngl_vertex.glsl"
_DEFAULT_FRAG_FILENAME = "moderngl_frag.glsl"

_vertex = struct.Struct("2f 2f")  # 4 floats (one vec2 for screen coords, one for vec2 coords)
_POSITION_NORTHWEST = (-1, 1)
_POSITION_NORTHEAST = (1, 1)
_POSITION_SOUTHWEST = (-1, -1)
_POSITION_SOUTHEAST = (1, -1)
_TEXCOORD_NORTHWEST = (0, 1)
_TEXCOORD_NORTHEAST = (1, 1)
_TEXCOORD_SOUTHWEST = (0, 0)
_TEXCOORD_SOUTHEAST = (1, 0)

_NORTHWEST = _vertex.pack(*_POSITION_NORTHWEST, *_TEXCOORD_NORTHWEST)
_NORTHEAST = _vertex.pack(*_POSITION_NORTHEAST, *_TEXCOORD_NORTHEAST)
_SOUTHWEST = _vertex.pack(*_POSITION_SOUTHWEST, *_TEXCOORD_SOUTHWEST)
_SOUTHEAST = _vertex.pack(*_POSITION_SOUTHEAST, *_TEXCOORD_SOUTHEAST)

_VERTEXES = b"".join((_NORTHWEST, _SOUTHWEST, _NORTHEAST, _SOUTHEAST))

_DEFAULT_WINDOW_IMPL = "pyglet"
_IDENTITY_MAT4 = array("f", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

GL_RGBA = 0x1908
ModernGlResource = (
    Buffer | Program | VertexArray | Query | Sampler | Texture | Renderbuffer | Framebuffer
)


def _create_orthogonal_projection(
    left,
    right,
    bottom,
    top,
    near,
    far,
) -> array:
    rml = right - left
    tmb = top - bottom
    fmn = far - near

    A = 2.0 / rml
    B = 2.0 / tmb
    C = -2.0 / fmn
    Tx = -(right + left) / rml
    Ty = -(top + bottom) / tmb
    Tz = -(far + near) / fmn

    return array(
        "f",
        (
            A,
            0.0,
            0.0,
            0.0,
            0.0,
            B,
            0.0,
            0.0,
            0.0,
            0.0,
            C,
            0.0,
            Tx,
            Ty,
            Tz,
            1.0,
        ),
    )


def _extract_gl_errors() -> Iterator[int]:
    # glGetError does _not_ return the most error;
    # it turns out OpenGL maintains a queue of errors,
    # and glGetError pops the most recent one.
    err: int
    while (err := GL.glGetError()) != GL.GL_NO_ERROR:
        yield err


def _warn_unhandled_gl_errors():
    # Should be called as soon as possible after entering Python from the core;
    # unhandled OpenGL errors from the core must not hamper the frontend.
    unhandled_errors = tuple(_extract_gl_errors())
    if unhandled_errors:
        error_string = ", ".join(f"0x{e:X}" for e in unhandled_errors)
        warnings.warn(f"Core did not handle the following OpenGL errors: {error_string}")


def _clear_gl_errors():
    for i in _extract_gl_errors():
        pass


@final
class ModernGlVideoDriver(VideoDriver):
    def __init__(
        self,
        vertex_shader: str | None = None,
        fragment_shader: str | None = None,
        varyings: Sequence[str] = ("transformedTexCoord",),
        window: str | None = None,
        # TODO: Add ability to configure the OpenGL message callback
        # TODO: Add ability to configure the OpenGL debug group
        # TODO: Add ability to force an OpenGL version
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
        package_files = resources.files(modules[__name__].__package__)
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
        self._shader_program: moderngl.Program | None = None
        self._vao: VertexArray | None = None
        self._vbo: Buffer | None = None
        self._last_width: int | None = None
        self._last_height: int | None = None
        self._rotation: Rotation = Rotation.NONE

        # Framebuffer, color, and depth attachments for the "default" framebuffer
        # (equivalent to what a window would provide)
        self._fbo: Framebuffer | None = None
        self._color: Texture | None = None
        self._depth: Renderbuffer | None = None

        # Framebuffer, color, and depth attachments for the framebuffer
        # that the core will directly render to.
        # Will be copied to the default framebuffer for "display".
        self._hw_render_fbo: Framebuffer | None = None
        self._hw_render_color: Texture | None = None
        self._hw_render_depth: Renderbuffer | None = None

        # Texture for CPU-rendered output
        self._cpu_color: Texture | None = None

        self._get_proc_address = retro_hw_get_proc_address_t(self.get_proc_address)
        self._get_hw_framebuffer = retro_hw_get_current_framebuffer_t(
            lambda: self.current_framebuffer
        )

        self._window: BaseWindow | None = None
        self._window_class: type[BaseWindow] | None = None

        # TODO: Honor os.environ.get("MODERNGL_WINDOW")
        if window is not None and moderngl_window is not None:
            window_mode = _DEFAULT_WINDOW_IMPL if window == "default" else window
            if not isinstance(window, str):
                raise TypeError(f"Expected a str or None, got {type(window).__name__}")

            self._window_class = moderngl_window.get_local_window_cls(window_mode)

        self._debug_group_id = 0
        self.__gl_push_debug_group: Callable[[int, int, int, bytes], None] | None = None
        self.__gl_pop_debug_group: Callable[[], None] | None = None
        self.__gl_object_label: Callable[[int, int, int, bytes], None] | None = None

    def __del__(self):
        if self._cpu_color:
            del self._cpu_color

        if self._hw_render_depth:
            del self._hw_render_depth

        if self._hw_render_color:
            del self._hw_render_color

        if self._hw_render_fbo:
            del self._hw_render_fbo

        if self._depth:
            del self._depth

        if self._color:
            del self._color

        if self._fbo:
            del self._fbo

        if self._vbo:
            del self._vbo

        if self._vao:
            del self._vao

        if self._shader_program:
            del self._shader_program

        if self._context:
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

    @override
    @property
    def current_framebuffer(self) -> int | None:
        if self._hw_render_fbo:
            return self._hw_render_fbo.glo

        return 0

    @override
    def get_proc_address(self, sym: bytes) -> int | None:
        if not sym:
            return None

        if not self._context:
            raise RuntimeError("OpenGL context not initialized")

        # See here https://github.com/moderngl/glcontext?tab=readme-ov-file#structure
        proc: int | None = self._context.mglo._context.load_opengl_function(sym.decode())
        if proc is None:
            return None

        return proc

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        _clear_gl_errors()

        with self.__debug_group(b"libretro.ModernGlVideoDriver.refresh"):
            match data:
                case FrameBufferSpecial.DUPE:
                    # Do nothing, we're re-rendering the previous frame
                    # TODO: Re-render whichever framebuffer was most recently used
                    pass
                case FrameBufferSpecial.HARDWARE:
                    self._context.copy_framebuffer(self._color, self._hw_render_fbo)
                    self._hw_render_color.use()
                case memoryview():
                    self.__update_cpu_texture(data, width, height, pitch)
                    assert self._cpu_color is not None
                    self._cpu_color.use()

            self._context.viewport = (0, 0, width, height)
            matrix = _create_orthogonal_projection(-1, 1, 1, -1, -1, 1)
            self._shader_program["mvp"].write(matrix)

            self._fbo.use()
            self._color.use(1)

            self._vao.render(moderngl.TRIANGLE_STRIP)

            if self._window:
                with self.__debug_group(b"libretro.ModernGlVideoDriver.refresh.swap_buffers"):
                    self._window.fbo.use()
                    self._context.copy_framebuffer(self._window.fbo, self._fbo)
                    self._window.swap_buffers()

            self._context.finish()
            self._last_width = width
            self._last_height = height

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

        context_type = (
            HardwareContext(self._callback.context_type)
            if self._callback
            else HardwareContext.NONE
        )

        if context_type not in _CONTEXTS:
            raise RuntimeError(f"Unsupported hardware context: {context_type}")

        # TODO: Honor cache_context; try to avoid reinitializing the context
        if self._context:
            _clear_gl_errors()
            if self._callback and self._callback.context_destroy:
                # If the core wants to clean up before the context is destroyed...
                with self.__debug_group(b"libretro.ModernGlVideoDriver.reinit.context_destroy"):
                    self._callback.context_destroy()

            _warn_unhandled_gl_errors()

            if self._window:
                self._window.destroy()
                del self._window

            self._context.release()
            del self._context

            del self._hw_render_depth
            del self._hw_render_color
            del self._hw_render_fbo
            del self._vao
            del self._fbo
            del self._shader_program
            del self._vbo
            del self._cpu_color
            del self.__gl_push_debug_group
            del self.__gl_pop_debug_group
            del self.__gl_object_label
            # Destroy the OpenGL context and create a new one

        geometry = self._system_av_info.geometry

        match context_type, self._window_class:
            case HardwareContext.NONE, type() as window_class:
                self._window = window_class(
                    title="libretro.py",
                    size=(geometry.base_width, geometry.base_height),
                    resizable=False,
                    visible=True,
                    vsync=False,
                )
                moderngl_window.activate_context(self._window)
                self._context = self._window.ctx
            case HardwareContext.OPENGL, type() as window_class:
                self._window = window_class(
                    title="libretro.py",
                    gl_version=(2, 1),
                    size=(geometry.base_width, geometry.base_height),
                    resizable=False,
                    visible=True,
                    vsync=False,
                )
                moderngl_window.activate_context(self._window)
                self._context = self._window.ctx
            case HardwareContext.OPENGL_CORE, type() as window_class:
                self._window = window_class(
                    title="libretro.py",
                    gl_version=(self._callback.version_major, self._callback.version_minor),
                    size=(geometry.base_width, geometry.base_height),
                    resizable=False,
                    visible=True,
                    vsync=False,
                )
                moderngl_window.activate_context(self._window)
                self._context = self._window.ctx
            case HardwareContext.NONE, None:
                # Create a default context with OpenGL 3.3 core profile;
                # do not expose it to the core, only use it for software rendering
                self._context = create_context(standalone=True)
            case HardwareContext.OPENGL, None:
                self._context = create_context(require=210, standalone=True, share=self._shared)
            case HardwareContext.OPENGL_CORE, None:
                ver = self._callback.version_major * 100 + self._callback.version_minor * 10
                self._context = create_context(require=ver, standalone=True, share=self._shared)

        _clear_gl_errors()
        if self._context.version_code >= 430:
            self.__gl_push_debug_group = GL.glPushDebugGroup
            self.__gl_pop_debug_group = GL.glPopDebugGroup
            self.__gl_object_label = GL.glObjectLabel
            self._context.enable_direct(GL.GL_DEBUG_OUTPUT)
            self._context.enable_direct(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
        elif "GL_KHR_debug" in self._context.extensions and GL.glPushDebugGroupKHR:
            self.__gl_push_debug_group = GL.glPushDebugGroupKHR
            self.__gl_pop_debug_group = GL.glPopDebugGroupKHR
            self.__gl_object_label = GL.glObjectLabelKHR
            self._context.enable_direct(GL.GL_DEBUG_OUTPUT_KHR)
            self._context.enable_direct(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS_KHR)
            # TODO: Contribute this stuff to moderngl
        else:
            self.__gl_push_debug_group = None
            self.__gl_pop_debug_group = None
            self.__gl_object_label = None

        _clear_gl_errors()
        with self.__debug_group(b"libretro.ModernGlVideoDriver.reinit"):
            self._context.gc_mode = "auto"
            self.__init_fbo()

            self._shader_program = self._context.program(
                vertex_shader=self._vertex_shader,
                fragment_shader=self._fragment_shader,
                varyings=self._varyings,
                fragment_outputs={"pixelColor": 0},
            )

            mvp = array("f", _IDENTITY_MAT4)
            if not self._callback or not self._callback.bottom_left_origin:
                # If we're only using software rendering, or if we want the origin at the top-left...
                mvp[5] = -1  # ...then flip the screen vertically by negating the Y scale

            self._shader_program["mvp"].write(mvp)
            self._vbo = self._context.buffer(_VERTEXES)
            self._vao = self._context.vertex_array(
                self._shader_program, self._vbo, "vertexCoord", "texCoord"
            )
            # TODO: Make the particular names configurable

            self.__object_label(self._shader_program, b"libretro.py Shader Program")
            self.__object_label(self._vbo, b"libretro.py Screen VBO")
            self.__object_label(self._vao, b"libretro.py Screen VAO")

            # TODO: Honor debug_context; enable debugging features if requested
            if self._callback is not None and context_type != HardwareContext.NONE:
                # If the core specifically wants to render with the OpenGL API...
                self.__init_hw_render()

                if self._callback.context_reset:
                    # If the core wants to set up resources after the context is created...
                    _clear_gl_errors()
                    with self.__debug_group(b"libretro.ModernGlVideoDriver.reinit.context_reset"):
                        self._callback.context_reset()

                    _warn_unhandled_gl_errors()

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
    def geometry(self) -> retro_game_geometry | None:
        return deepcopy(self._system_av_info.geometry) if self._system_av_info else None

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
            if self._cpu_color:
                self._cpu_color.release()
                self._cpu_color = None

    @property
    @override
    def rotation(self) -> Rotation:
        return self._rotation

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        if not isinstance(rotation, (Rotation, int)):
            raise TypeError(f"Expected a Rotation, got {type(rotation).__name__}")

        if rotation not in Rotation:
            raise ValueError(f"Invalid rotation: {rotation}")

        self._rotation = rotation
        # TODO: Set the rotation matrix in the shader

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        if not self._system_av_info:
            return None

        return deepcopy(self._system_av_info)

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        if not isinstance(av_info, retro_system_av_info):
            raise TypeError(f"Expected a retro_system_av_info, got {type(av_info).__name__}")

        self._system_av_info = deepcopy(av_info)
        self.reinit()

    @override
    def screenshot(self, prerotate: bool = True) -> Screenshot | None:
        if self._system_av_info is None:
            return None

        _clear_gl_errors()
        with self.__debug_group(b"libretro.ModernGlVideoDriver.screenshot"):
            size = (self._last_width, self._last_height)
            if self._window:
                frame = self._window.fbo.read(size, 4)
            else:
                frame = self._fbo.read(size, 4)

            if frame is None:
                return None

            _clear_gl_errors()
            if not self._callback or not self._callback.bottom_left_origin:
                # If we're using software rendering or the origin is at the bottom-left...
                bytes_per_row = self._last_width * self._pixel_format.bytes_per_pixel
                reversed_frame = array("B", frame)
                reversed_frame_view = memoryview(reversed_frame)
                frame_view = memoryview(frame)
                frame_len = len(frame)
                for i in range(self._last_height):
                    # For each row...
                    start = i * bytes_per_row
                    end = start + bytes_per_row
                    reversed_frame_view[start:end] = frame_view[
                        frame_len - end : frame_len - start
                    ]
                    # ...copy row number (height - i) to row i

                frame = reversed_frame_view

            return Screenshot(
                memoryview(frame),
                self._last_width,
                self._last_height,
                self._rotation,
                self._pixel_format,
            )

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

    def __get_framebuffer_size(self) -> tuple[int, int]:
        # Equivalent to glGetIntegerv
        max_fbo_size = self._context.info["GL_MAX_TEXTURE_SIZE"]
        max_rb_size = self._context.info["GL_MAX_RENDERBUFFER_SIZE"]
        geometry = self._system_av_info.geometry

        if (
            geometry.max_width > max_rb_size
            or geometry.max_height > max_fbo_size
            or geometry.max_height > max_rb_size
            or geometry.max_width > max_fbo_size
        ):
            warnings.warn(
                f"Core-provided framebuffer size ({geometry.max_width}x{geometry.max_height}) exceeds GL_MAX_TEXTURE_SIZE ({max_fbo_size}) or GL_MAX_RENDERBUFFER_SIZE ({max_rb_size})"
            )

        width = min(geometry.max_width, max_fbo_size, max_rb_size)
        height = min(geometry.max_height, max_fbo_size, max_rb_size)
        return width, height

    def __init_fbo(self):
        with self.__debug_group(b"libretro.ModernGlVideoDriver.__init_fbo"):
            assert self._context is not None
            assert self._system_av_info is not None

            del self._fbo
            del self._color
            del self._depth

            geometry = self._system_av_info.geometry
            size = self.__get_framebuffer_size()

            # Similar to glGenTextures, glBindTexture, and glTexImage2D
            self._color = self._context.texture(size, 4)
            self._depth = self._context.depth_renderbuffer(size)

            # Similar to glGenFramebuffers, glBindFramebuffer, and glFramebufferTexture2D
            self._fbo = self._context.framebuffer(self._color, self._depth)

            self.__object_label(self._color, b"libretro.py Main FBO Color Attachment")
            self.__object_label(self._depth, b"libretro.py Main FBO Depth Attachment")
            self.__object_label(self._fbo, b"libretro.py Main FBO")

            self._fbo.viewport = (0, 0, geometry.base_width, geometry.base_height)
            self._fbo.scissor = (0, 0, geometry.base_width, geometry.base_height)
            self._fbo.clear()

        _clear_gl_errors()

    def __init_hw_render(self):
        with self.__debug_group(b"libretro.ModernGlVideoDriver.__init_hw_render"):
            assert self._context is not None
            assert self._callback is not None
            assert self._system_av_info is not None

            self._hw_render_fbo = None
            self._hw_render_color = None
            self._hw_render_depth = None

            size = self.__get_framebuffer_size()

            # Similar to glGenTextures, glBindTexture, and glTexImage2D
            self._hw_render_color = self._context.texture(size, 4)
            if self._callback.depth:
                # If the core is asking for a depth attachment...
                # Similar to glGenRenderbuffers, glBindRenderbuffer, and glRenderbufferStorage
                self._hw_render_depth = self._context.depth_renderbuffer(size)

                if self._callback.stencil:
                    warnings.warn(
                        "Core requested stencil attachment, but moderngl lacks support; ignoring"
                    )
                    # TODO: Implement stencil buffer support in moderngl

            # Similar to glGenFramebuffers, glBindFramebuffer, and glFramebufferTexture2D
            self._hw_render_fbo = self._context.framebuffer(
                self._hw_render_color, self._hw_render_depth
            )
            self._hw_render_fbo.clear()

            self.__object_label(self._hw_render_fbo, b"libretro.py Hardware Rendering FBO")
            self.__object_label(
                self._hw_render_color, b"libretro.py Hardware Rendering FBO Color Attachment"
            )
            if self._hw_render_depth:
                self.__object_label(
                    self._hw_render_depth, b"libretro.py Hardware Rendering FBO Depth Attachment"
                )

    def __update_cpu_texture(self, data: memoryview, width: int, height: int, pitch: int):
        with self.__debug_group(b"libretro.ModernGlVideoDriver.__update_cpu_texture"):
            if self._cpu_color and self._cpu_color.size == (width, height):
                # If we have a texture for CPU-rendered output, and it's the right size...
                self._cpu_color.write(data)
            else:
                del self._cpu_color

                # Equivalent to glGenTextures, glBindTexture, glTexImage2D, and glTexParameteri
                match self._pixel_format:
                    case PixelFormat.XRGB8888:
                        self._cpu_color = self._context.texture(
                            (width, height), 4, data
                        )  # GL_RGBA8
                        self._cpu_color.swizzle = "BGR1"
                    case PixelFormat.RGB565:
                        GL_RGB565 = 0x8D62
                        self._cpu_color = self._context.texture(
                            (width, height), 3, data, internal_format=GL_RGB565
                        )
                        # moderngl can't natively express GL_RGB565
                    case PixelFormat.RGB1555:
                        GL_RGB5 = 0x8050
                        self._cpu_color = self._context.texture(
                            (width, height), 3, data, internal_format=GL_RGB5
                        )
                        # moderngl can't natively express GL_RGB5

                self.__object_label(self._cpu_color, b"libretro.py CPU-Rendered Frame")

    def __object_label(self, obj: ModernGlResource, label: bytes):
        if self.__gl_object_label:
            # TODO: Honor self._callback.debug_context
            gltype: int
            match obj:
                case Buffer():
                    gltype = GL.GL_BUFFER
                case Program():
                    gltype = GL.GL_PROGRAM
                case VertexArray():
                    gltype = GL.GL_VERTEX_ARRAY
                case Query():
                    gltype = GL.GL_QUERY
                case Sampler():
                    gltype = GL.GL_SAMPLER
                case Texture():
                    gltype = GL.GL_TEXTURE
                case Renderbuffer():
                    gltype = GL.GL_RENDERBUFFER
                case Framebuffer():
                    gltype = GL.GL_FRAMEBUFFER
                case _:
                    raise TypeError(f"Unsupported object type: {type(obj).__name__}")

            self.__gl_object_label(gltype, obj.glo, -1, label)

    @contextmanager
    def __debug_group(self, label: bytes):
        if self.__gl_push_debug_group:
            self._debug_group_id = self._debug_group_id + 1
            self.__gl_push_debug_group(
                GL.GL_DEBUG_SOURCE_APPLICATION, self._debug_group_id, -1, label
            )
            yield None
            self.__gl_pop_debug_group()
            self._debug_group_id = self._debug_group_id - 1
        else:
            yield None


__all__ = ["ModernGlVideoDriver"]
