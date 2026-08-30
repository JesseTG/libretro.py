"""
:class:`.VideoDriver` implementation backed by :mod:`moderngl` and PyOpenGL.

.. seealso::

    :class:`.VideoDriver`
        The protocol this driver implements.
"""

# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
# ModernGL's typeshed stubs are very incomplete,
# and PyOpenGL doesn't have any at all.
# These two warnings silence a lot of noise.

from __future__ import annotations

import struct
import warnings
from array import array
from collections.abc import Iterator, Sequence, Set
from copy import deepcopy
from importlib import resources
from sys import modules
from typing import TYPE_CHECKING, cast, final, override

import moderngl
from OpenGL import GL
from OpenGL.error import GLError

from libretro.api.proc import retro_proc_address_t

if TYPE_CHECKING:
    import moderngl_window
    from moderngl_window.context.base import BaseWindow
else:
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
    Renderbuffer,
    Texture,
    Uniform,
    VertexArray,
    create_context,
)

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.video import (
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_render_callback,
    retro_hw_render_interface,
)

from ..driver import (
    FrameBufferSpecial,
    Screenshot,
    UnsupportedContextError,
    VideoDriver,
)

_CONTEXTS = frozenset((HardwareContext.NONE, HardwareContext.OPENGL_CORE, HardwareContext.OPENGL))

_DEFAULT_VERT_FILENAME = "moderngl_vertex.glsl"
_DEFAULT_FRAG_FILENAME = "moderngl_frag.glsl"

_vertex = struct.Struct("2f 2f")  # 4 floats (one vec2 for screen coords, one for vec2 coords)
_POSITION_NORTHWEST = (-1, 1)
_POSITION_NORTHEAST = (1, 1)
_POSITION_SOUTHWEST = (-1, -1)
_POSITION_SOUTHEAST = (1, -1)

_FULL_TEXCOORD_SCALE = (1.0, 1.0)
"""Texture coordinate scale for a texture that holds nothing but the frame."""


def _screen_quad(scale: tuple[float, float] = _FULL_TEXCOORD_SCALE) -> bytes:
    """
    Pack the screen quad's vertexes,
    sampling only the lower-left ``[0, u] x [0, v]`` corner of the bound texture.

    The texture a hardware-rendering core draws into is allocated for its
    :attr:`~.retro_game_geometry.max_width` by :attr:`~.retro_game_geometry.max_height`
    geometry, but the core only fills the corner described by the geometry of the
    frame it just rendered; ``scale`` is the ratio between the two.
    Sampling the whole texture would shrink the frame by that same ratio
    and pad it with texels that the core never rendered to.

    :param scale: The fraction of the bound texture that the frame occupies,
        as ``(horizontal, vertical)``.
        Both components are 1 for a texture sized to the frame exactly.
    """
    u, v = scale
    return b"".join(
        (
            _vertex.pack(*_POSITION_NORTHWEST, 0.0, v),
            _vertex.pack(*_POSITION_SOUTHWEST, 0.0, 0.0),
            _vertex.pack(*_POSITION_NORTHEAST, u, v),
            _vertex.pack(*_POSITION_SOUTHEAST, u, 0.0),
        )
    )


_VERTEXES = _screen_quad()

_SCREENSHOT_COMPONENTS = 4
"""Components per pixel read back by :meth:`.ModernGlVideoDriver.screenshot`."""

_DEFAULT_WINDOW_IMPL = "pyglet"

_MVP_UPRIGHT = array("f", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
"""Draws the bound texture as it stands, for one whose first row is its bottom row."""

_MVP_FLIPPED = array("f", [1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
"""Draws the bound texture upside down, for one whose first row is its top row."""

GL_RGBA = 0x1908


def _get_gl_error() -> int:
    try:
        return cast(int, GL.glGetError())
    except GLError as e:
        return cast(int, e.err)


def _extract_gl_errors() -> Iterator[int]:
    # glGetError does _not_ return the most error;
    # it turns out OpenGL maintains a queue of errors,
    # and glGetError pops the most recent one.
    err: int
    while (err := _get_gl_error()) != GL.GL_NO_ERROR:
        yield err


def _gl_error_str(code: int) -> str:
    match code:
        case GL.GL_NO_ERROR:
            return "GL_NO_ERROR"
        case GL.GL_INVALID_ENUM:
            return "GL_INVALID_ENUM"
        case GL.GL_INVALID_VALUE:
            return "GL_INVALID_VALUE"
        case GL.GL_INVALID_OPERATION:
            return "GL_INVALID_OPERATION"
        case GL.GL_STACK_OVERFLOW:
            return "GL_STACK_OVERFLOW"
        case GL.GL_STACK_UNDERFLOW:
            return "GL_STACK_UNDERFLOW"
        case GL.GL_OUT_OF_MEMORY:
            return "GL_OUT_OF_MEMORY"
        case GL.GL_INVALID_FRAMEBUFFER_OPERATION:
            return "GL_INVALID_FRAMEBUFFER_OPERATION"
        case GL.GL_CONTEXT_LOST:
            return "GL_CONTEXT_LOST"
        case _:
            return f"0x{code:X}"


def _warn_unhandled_gl_errors():
    # Should be called as soon as possible after entering Python from the core;
    # unhandled OpenGL errors from the core must not hamper the frontend.
    unhandled_errors = tuple(_extract_gl_errors())
    if unhandled_errors:
        error_string = ", ".join(_gl_error_str(e) for e in unhandled_errors)
        warnings.warn(f"Core did not handle the following OpenGL errors: {error_string}")


@final
class ModernGlVideoDriver(VideoDriver):
    """
    A video driver that exposes an OpenGL context to the :term:`core`
    via :mod:`moderngl` and PyOpenGL.
    """

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
        Initialize the video driver.
        Does not create an OpenGL context; that will occur when :meth:`reinit` is called.

        This driver uses a basic shader program, but custom shaders can be provided.

        :warning: The shaders are not compiled or linked until the OpenGL context is created,
            so GLSL errors won't be detected until then.

        :param vertex_shader: The GLSL source of the vertex shader to use for rendering,
            or :obj:`None` to use the built-in default.
        :param fragment_shader: The GLSL source of the fragment shader to use for rendering,
            or :obj:`None` to use the built-in default.
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
        self._pixel_format = PixelFormat.RGB1555
        self._system_av_info: retro_system_av_info | None = None
        self._shared = False
        self._context: Context | None = None
        self._shader_program: moderngl.Program | None = None
        self._vao: VertexArray | None = None
        self._vbo: Buffer | None = None
        self._last_size: tuple[int, int] | None = None
        self._texcoord_scale: tuple[float, float] = _FULL_TEXCOORD_SCALE
        self._mvp_uniform: Uniform | None = None
        self._flipped: bool | None = None
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

        # Objects for the window, if requested
        self._window: BaseWindow | None = None
        self._window_class: type[BaseWindow] | None = None

        # TODO: Honor os.environ.get("MODERNGL_WINDOW")
        if window is not None and moderngl_window is not None:
            window_mode = _DEFAULT_WINDOW_IMPL if window == "default" else window
            if not isinstance(window, str):
                raise TypeError(f"Expected a str or None, got {type(window).__name__}")

            self._window_class = moderngl_window.get_local_window_cls(window_mode)

    def __del__(self):
        """Clean up allocated OpenGL resources and the underlying context."""
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
    def set_context(self, callback: retro_hw_render_callback) -> None:
        if callback is None:
            return None

        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        context_type = HardwareContext(callback.context_type)
        if context_type not in _CONTEXTS:
            raise UnsupportedContextError(
                f"Unsupported hardware context: {context_type} (must be one of: {_CONTEXTS})"
            )

        self._callback = deepcopy(callback)

    @property
    @override
    def current_framebuffer(self) -> int | None:
        if self._hw_render_fbo:
            return self._hw_render_fbo.glo

        return 0

    @override
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if not sym:
            return None

        if not self._context:
            raise RuntimeError("OpenGL context not initialized")

        # See here https://github.com/moderngl/glcontext?tab=readme-ov-file#structure
        proc: int | None = self._context.mglo._context.load_opengl_function(sym.decode())
        if proc is None:
            return None

        return retro_proc_address_t(proc)

    @override
    def refresh(
        self, data: memoryview[int] | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        if not self._context:
            raise RuntimeError("OpenGL context not initialized")

        _warn_unhandled_gl_errors()

        with self._context.debug_scope("libretro.ModernGlVideoDriver.refresh"):
            match data:
                case FrameBufferSpecial.DUPE:
                    # Do nothing, we're re-rendering the previous frame
                    # TODO: Re-render whichever framebuffer was most recently used
                    pass
                case FrameBufferSpecial.HARDWARE:
                    assert self._hw_render_color is not None, (
                        "Hardware render color buffer should have been initialized in reinit() by now"
                    )
                    # The quad below redraws every pixel this frame occupies,
                    # so blitting the hardware framebuffer over first would be wasted work.
                    # It would be *expensive* wasted work, too:
                    # both surfaces are allocated for the core's maximum geometry,
                    # which is usually far larger than a single frame.
                    self._hw_render_color.use()
                    # This texture is sized for the core's *maximum* geometry,
                    # but the core only rendered into the corner
                    # described by *this frame's* geometry.
                    hw_width, hw_height = cast(tuple[int, int], self._hw_render_color.size)
                    self.__set_texcoord_scale(width / hw_width, height / hw_height)
                    # A hardware frame sits in its texture whichever way up
                    # the core said it would render.
                    self.__set_flip(not self._callback or not self._callback.bottom_left_origin)
                case memoryview():
                    self.__update_cpu_texture(data, width, height, pitch)
                    assert self._cpu_color is not None, (
                        "CPU-rendered color buffer should have been initialized in reinit() by now"
                    )
                    self._cpu_color.use()
                    # This texture is allocated at exactly the frame's size,
                    # so all of it is the frame.
                    self.__set_texcoord_scale(*_FULL_TEXCOORD_SCALE)
                    # A software frame always arrives top row first,
                    # even from a core that renders in hardware the rest of the time.
                    self.__set_flip(True)

            assert self._shader_program is not None, (
                "Shader program should have been initialized in reinit() by now"
            )
            assert self._vao is not None, "VAO should have been initialized in reinit() by now"

            # A core may resize its output between frames with SET_GEOMETRY,
            # so aim at the frame that was just handed over
            # rather than at the geometry this framebuffer was created with,
            # growing the framebuffer first if the frame has outgrown it.
            self.__resize_fbo(width, height)
            assert self._fbo is not None, "FBO should have been initialized in reinit() by now"

            # These belong on the framebuffer and not on the context:
            # Framebuffer.use() re-applies its own viewport and scissor,
            # which would undo anything set through Context.viewport here.
            self._fbo.viewport = (0, 0, width, height)
            self._fbo.scissor = (0, 0, width, height)
            self._fbo.use()

            self._vao.render(moderngl.TRIANGLE_STRIP)

            if self._window:
                with self._context.debug_scope(
                    "libretro.ModernGlVideoDriver.refresh.swap_buffers"
                ):
                    self._window.fbo.use()
                    self._context.copy_framebuffer(self._window.fbo, self._fbo)

                    # swap_buffers() also pumps window events, and pyglet's
                    # resize/scale handlers update their "WindowBlock" UBO and
                    # leave it bound to uniform-buffer binding 0 -- an indexed
                    # binding that belongs to the core between frames.
                    # melonDS, for one, binds its 3D config UBO there exactly
                    # once at startup, so a single clobber would black out its
                    # 3D renderer for the rest of the session.

                    bound_ubo = int(GL.glGetIntegeri_v(GL.GL_UNIFORM_BUFFER_BINDING, 0))  # type: ignore
                    self._window.swap_buffers()
                    GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, 0, bound_ubo)

            # Scissoring is context-wide state that outlives this call, and the next
            # thing to draw through this context is usually the core.
            # Left enabled, it clips the core's own rendering to the corner
            # that the frame just presented happened to occupy.
            self._context.scissor = None

            self._context.finish()
            self._last_size = (width, height)

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

        if self._callback:
            context_type = HardwareContext(self._callback.context_type)
            if context_type not in _CONTEXTS:
                raise RuntimeError(f"Unsupported hardware context: {context_type}")
        else:
            context_type = HardwareContext.NONE

        # TODO: Honor cache_context; try to avoid reinitializing the context
        if self._context:
            self._context.clear_errors()
            if self._callback and self._callback.context_destroy:
                # If the core wants to clean up before the context is destroyed...
                with self._context.debug_scope(
                    "libretro.ModernGlVideoDriver.reinit.context_destroy"
                ):
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
                assert self._callback is not None, (
                    "Should've been set by the core, or else this branch wouldn't have been taken"
                )
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
                assert self._callback is not None, (
                    "Should've been set by the core, or else this branch wouldn't have been taken"
                )
                ver = self._callback.version_major * 100 + self._callback.version_minor * 10
                self._context = create_context(require=ver, standalone=True, share=self._shared)

        self._context.clear_errors()
        if self._context.version_code >= 430:
            self._context.enable_direct(cast(int, GL.GL_DEBUG_OUTPUT))
            self._context.enable_direct(cast(int, GL.GL_DEBUG_OUTPUT_SYNCHRONOUS))
        elif "GL_KHR_debug" in self._context.extensions and GL.glPushDebugGroupKHR:
            self._context.enable_direct(cast(int, GL.GL_DEBUG_OUTPUT_KHR))
            self._context.enable_direct(cast(int, GL.GL_DEBUG_OUTPUT_SYNCHRONOUS_KHR))
            # TODO: Contribute this stuff to moderngl

        self._context.clear_errors()
        with self._context.debug_scope("libretro.ModernGlVideoDriver.reinit"):
            self._context.gc_mode = "auto"
            self.__init_fbo(*self.__get_presentation_size())

            self._shader_program = self._context.program(
                vertex_shader=self._vertex_shader,
                fragment_shader=self._fragment_shader,
                varyings=self._varyings,
                fragment_outputs={"pixelColor": 0},
            )

            mvp_uniform = self._shader_program.get("mvp", None)
            if not isinstance(mvp_uniform, Uniform):
                raise RuntimeError(
                    f"Expected shader program to have an 'mvp' uniform, but it was a {type(mvp_uniform).__name__} or not present at all"
                )

            self._mvp_uniform = mvp_uniform
            # refresh() picks the right one for each frame as it arrives,
            # but a core whose very first frame is a duplicate never gets there,
            # so start with the one that frame would most likely have called for.
            self._flipped = None
            self.__set_flip(not self._callback or not self._callback.bottom_left_origin)

            self._vbo = self._context.buffer(_VERTEXES)
            self._texcoord_scale = _FULL_TEXCOORD_SCALE
            self._vao = self._context.vertex_array(
                self._shader_program, self._vbo, "vertexCoord", "texCoord"
            )
            # TODO: Make the particular names configurable

            self._shader_program.label = "libretro.py Shader Program"
            self._vbo.label = "libretro.py Screen VBO"
            self._vao.label = "libretro.py Screen VAO"

            # TODO: Honor debug_context; enable debugging features if requested
            if self._callback is not None and context_type != HardwareContext.NONE:
                # If the core specifically wants to render with the OpenGL API...
                self.__init_hw_render()

                if self._callback.context_reset:
                    # If the core wants to set up resources after the context is created...
                    self._context.clear_errors()
                    with self._context.debug_scope(
                        "libretro.ModernGlVideoDriver.reinit.context_reset"
                    ):
                        self._callback.context_reset()
                        _warn_unhandled_gl_errors()

    @property
    @override
    def supported_contexts(self) -> Set[HardwareContext]:
        return _CONTEXTS

    @property
    @override
    def preferred_context(self) -> HardwareContext | None:
        return HardwareContext.OPENGL_CORE

    @property
    @override
    def active_context(self) -> HardwareContext:
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
        # No OpenGL state to update here:
        # refresh() aims the viewport and scissor at each frame as it arrives,
        # which covers a resize whether it came through here
        # or from a core that simply varied its output size.

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

        if not self._context:
            return None

        if not self._last_size:
            return None

        self._context.clear_errors()
        with self._context.debug_scope("libretro.ModernGlVideoDriver.screenshot"):
            if self._window:
                frame = self._window.fbo.read(self._last_size, _SCREENSHOT_COMPONENTS)
            else:
                if not self._fbo:
                    return None

                frame = self._fbo.read(self._last_size, _SCREENSHOT_COMPONENTS)

            self._context.clear_errors()
            if frame is None:
                return None

            # Whichever way up the core renders, the framebuffer just read from
            # holds the frame the right way up: refresh() turns each frame over
            # as it draws it, if that's what the frame needs.
            # OpenGL hands back its rows bottom-first, though, and a screenshot runs
            # top-down like a software frame, so the rows are reversed unconditionally.
            bytes_per_row = self._last_size[0] * _SCREENSHOT_COMPONENTS
            reversed_frame = array("B", frame)
            reversed_frame_view = memoryview(reversed_frame)
            frame_view = memoryview(frame)
            frame_len = len(frame)
            for i in range(self._last_size[1]):
                # For each row...
                start = i * bytes_per_row
                end = start + bytes_per_row
                reversed_frame_view[start:end] = frame_view[frame_len - end : frame_len - start]
                # ...copy row number (height - i) to row i

            return Screenshot(
                memoryview(reversed_frame_view),
                self._last_size[0],
                self._last_size[1],
                self._rotation,
                self._pixel_format,
            )

    @property
    @override
    def shared_context(self) -> bool:
        return self._shared

    @shared_context.setter
    @override
    def shared_context(self, value: bool) -> None:
        self._shared = bool(value)

    @property
    @override
    def can_dupe(self) -> bool:
        return True

    @override
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        # TODO: Map the OpenGL texture to a software framebuffer
        pass

    @property
    @override
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        # libretro doesn't define one of these for OpenGL, so no need
        return None

    def __set_flip(self, flip: bool) -> None:
        """
        Choose whether the screen quad turns the bound texture over as it draws it.

        The quad's texture coordinates run bottom-up, like OpenGL's own origin,
        so a texture whose first row is its *top* row has to be flipped back over.
        Which of the two applies depends on where the frame came from,
        not on the driver's configuration:
        a core that renders in hardware may still hand over software frames
        (a software menu over a hardware-rendered game does exactly this),
        and those arrive top row first no matter which origin the core asked for.

        Rewrites the uniform only when the answer actually changes,
        which in practice is only when a core switches between the two paths.
        """
        if self._flipped == flip:
            return

        assert self._mvp_uniform is not None, (
            "MVP uniform should have been looked up in reinit() by now"
        )
        self._mvp_uniform.write(_MVP_FLIPPED if flip else _MVP_UPRIGHT)
        self._flipped = flip

    def __set_texcoord_scale(self, u: float, v: float) -> None:
        """
        Aim the screen quad at the lower-left ``[0, u] x [0, v]`` corner of the bound texture.

        Rewrites the vertex buffer only when the scale actually changes,
        which in practice is once per geometry change.
        See ``_screen_quad`` for where these coordinates come from.
        """
        # Clamp, in case a core reports a frame larger than the geometry it declared
        # or its maximum geometry had to be clipped to fit GL_MAX_TEXTURE_SIZE;
        # sampling past the edge of the texture would show garbage.
        scale = (min(u, 1.0), min(v, 1.0))
        if self._texcoord_scale == scale:
            return

        assert self._vbo is not None, "VBO should have been initialized in reinit() by now"
        self._vbo.write(_screen_quad(scale))
        self._texcoord_scale = scale

    def __get_framebuffer_size(self) -> tuple[int, int]:
        assert self._context is not None
        assert self._system_av_info is not None
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

    def __get_presentation_size(self) -> tuple[int, int]:
        """
        Return the size to give the framebuffer that frames are presented in.

        Unlike the framebuffer that a hardware-rendering core draws into,
        this one only ever holds a single frame,
        so it's allocated for the geometry frames arrive at
        rather than for the largest geometry the core is allowed to use.
        Cores routinely declare a maximum many times the size of the frames they emit,
        and every pixel of that surplus costs time on each frame
        it's carried through the driver.
        :meth:`__resize_fbo` grows it if a frame ever arrives that doesn't fit.
        """
        assert self._system_av_info is not None
        max_width, max_height = self.__get_framebuffer_size()
        geometry = self._system_av_info.geometry
        return min(geometry.base_width, max_width), min(geometry.base_height, max_height)

    def __resize_fbo(self, width: int, height: int) -> None:
        """Grow the presentation framebuffer if a frame arrives that overflows it."""
        assert self._fbo is not None
        fbo_width, fbo_height = self._fbo.size
        if width <= fbo_width and height <= fbo_height:
            return

        # Never shrink, and never exceed what the core said it would need.
        max_width, max_height = self.__get_framebuffer_size()
        self.__init_fbo(
            min(max(width, fbo_width), max_width),
            min(max(height, fbo_height), max_height),
        )

    def __init_fbo(self, width: int, height: int):
        assert self._context is not None
        with self._context.debug_scope("libretro.ModernGlVideoDriver.__init_fbo"):
            del self._fbo
            del self._color
            del self._depth

            size = (width, height)

            # Similar to glGenTextures, glBindTexture, and glTexImage2D
            self._color = self._context.texture(size, 4)
            self._depth = self._context.depth_renderbuffer(size)

            # Similar to glGenFramebuffers, glBindFramebuffer, and glFramebufferTexture2D
            self._fbo = self._context.framebuffer(self._color, self._depth)

            self._color.label = "libretro.py Main FBO Color Attachment"
            self._depth.label = "libretro.py Main FBO Depth Attachment"
            self._fbo.label = "libretro.py Main FBO"

            self._fbo.viewport = (0, 0, width, height)
            self._fbo.scissor = (0, 0, width, height)
            self._fbo.clear()

        self._context.clear_errors()

    def __init_hw_render(self):
        assert self._context is not None
        with self._context.debug_scope("libretro.ModernGlVideoDriver.__init_hw_render"):
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

            self._hw_render_fbo.label = "libretro.py Hardware Rendering FBO"
            self._hw_render_color.label = "libretro.py Hardware Rendering FBO Color Attachment"
            if self._hw_render_depth:
                self._hw_render_depth.label = "libretro.py Hardware Rendering FBO Depth Attachment"

    def __update_cpu_texture(self, data: memoryview[int], width: int, height: int, _pitch: int):
        assert self._context is not None
        with self._context.debug_scope("libretro.ModernGlVideoDriver.__update_cpu_texture"):
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
                    case _:
                        # The 10-bit formats have no texture mapping here yet;
                        # fail loudly instead of leaving self._cpu_color unset
                        raise ValueError(f"{self._pixel_format!r} frames aren't supported")

                self._cpu_color.label = "libretro.py CPU-Rendered Frame"


__all__ = ["ModernGlVideoDriver"]
