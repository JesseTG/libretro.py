"""
Headless Vulkan :class:`.VideoDriver` built on the :mod:`vulkan` package (CFFI bindings).

Implements the frontend side of ``libretro_vulkan.h``:
the context negotiation interface
and the version 5 :class:`.retro_hw_render_interface_vulkan`.
There is no window or swapchain;
each hardware frame is copied from the core's image
into host memory so that :meth:`.VulkanVideoDriver.screenshot` works,
mirroring the offscreen default of :class:`.ModernGlVideoDriver`.
"""

# The vulkan package is untyped CFFI, so the "unknown type" family of checks
# reports every use of it; relax those (and only those) for this module.
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false, reportUnknownParameterType=false
# pyright: reportMissingParameterType=false, reportMissingTypeStubs=false

from __future__ import annotations

import ctypes
import threading
from collections.abc import Set
from contextlib import suppress
from copy import deepcopy
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_int,
    c_uint32,
    c_void_p,
)
from typing import Any, final, override
from warnings import warn

import vulkan as vk
from vulkan import ffi

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t
from libretro.api.video import (
    RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION,
    HardwareContext,
    HardwareRenderInterfaceType,
    MemoryAccess,
    PixelFormat,
    Rotation,
    VkApplicationInfo,
    VkPhysicalDeviceFeatures,
    retro_framebuffer,
    retro_hw_context_reset_t,
    retro_hw_render_callback,
    retro_hw_render_context_negotiation_interface,
    retro_hw_render_context_negotiation_interface_vulkan,
    retro_hw_render_interface_vulkan,
    retro_vulkan_context,
    retro_vulkan_create_device_wrapper_t,
    retro_vulkan_create_instance_wrapper_t,
    retro_vulkan_get_sync_index_mask_t,
    retro_vulkan_get_sync_index_t,
    retro_vulkan_image,
    retro_vulkan_lock_queue_t,
    retro_vulkan_set_command_buffers_t,
    retro_vulkan_set_image_t,
    retro_vulkan_set_signal_semaphore_t,
    retro_vulkan_unlock_queue_t,
    retro_vulkan_wait_sync_index_t,
)

from ..driver import FrameBufferSpecial, Screenshot, UnsupportedContextError, VideoDriver
from ..software import ArrayVideoDriver

_CONTEXTS = frozenset((HardwareContext.NONE, HardwareContext.VULKAN))

_VK_API_VERSION_1_1 = (1 << 22) | (1 << 12)
_VK_FORMAT_R5G6B5_UNORM_PACK16 = 4
_VK_FORMAT_B5G6R5_UNORM_PACK16 = 5
_VK_FORMAT_A1R5G5B5_UNORM_PACK16 = 8
_VK_FORMAT_R8G8B8A8_UNORM = 37
_VK_FORMAT_R8G8B8A8_SRGB = 43
_VK_FORMAT_B8G8R8A8_UNORM = 44
_VK_FORMAT_B8G8R8A8_SRGB = 50
_VK_FORMAT_A2R10G10B10_UNORM_PACK32 = 58
_VK_FORMAT_A2B10G10R10_UNORM_PACK32 = 64

# Formats the capture path can copy and convert to RGBA bytes,
# mapped to their texel size in bytes.
# (Beetle PSX HW scans out A1R5G5B5 when dithering is enabled;
# Dolphin scans out A2B10G10R10.)
_CAPTURABLE_FORMATS: dict[int, int] = {
    _VK_FORMAT_R8G8B8A8_UNORM: 4,
    _VK_FORMAT_R8G8B8A8_SRGB: 4,
    _VK_FORMAT_B8G8R8A8_UNORM: 4,
    _VK_FORMAT_B8G8R8A8_SRGB: 4,
    _VK_FORMAT_A2R10G10B10_UNORM_PACK32: 4,
    _VK_FORMAT_A2B10G10R10_UNORM_PACK32: 4,
    _VK_FORMAT_R5G6B5_UNORM_PACK16: 2,
    _VK_FORMAT_B5G6R5_UNORM_PACK16: 2,
    _VK_FORMAT_A1R5G5B5_UNORM_PACK16: 2,
}

_LOADER_NAMES = ("libvulkan.so.1", "vulkan-1.dll", "libvulkan.dylib", "libvulkan.1.dylib")

_VK_KHR_SURFACE = "VK_KHR_surface"
_VK_EXT_HEADLESS_SURFACE = "VK_EXT_headless_surface"

_PFN_GetInstanceProcAddr = CFUNCTYPE(c_void_p, c_void_p, c_char_p)


def _wanted_instance_extensions(available: set[str]) -> tuple[list[str], int]:
    """Return the instance extensions this driver enables (of those available), plus create flags."""
    extensions: list[str] = []
    flags = 0
    if vk.VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME in available:
        extensions.append(vk.VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME)
        flags |= vk.VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR

    if vk.VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME in available:
        extensions.append(vk.VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME)

    if _VK_KHR_SURFACE in available:
        # Some cores (e.g. PPSSPP) assume create_device receives a real surface
        # and query surface support during queue selection;
        # a headless surface satisfies them without a window
        extensions.append(_VK_KHR_SURFACE)
        if _VK_EXT_HEADLESS_SURFACE in available:
            extensions.append(_VK_EXT_HEADLESS_SURFACE)

    return extensions, flags


class _VkInstanceCreateInfo(Structure):
    # Only used to read the create info a core passes to the create_instance wrapper
    _fields_ = (
        ("sType", c_int),
        ("pNext", c_void_p),
        ("flags", c_uint32),
        ("pApplicationInfo", POINTER(VkApplicationInfo)),
        ("enabledLayerCount", c_uint32),
        ("ppEnabledLayerNames", POINTER(c_char_p)),
        ("enabledExtensionCount", c_uint32),
        ("ppEnabledExtensionNames", POINTER(c_char_p)),
    )


class _VkDeviceCreateInfo(Structure):
    # Only used to read the create info a core passes to the create_device wrapper
    _fields_ = (
        ("sType", c_int),
        ("pNext", c_void_p),
        ("flags", c_uint32),
        ("queueCreateInfoCount", c_uint32),
        ("pQueueCreateInfos", c_void_p),
        ("enabledLayerCount", c_uint32),
        ("ppEnabledLayerNames", POINTER(c_char_p)),
        ("enabledExtensionCount", c_uint32),
        ("ppEnabledExtensionNames", POINTER(c_char_p)),
        ("pEnabledFeatures", POINTER(VkPhysicalDeviceFeatures)),
    )


def _raw(handle) -> int:
    """Return the integer value of a CFFI Vulkan handle (0 for None)."""
    if handle is None:
        return 0

    return int(ffi.cast("uintptr_t", handle))


# Interface structs whose Python callbacks have been replaced with native stubs;
# kept alive forever because cores may hold the pointer in exit-time destructors
_RETIRED_INTERFACES: list[retro_hw_render_interface_vulkan] = []


def _retire_interface(interface: retro_hw_render_interface_vulkan) -> None:
    """
    Replace an interface's Python callbacks with a harmless native function
    and keep the struct alive for the rest of the process.

    Some cores (e.g. mupen64plus-next's paraLLEl-RDP runtime) hold onto the
    interface pointer in objects destroyed at process exit, calling
    ``lock_queue``/``wait_sync_index`` after the Python interpreter has
    finalized — which would crash if they still pointed at ctypes closures.
    ``free`` is a safe stand-in: every callback receives this driver's
    ``handle``, which is ``NULL``, and ``free(NULL)`` is a no-op.
    """
    libc = ctypes.CDLL(None)
    noop = ctypes.cast(libc.free, c_void_p).value
    assert noop is not None
    interface.set_image = ctypes.cast(noop, retro_vulkan_set_image_t)
    interface.get_sync_index = ctypes.cast(noop, retro_vulkan_get_sync_index_t)
    interface.get_sync_index_mask = ctypes.cast(noop, retro_vulkan_get_sync_index_mask_t)
    interface.set_command_buffers = ctypes.cast(noop, retro_vulkan_set_command_buffers_t)
    interface.wait_sync_index = ctypes.cast(noop, retro_vulkan_wait_sync_index_t)
    interface.lock_queue = ctypes.cast(noop, retro_vulkan_lock_queue_t)
    interface.unlock_queue = ctypes.cast(noop, retro_vulkan_unlock_queue_t)
    interface.set_signal_semaphore = ctypes.cast(noop, retro_vulkan_set_signal_semaphore_t)
    _RETIRED_INTERFACES.append(interface)


def _load_loader() -> ctypes.CDLL:
    for name in _LOADER_NAMES:
        try:
            return ctypes.CDLL(name)
        except OSError:
            continue

    raise RuntimeError(
        "Couldn't load the Vulkan loader library; "
        "install the Vulkan SDK or (on macOS) MoltenVK, "
        "and ensure it's on the dynamic library search path"
    )


_RGBA_LUTS: dict[int, list[bytes]] = {}


def _pack16_lut(vk_format: int) -> list[bytes]:
    """Return (and cache) a 65536-entry texel-to-RGBA lookup table for a 16-bit format."""
    lut = _RGBA_LUTS.get(vk_format)
    if lut is not None:
        return lut

    def expand5(v: int) -> int:
        return (v << 3) | (v >> 2)

    def expand6(v: int) -> int:
        return (v << 2) | (v >> 4)

    entries = []
    for texel in range(0x10000):
        match vk_format:
            case _ if vk_format == _VK_FORMAT_R5G6B5_UNORM_PACK16:
                r = expand5(texel >> 11)
                g = expand6((texel >> 5) & 0x3F)
                b = expand5(texel & 0x1F)
            case _ if vk_format == _VK_FORMAT_B5G6R5_UNORM_PACK16:
                b = expand5(texel >> 11)
                g = expand6((texel >> 5) & 0x3F)
                r = expand5(texel & 0x1F)
            case _:  # A1R5G5B5
                r = expand5((texel >> 10) & 0x1F)
                g = expand5((texel >> 5) & 0x1F)
                b = expand5(texel & 0x1F)
        entries.append(bytes((r, g, b, 255)))

    _RGBA_LUTS[vk_format] = entries
    return entries


def _to_rgba32(pixels: bytearray, vk_format: int) -> bytearray:
    """Convert captured texels in a supported format to R, G, B, A byte order."""
    match _CAPTURABLE_FORMATS[vk_format]:
        case 2:
            lut = _pack16_lut(vk_format)
            texels = memoryview(pixels).cast("H")
            return bytearray(b"".join(map(lut.__getitem__, texels)))
        case _ if vk_format in (
            _VK_FORMAT_A2R10G10B10_UNORM_PACK32,
            _VK_FORMAT_A2B10G10R10_UNORM_PACK32,
        ):
            rgba = bytearray(len(pixels))
            red_first = vk_format == _VK_FORMAT_A2B10G10R10_UNORM_PACK32
            i = 0
            for texel in memoryview(pixels).cast("I"):
                low = (texel & 0x3FF) >> 2
                mid = (texel >> 10 & 0x3FF) >> 2
                high = (texel >> 20 & 0x3FF) >> 2
                if red_first:
                    rgba[i] = low
                    rgba[i + 2] = high
                else:
                    rgba[i] = high
                    rgba[i + 2] = low
                rgba[i + 1] = mid
                rgba[i + 3] = 255
                i += 4

            return rgba
        case _:
            rgba = bytearray(pixels)
            if vk_format in (_VK_FORMAT_B8G8R8A8_UNORM, _VK_FORMAT_B8G8R8A8_SRGB):
                # B, G, R, A: swap the red and blue channels
                rgba[0::4], rgba[2::4] = rgba[2::4], rgba[0::4]

            return rgba


def _rotate_rgba32(
    src: bytearray, width: int, height: int, rotation: Rotation
) -> tuple[bytearray, int, int]:
    """Rotate a tightly-packed 4-byte-per-pixel buffer, returning it with its new dimensions."""
    if rotation == Rotation.NONE:
        return src, width, height

    out = bytearray(len(src))
    match rotation:
        case Rotation.NINETY:
            start_y = (width - 1) * height * 4
            delta_x = height * -4
            delta_y = 4
            sideways = True
        case Rotation.ONE_EIGHTY:
            start_y = width * height * 4 - 4
            delta_x = -4
            delta_y = width * -4
            sideways = False
        case Rotation.TWO_SEVENTY:
            start_y = (height - 1) * 4
            delta_x = height * 4
            delta_y = -4
            sideways = True
        case _:
            raise ValueError(f"Invalid rotation: {rotation}")

    i = 0
    for y in range(height):
        o = start_y + y * delta_y
        for _ in range(width):
            out[o : o + 4] = src[i : i + 4]
            i += 4
            o += delta_x

    if sideways:
        return out, height, width

    return out, width, height


@final
class VulkanVideoDriver(VideoDriver):
    """
    A headless Vulkan video driver for hardware-rendered cores.

    Cores render into their own :c:type:`VkImage`
    and pass it to the driver with ``set_image``;
    the driver copies the visible region into host memory each frame,
    which backs :meth:`~.VulkanVideoDriver.screenshot`.
    Software-rendered frames are supported as well,
    with the same semantics as :class:`.ArrayVideoDriver`.
    """

    def __init__(self, *, sync_indices: int = 2, gpu_index: int = 0):
        """
        Initialize the driver without creating any Vulkan objects;
        those are created in :meth:`~.VulkanVideoDriver.reinit`.

        :param sync_indices: The number of frame-in-flight indices
            reported through ``get_sync_index_mask``.
        :param gpu_index: The index of the physical device to use,
            in the order reported by :c:func:`vkEnumeratePhysicalDevices`.

        :raises ValueError: If ``sync_indices`` is not between 1 and 32,
            or if ``gpu_index`` is negative.
        """
        if not (1 <= sync_indices <= 32):
            raise ValueError(f"Expected 1 <= sync_indices <= 32, got {sync_indices}")

        if gpu_index < 0:
            raise ValueError(f"Expected a non-negative gpu_index, got {gpu_index}")

        self._sync_index_count = sync_indices
        self._gpu_index = gpu_index

        self._software = ArrayVideoDriver()
        self._callback = retro_hw_render_callback(context_type=HardwareContext.NONE)
        self._pending_context_destroy: retro_hw_context_reset_t | None = None
        self._active = HardwareContext.NONE
        self._needs_reinit = True
        self._negotiation: retro_hw_render_context_negotiation_interface_vulkan | None = None

        self._queue_lock = threading.RLock()
        self._loader: ctypes.CDLL | None = None

        # CFFI handles for the live context (None when no Vulkan context is active)
        self._instance = None
        self._gpu = None
        self._device = None
        self._queue = None
        self._queue_family = 0
        self._surface_raw = 0
        self._core_created_device = False
        self._negotiation_used = False

        # Frontend capture resources
        self._command_pool = None
        self._command_buffer = None
        self._fence = None
        self._staging_buffer = None
        self._staging_memory = None
        self._staging_map = None
        self._staging_dims: tuple[int, int] | None = None

        # Per-frame state provided by the core through the render interface
        self._sync_index = 0
        self._hw_image: tuple[int, int, int, int, int] | None = None
        self._hw_semaphores: list[int] = []
        self._hw_src_queue_family: int = vk.VK_QUEUE_FAMILY_IGNORED
        self._core_command_buffers: list[int] = []
        self._signal_semaphore: int = 0

        # The most recent captured hardware frame: (pixels, width, height, vk_format)
        self._hw_frame: tuple[bytearray, int, int, int] | None = None
        self._last_frame_hw = False
        self._warned_no_image = False
        self._warned_format: int | None = None

        self._interface: retro_hw_render_interface_vulkan | None = None
        # ctypes callback objects must outlive the interface struct
        self._interface_refs: tuple[Any, ...] | None = None

    def __del__(self):
        """Release all Vulkan resources; never raises."""
        with suppress(Exception):
            self.__destroy_vulkan()

    @override
    def refresh(
        self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        match data:
            case FrameBufferSpecial.HARDWARE:
                self.__refresh_hardware(width, height)

            case FrameBufferSpecial.DUPE:
                if self._last_frame_hw:
                    self.__finish_frame()
                else:
                    self._software.refresh(data, width, height, pitch)

            case memoryview():
                self._software.refresh(data, width, height, pitch)
                self._last_frame_hw = False

            case _:
                raise TypeError(
                    f"Expected a memoryview or a FrameBufferSpecial, got {type(data).__name__}"
                )

    @property
    @override
    def needs_reinit(self) -> bool:
        return self._needs_reinit

    @override
    def reinit(self) -> None:
        if self._software.system_av_info is None:
            raise RuntimeError("Cannot reinitialize video driver without system AV info from core")

        if self._interface is not None:
            context_destroy = self._pending_context_destroy or self._callback.context_destroy
            if context_destroy:
                context_destroy()

        self._pending_context_destroy = None
        self.__destroy_vulkan()

        if self._active == HardwareContext.VULKAN:
            self.__init_vulkan()
            self._needs_reinit = False
            if self._callback.context_reset:
                self._callback.context_reset()
        else:
            self._needs_reinit = False

    @property
    @override
    def supported_contexts(self) -> Set[HardwareContext]:
        return _CONTEXTS

    @property
    @override
    def active_context(self) -> HardwareContext:
        return self._active

    @property
    @override
    def preferred_context(self) -> HardwareContext | None:
        return HardwareContext.VULKAN

    @override
    def set_context(self, callback: retro_hw_render_callback) -> None:
        if not isinstance(callback, retro_hw_render_callback):
            raise TypeError(f"Expected a retro_hw_render_callback, got {type(callback).__name__}")

        context_type = HardwareContext(callback.context_type)
        if context_type not in _CONTEXTS:
            raise UnsupportedContextError(
                f"VulkanVideoDriver only supports NONE and VULKAN contexts, got {context_type}"
            )

        if self._interface is not None:
            # Keep the active context's destroy callback so the next reinit
            # can still notify the core, even though the new callback replaces it
            self._pending_context_destroy = self._callback.context_destroy

        self._callback = deepcopy(callback)
        self._active = context_type
        self._needs_reinit = True

    @property
    @override
    def current_framebuffer(self) -> int | None:
        return None  # Only meaningful for OpenGL

    @override
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        return None  # Only meaningful for OpenGL; Vulkan cores use get_instance_proc_addr

    @property
    @override
    def rotation(self) -> Rotation:
        return self._software.rotation

    @rotation.setter
    @override
    def rotation(self, rotation: Rotation) -> None:
        self._software.rotation = rotation

    @property
    @override
    def can_dupe(self) -> bool | None:
        return True

    @property
    @override
    def pixel_format(self) -> PixelFormat:
        return self._software.pixel_format

    @pixel_format.setter
    @override
    def pixel_format(self, format: PixelFormat) -> None:
        self._software.pixel_format = format

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return self._software.system_av_info

    @system_av_info.setter
    @override
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        self._software.system_av_info = av_info
        self.reinit()

    @property
    @override
    def geometry(self) -> retro_game_geometry | None:
        return self._software.geometry

    @geometry.setter
    @override
    def geometry(self, geometry: retro_game_geometry) -> None:
        self._software.geometry = geometry

    @override
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        return self._software.get_software_framebuffer(width, height, flags)

    @override
    def destroy_hw_context(self) -> None:
        if self._interface is None:
            return

        context_destroy = self._pending_context_destroy or self._callback.context_destroy
        self._pending_context_destroy = None
        if context_destroy:
            context_destroy()

        # The next reinit must not call context_destroy again.
        # This must happen *after* the call above:
        # ctypes function-pointer fields are views into the struct's memory,
        # so nulling the field first would also null the captured value.
        self._callback.context_destroy = None

    @property
    @override
    def hw_render_interface(self) -> retro_hw_render_interface_vulkan | None:
        return self._interface

    @property
    @override
    def context_negotiation_interface(
        self,
    ) -> retro_hw_render_context_negotiation_interface | None:
        return self._negotiation

    @context_negotiation_interface.setter
    @override
    def context_negotiation_interface(
        self, interface: retro_hw_render_context_negotiation_interface | None
    ) -> None:
        if interface is None:
            self._negotiation = None
            return

        if not isinstance(interface, retro_hw_render_context_negotiation_interface):
            raise TypeError(
                "Expected a retro_hw_render_context_negotiation_interface or None, "
                f"got {type(interface).__name__}"
            )

        if not isinstance(interface, retro_hw_render_context_negotiation_interface_vulkan):
            # Reinterpret the base struct as the full Vulkan layout;
            # the underlying memory is the core's full struct
            interface = ctypes.cast(
                byref(interface), POINTER(retro_hw_render_context_negotiation_interface_vulkan)
            )[0]

        assert isinstance(interface, retro_hw_render_context_negotiation_interface_vulkan)
        self._negotiation = interface

    @property
    @override
    def shared_context(self) -> bool:
        return False

    @shared_context.setter
    @override
    def shared_context(self, value: bool) -> None:
        raise NotImplementedError("Shared contexts are only meaningful for OpenGL")

    @property
    def sync_indices(self) -> int:
        """The number of frame-in-flight indices reported through ``get_sync_index_mask``."""
        return self._sync_index_count

    @override
    def screenshot(self, prerotate: bool = True) -> Screenshot | None:
        if not self._last_frame_hw:
            return self._software.screenshot(prerotate)

        if self._hw_frame is None:
            return None

        pixels, width, height, vk_format = self._hw_frame
        rgba = _to_rgba32(pixels, vk_format)
        rgba[3::4] = b"\xff" * (width * height)  # Screenshots are opaque

        rotation = self._software.rotation
        rot = rotation if prerotate else Rotation.NONE
        rgba, out_width, out_height = _rotate_rgba32(rgba, width, height, rot)

        return Screenshot(
            memoryview(rgba),
            out_width,
            out_height,
            rotation,
            self._software.pixel_format,
        )

    def __init_vulkan(self) -> None:
        self._loader = _load_loader()
        gipa_addr = ctypes.cast(self._loader.vkGetInstanceProcAddr, c_void_p).value
        assert gipa_addr is not None

        self.__create_instance(gipa_addr)
        self.__create_surface()
        self.__select_gpu()
        self.__create_device(gipa_addr)
        self.__create_capture_resources()
        self.__build_interface(gipa_addr)

    def __create_surface(self) -> None:
        """
        Create a headless surface for cores whose device negotiation
        assumes one exists (they may query surface support during queue selection).
        Leaves the surface at 0 when ``VK_EXT_headless_surface`` isn't available.
        """
        self._surface_raw = 0
        try:
            create: Any = vk.vkGetInstanceProcAddr(self._instance, "vkCreateHeadlessSurfaceEXT")
        except Exception:
            return

        if create is None:
            return

        try:
            surface = create(self._instance, vk.VkHeadlessSurfaceCreateInfoEXT(), None)
        except Exception as e:
            warn(f"Couldn't create a headless surface: {e}")
            return

        self._surface_raw = int(ffi.cast("uint64_t", surface))

    def __destroy_surface(self) -> None:
        if not self._surface_raw or self._instance is None:
            return

        try:
            destroy = vk.vkGetInstanceProcAddr(self._instance, "vkDestroySurfaceKHR")
            destroy(self._instance, ffi.cast("VkSurfaceKHR", self._surface_raw), None)
        except Exception as e:
            warn(f"Couldn't destroy the headless surface: {e}")

        self._surface_raw = 0

    def __create_instance(self, gipa_addr: int) -> None:
        negotiation = self._negotiation
        app_name = b"libretro.py"
        engine_name = b"libretro.py"
        # Vulkan cores put a full VK_MAKE_VERSION value in version_major
        # (both Azahar and libretro-samples do this);
        # plain major/minor pairs appear only in older or GL-minded cores.
        requested = self._callback.version_major
        if requested and requested < (1 << 22):
            requested = (requested << 22) | (self._callback.version_minor << 12)

        api_version = max(_VK_API_VERSION_1_1, requested)

        if negotiation is not None and negotiation.get_application_info:
            app_info_ptr = negotiation.get_application_info()
            if app_info_ptr:
                app_info = app_info_ptr[0]
                app_name = app_info.pApplicationName or app_name
                engine_name = app_info.pEngineName or engine_name
                api_version = max(api_version, app_info.apiVersion)

        available: set[str] = {
            str(ext.extensionName) for ext in vk.vkEnumerateInstanceExtensionProperties(None)
        }
        extensions, flags = _wanted_instance_extensions(available)

        if (
            negotiation is not None
            and negotiation.interface_version >= 2
            and negotiation.create_instance
        ):
            instance_raw = self.__negotiate_instance(negotiation, gipa_addr, api_version)
            if instance_raw:
                self._instance = ffi.cast("VkInstance", instance_raw)
                return

            warn("The core's create_instance failed; creating a VkInstance without it")

        app_info = vk.VkApplicationInfo(
            pApplicationName=app_name.decode(),
            applicationVersion=0,
            pEngineName=engine_name.decode(),
            engineVersion=0,
            apiVersion=api_version,
        )
        create_info = vk.VkInstanceCreateInfo(
            flags=flags,
            pApplicationInfo=app_info,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,
        )
        self._instance = vk.vkCreateInstance(create_info, None)

    def __negotiate_instance(
        self,
        negotiation: retro_hw_render_context_negotiation_interface_vulkan,
        gipa_addr: int,
        api_version: int,
    ) -> int:
        self._negotiation_used = True

        available: set[str] = {
            str(ext.extensionName) for ext in vk.vkEnumerateInstanceExtensionProperties(None)
        }

        def _create_instance_wrapper(_opaque: int | None, create_info_ptr: int | None) -> int:
            try:
                if not create_info_ptr:
                    return 0

                info = ctypes.cast(create_info_ptr, POINTER(_VkInstanceCreateInfo))[0]
                extensions = [
                    info.ppEnabledExtensionNames[i].decode()
                    for i in range(info.enabledExtensionCount)
                ]
                layers = [
                    info.ppEnabledLayerNames[i].decode() for i in range(info.enabledLayerCount)
                ]
                wanted, wanted_flags = _wanted_instance_extensions(available)
                extensions.extend(ext for ext in wanted if ext not in extensions)
                flags = info.flags | wanted_flags

                app_info = (
                    ffi.cast("VkApplicationInfo *", ctypes.addressof(info.pApplicationInfo[0]))
                    if info.pApplicationInfo
                    else ffi.NULL
                )
                create_info = vk.VkInstanceCreateInfo(
                    pNext=ffi.cast("void *", info.pNext or 0),
                    flags=flags,
                    pApplicationInfo=app_info,
                    enabledLayerCount=len(layers),
                    ppEnabledLayerNames=layers,
                    enabledExtensionCount=len(extensions),
                    ppEnabledExtensionNames=extensions,
                )
                return _raw(vk.vkCreateInstance(create_info, None))
            except Exception as e:
                warn(f"vkCreateInstance failed in the create_instance wrapper: {e}")
                return 0

        wrapper = retro_vulkan_create_instance_wrapper_t(_create_instance_wrapper)
        app_info_ctypes = VkApplicationInfo(
            sType=0,
            pApplicationName=b"libretro.py",
            pEngineName=b"libretro.py",
            apiVersion=api_version,
        )
        return negotiation.create_instance(gipa_addr, byref(app_info_ctypes), wrapper, None) or 0

    def __select_gpu(self) -> None:
        gpus = vk.vkEnumeratePhysicalDevices(self._instance)
        if not gpus:
            raise RuntimeError("No Vulkan physical devices found")

        if self._gpu_index >= len(gpus):
            warn(
                f"gpu_index {self._gpu_index} is out of range "
                f"({len(gpus)} devices found); using device 0"
            )
            self._gpu = gpus[0]
        else:
            self._gpu = gpus[self._gpu_index]

    def __create_device(self, gipa_addr: int) -> None:
        negotiation = self._negotiation
        self._core_created_device = False

        if negotiation is not None:
            if negotiation.interface_version >= 2 and negotiation.create_device2:
                if self.__negotiate_device2(negotiation, gipa_addr):
                    return
                warn("The core's create_device2 failed; falling back")

            if negotiation.create_device:
                if self.__negotiate_device(negotiation, gipa_addr):
                    return
                warn("The core's create_device failed; falling back to default device creation")

        self.__create_device_default()

    def __adopt_context(self, context: retro_vulkan_context) -> bool:
        if not context.device or not context.queue:
            return False

        self._device = ffi.cast("VkDevice", context.device)
        self._queue = ffi.cast("VkQueue", context.queue)
        self._queue_family = context.queue_family_index
        if context.gpu:
            self._gpu = ffi.cast("VkPhysicalDevice", context.gpu)

        self._core_created_device = True
        return True

    def __negotiate_device(
        self,
        negotiation: retro_hw_render_context_negotiation_interface_vulkan,
        gipa_addr: int,
    ) -> bool:
        self._negotiation_used = True
        context = retro_vulkan_context()
        features = VkPhysicalDeviceFeatures()  # The frontend itself requires no features

        ok = negotiation.create_device(
            byref(context),
            _raw(self._instance),
            _raw(self._gpu),
            self._surface_raw,  # A headless surface (or 0 if unavailable)
            gipa_addr,
            None,
            0,
            None,
            0,
            byref(features),
        )
        if not ok:
            return False

        return self.__adopt_context(context)

    def __negotiate_device2(
        self,
        negotiation: retro_hw_render_context_negotiation_interface_vulkan,
        gipa_addr: int,
    ) -> bool:
        self._negotiation_used = True

        device_extensions = {
            ext.extensionName for ext in vk.vkEnumerateDeviceExtensionProperties(self._gpu, None)
        }

        def _create_device_wrapper(
            gpu_raw: int | None, _opaque: int | None, create_info_ptr: int | None
        ) -> int:
            try:
                if not create_info_ptr:
                    return 0

                info = ctypes.cast(create_info_ptr, POINTER(_VkDeviceCreateInfo))[0]
                extensions = [
                    info.ppEnabledExtensionNames[i].decode()
                    for i in range(info.enabledExtensionCount)
                ]
                if (
                    vk.VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME in device_extensions
                    and vk.VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME not in extensions
                ):
                    extensions.append(vk.VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME)

                layers = [
                    info.ppEnabledLayerNames[i].decode() for i in range(info.enabledLayerCount)
                ]
                create_info = vk.VkDeviceCreateInfo(
                    pNext=ffi.cast("void *", info.pNext or 0),
                    flags=info.flags,
                    queueCreateInfoCount=info.queueCreateInfoCount,
                    pQueueCreateInfos=ffi.cast(
                        "VkDeviceQueueCreateInfo *", info.pQueueCreateInfos or 0
                    ),
                    enabledLayerCount=len(layers),
                    ppEnabledLayerNames=layers,
                    enabledExtensionCount=len(extensions),
                    ppEnabledExtensionNames=extensions,
                    pEnabledFeatures=ffi.cast(
                        "VkPhysicalDeviceFeatures *",
                        ctypes.addressof(info.pEnabledFeatures[0]) if info.pEnabledFeatures else 0,
                    ),
                )
                gpu = ffi.cast("VkPhysicalDevice", gpu_raw or 0)
                return _raw(vk.vkCreateDevice(gpu, create_info, None))
            except Exception as e:
                warn(f"vkCreateDevice failed in the create_device wrapper: {e}")
                return 0

        wrapper = retro_vulkan_create_device_wrapper_t(_create_device_wrapper)

        context = retro_vulkan_context()
        ok = negotiation.create_device2(
            byref(context),
            _raw(self._instance),
            _raw(self._gpu),
            self._surface_raw,  # A headless surface (or 0 if unavailable)
            gipa_addr,
            wrapper,
            None,
        )
        if not ok:
            # Retry allowing the core to pick the physical device itself
            context = retro_vulkan_context()
            ok = negotiation.create_device2(
                byref(context),
                _raw(self._instance),
                0,
                self._surface_raw,
                gipa_addr,
                wrapper,
                None,
            )

        if not ok:
            return False

        return self.__adopt_context(context)

    def __create_device_default(self) -> None:
        families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self._gpu)
        wanted = vk.VK_QUEUE_GRAPHICS_BIT | vk.VK_QUEUE_COMPUTE_BIT
        try:
            family = next(i for i, f in enumerate(families) if (f.queueFlags & wanted) == wanted)
        except StopIteration:
            raise RuntimeError("No Vulkan queue family supports both graphics and compute")

        extensions = [
            ext.extensionName
            for ext in vk.vkEnumerateDeviceExtensionProperties(self._gpu, None)
            if ext.extensionName == vk.VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME
        ]

        queue_info = vk.VkDeviceQueueCreateInfo(
            queueFamilyIndex=family, queueCount=1, pQueuePriorities=[1.0]
        )
        create_info = vk.VkDeviceCreateInfo(
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_info],
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,
            # Like RetroArch, enable every feature the device supports
            pEnabledFeatures=vk.vkGetPhysicalDeviceFeatures(self._gpu),
        )
        self._device = vk.vkCreateDevice(self._gpu, create_info, None)
        self._queue = vk.vkGetDeviceQueue(self._device, family, 0)
        self._queue_family = family

    def __create_capture_resources(self) -> None:
        self._command_pool = vk.vkCreateCommandPool(
            self._device,
            vk.VkCommandPoolCreateInfo(
                flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
                queueFamilyIndex=self._queue_family,
            ),
            None,
        )
        self._command_buffer = vk.vkAllocateCommandBuffers(
            self._device,
            vk.VkCommandBufferAllocateInfo(
                commandPool=self._command_pool,
                level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
                commandBufferCount=1,
            ),
        )[0]
        self._fence = vk.vkCreateFence(self._device, vk.VkFenceCreateInfo(), None)

    def __ensure_staging_buffer(self, width: int, height: int) -> None:
        if self._staging_dims == (width, height):
            return

        self.__destroy_staging_buffer()

        size = width * height * 4
        self._staging_buffer = vk.vkCreateBuffer(
            self._device,
            vk.VkBufferCreateInfo(
                size=size,
                usage=vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            ),
            None,
        )
        reqs: Any = vk.vkGetBufferMemoryRequirements(self._device, self._staging_buffer)
        mem_props: Any = vk.vkGetPhysicalDeviceMemoryProperties(self._gpu)
        wanted = vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        try:
            type_index = next(
                i
                for i in range(mem_props.memoryTypeCount)
                if (reqs.memoryTypeBits >> i) & 1
                and (mem_props.memoryTypes[i].propertyFlags & wanted) == wanted
            )
        except StopIteration:
            raise RuntimeError("No host-visible, host-coherent Vulkan memory type available")

        self._staging_memory = vk.vkAllocateMemory(
            self._device,
            vk.VkMemoryAllocateInfo(allocationSize=reqs.size, memoryTypeIndex=type_index),
            None,
        )
        vk.vkBindBufferMemory(self._device, self._staging_buffer, self._staging_memory, 0)
        self._staging_map = vk.vkMapMemory(self._device, self._staging_memory, 0, size, 0)
        self._staging_dims = (width, height)

    def __refresh_hardware(self, width: int, height: int) -> None:
        if self._interface is None:
            warn("RETRO_HW_FRAME_BUFFER_VALID passed but no Vulkan context is active")
            return

        if self._hw_image is None:
            if not self._warned_no_image:
                warn("The core didn't provide an image with set_image before video_refresh")
                self._warned_no_image = True
            self.__finish_frame()
            return

        image_raw, layout, vk_format, base_mip, base_layer = self._hw_image
        if vk_format not in _CAPTURABLE_FORMATS:
            if self._warned_format != vk_format:
                warn(f"Unsupported VkFormat {vk_format} for frame capture; skipping")
                self._warned_format = vk_format
            self.__finish_frame()
            return

        self.__ensure_staging_buffer(width, height)
        self.__record_capture(image_raw, layout, base_mip, base_layer, width, height)
        self.__submit_capture()

        assert self._staging_map is not None
        # vkMapMemory in the vulkan package returns an ffi.buffer over the mapping;
        # the staging buffer is sized for 4-byte texels, so slice off what this
        # frame's (possibly smaller) texel size actually filled
        pixels = bytearray(self._staging_map[: width * height * _CAPTURABLE_FORMATS[vk_format]])
        self._hw_frame = (pixels, width, height, vk_format)
        self._last_frame_hw = True
        self.__consume_frame_state()

    def __record_capture(
        self, image_raw: int, layout: int, base_mip: int, base_layer: int, width: int, height: int
    ) -> None:
        image = ffi.cast("VkImage", image_raw)
        subresource = vk.VkImageSubresourceRange(
            vk.VK_IMAGE_ASPECT_COLOR_BIT, base_mip, 1, base_layer, 1
        )
        ownership_transfer = (
            self._hw_src_queue_family != self._queue_family
            and self._hw_src_queue_family != vk.VK_QUEUE_FAMILY_IGNORED
        )

        cmd = self._command_buffer
        vk.vkResetCommandBuffer(cmd, 0)
        vk.vkBeginCommandBuffer(
            cmd, vk.VkCommandBufferBeginInfo(flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT)
        )

        to_transfer = vk.VkImageMemoryBarrier(
            srcAccessMask=vk.VK_ACCESS_MEMORY_WRITE_BIT | vk.VK_ACCESS_MEMORY_READ_BIT,
            dstAccessMask=vk.VK_ACCESS_TRANSFER_READ_BIT,
            oldLayout=layout,
            newLayout=vk.VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
            srcQueueFamilyIndex=(
                self._hw_src_queue_family if ownership_transfer else vk.VK_QUEUE_FAMILY_IGNORED
            ),
            dstQueueFamilyIndex=(
                self._queue_family if ownership_transfer else vk.VK_QUEUE_FAMILY_IGNORED
            ),
            image=image,
            subresourceRange=subresource,
        )
        vk.vkCmdPipelineBarrier(
            cmd,
            vk.VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,
            vk.VK_PIPELINE_STAGE_TRANSFER_BIT,
            0,
            0,
            None,
            0,
            None,
            1,
            [to_transfer],
        )

        region = vk.VkBufferImageCopy(
            bufferOffset=0,
            bufferRowLength=0,
            bufferImageHeight=0,
            imageSubresource=vk.VkImageSubresourceLayers(
                aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                mipLevel=base_mip,
                baseArrayLayer=base_layer,
                layerCount=1,
            ),
            imageOffset=vk.VkOffset3D(0, 0, 0),
            imageExtent=vk.VkExtent3D(width, height, 1),
        )
        vk.vkCmdCopyImageToBuffer(
            cmd,
            image,
            vk.VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
            self._staging_buffer,
            1,
            [region],
        )

        to_original = vk.VkImageMemoryBarrier(
            srcAccessMask=vk.VK_ACCESS_TRANSFER_READ_BIT,
            dstAccessMask=vk.VK_ACCESS_MEMORY_WRITE_BIT | vk.VK_ACCESS_MEMORY_READ_BIT,
            oldLayout=vk.VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
            newLayout=layout,
            srcQueueFamilyIndex=(
                self._queue_family if ownership_transfer else vk.VK_QUEUE_FAMILY_IGNORED
            ),
            dstQueueFamilyIndex=(
                self._hw_src_queue_family if ownership_transfer else vk.VK_QUEUE_FAMILY_IGNORED
            ),
            image=image,
            subresourceRange=subresource,
        )
        vk.vkCmdPipelineBarrier(
            cmd,
            vk.VK_PIPELINE_STAGE_TRANSFER_BIT,
            vk.VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,
            0,
            0,
            None,
            0,
            None,
            1,
            [to_original],
        )
        vk.vkEndCommandBuffer(cmd)

    def __submit_capture(self) -> None:
        # Semaphores from set_image are ignored when the core used set_command_buffers
        wait_semaphores = self._hw_semaphores if not self._core_command_buffers else []
        assert self._command_buffer is not None
        command_buffers = [ffi.cast("VkCommandBuffer", raw) for raw in self._core_command_buffers]
        command_buffers.append(self._command_buffer)
        signal_semaphores = (
            [ffi.cast("VkSemaphore", self._signal_semaphore)] if self._signal_semaphore else []
        )

        submit = vk.VkSubmitInfo(
            waitSemaphoreCount=len(wait_semaphores),
            pWaitSemaphores=[ffi.cast("VkSemaphore", s) for s in wait_semaphores] or None,
            pWaitDstStageMask=[vk.VK_PIPELINE_STAGE_TRANSFER_BIT] * len(wait_semaphores) or None,
            commandBufferCount=len(command_buffers),
            pCommandBuffers=command_buffers,
            signalSemaphoreCount=len(signal_semaphores),
            pSignalSemaphores=signal_semaphores or None,
        )
        with self._queue_lock:
            vk.vkQueueSubmit(self._queue, 1, [submit], self._fence)

        vk.vkWaitForFences(self._device, 1, [self._fence], vk.VK_TRUE, 10_000_000_000)
        vk.vkResetFences(self._device, 1, [self._fence])

    def __finish_frame(self) -> None:
        """Handle per-frame bookkeeping for frames that don't capture anything."""
        if self._signal_semaphore and self._device is not None:
            # The signal semaphore must be signalled even for duped or skipped frames
            submit = vk.VkSubmitInfo(
                signalSemaphoreCount=1,
                pSignalSemaphores=[ffi.cast("VkSemaphore", self._signal_semaphore)],
            )
            with self._queue_lock:
                vk.vkQueueSubmit(self._queue, 1, [submit], self._fence)

            vk.vkWaitForFences(self._device, 1, [self._fence], vk.VK_TRUE, 10_000_000_000)
            vk.vkResetFences(self._device, 1, [self._fence])

        self.__consume_frame_state()

    def __consume_frame_state(self) -> None:
        self._hw_semaphores = []
        self._core_command_buffers = []
        self._signal_semaphore = 0
        self._sync_index = (self._sync_index + 1) % self._sync_index_count

    def __build_interface(self, gipa_addr: int) -> None:
        get_instance_proc_addr = _PFN_GetInstanceProcAddr(gipa_addr)
        gdpa_addr = get_instance_proc_addr(_raw(self._instance), b"vkGetDeviceProcAddr")
        if not gdpa_addr:
            raise RuntimeError("vkGetInstanceProcAddr couldn't resolve vkGetDeviceProcAddr")

        def _set_image(_handle, image_ptr, num_semaphores, semaphores, src_queue_family) -> None:
            if not image_ptr:
                self._hw_image = None
                return

            image: retro_vulkan_image = image_ptr[0]
            info = image.create_info
            self._hw_image = (
                info.image,
                image.image_layout,
                info.format,
                info.subresourceRange.baseMipLevel,
                info.subresourceRange.baseArrayLayer,
            )
            if num_semaphores and semaphores:
                self._hw_semaphores = [semaphores[i] for i in range(num_semaphores)]
            else:
                self._hw_semaphores = []

            self._hw_src_queue_family = src_queue_family

        def _get_sync_index(_handle) -> int:
            return self._sync_index

        def _get_sync_index_mask(_handle) -> int:
            return (1 << self._sync_index_count) - 1

        def _set_command_buffers(_handle, num_cmd, cmd) -> None:
            if num_cmd and cmd:
                self._core_command_buffers = [cmd[i] for i in range(num_cmd)]
            else:
                self._core_command_buffers = []

        def _wait_sync_index(_handle) -> None:
            # This driver submits synchronously (each frame waits on a fence),
            # so waiting on the queue covers everything for the current sync index.
            with self._queue_lock:
                vk.vkQueueWaitIdle(self._queue)

        def _lock_queue(_handle) -> None:
            self._queue_lock.acquire()

        def _unlock_queue(_handle) -> None:
            self._queue_lock.release()

        def _set_signal_semaphore(_handle, semaphore) -> None:
            self._signal_semaphore = semaphore

        refs = (
            retro_vulkan_set_image_t(_set_image),
            retro_vulkan_get_sync_index_t(_get_sync_index),
            retro_vulkan_get_sync_index_mask_t(_get_sync_index_mask),
            retro_vulkan_set_command_buffers_t(_set_command_buffers),
            retro_vulkan_wait_sync_index_t(_wait_sync_index),
            retro_vulkan_lock_queue_t(_lock_queue),
            retro_vulkan_unlock_queue_t(_unlock_queue),
            retro_vulkan_set_signal_semaphore_t(_set_signal_semaphore),
        )
        self._interface_refs = refs
        self._interface = retro_hw_render_interface_vulkan(
            interface_type=HardwareRenderInterfaceType.VULKAN,
            interface_version=RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION,
            handle=None,
            instance=_raw(self._instance),
            gpu=_raw(self._gpu),
            device=_raw(self._device),
            get_device_proc_addr=gdpa_addr,
            get_instance_proc_addr=gipa_addr,
            queue=_raw(self._queue),
            queue_index=self._queue_family,
            set_image=refs[0],
            get_sync_index=refs[1],
            get_sync_index_mask=refs[2],
            set_command_buffers=refs[3],
            wait_sync_index=refs[4],
            lock_queue=refs[5],
            unlock_queue=refs[6],
            set_signal_semaphore=refs[7],
        )

    def __destroy_staging_buffer(self) -> None:
        if self._device is None:
            return

        if self._staging_map is not None:
            vk.vkUnmapMemory(self._device, self._staging_memory)
            self._staging_map = None

        if self._staging_buffer is not None:
            vk.vkDestroyBuffer(self._device, self._staging_buffer, None)
            self._staging_buffer = None

        if self._staging_memory is not None:
            vk.vkFreeMemory(self._device, self._staging_memory, None)
            self._staging_memory = None

        self._staging_dims = None

    def __destroy_vulkan(self) -> None:
        if self._device is not None:
            with self._queue_lock:
                try:
                    vk.vkDeviceWaitIdle(self._device)
                except Exception as e:
                    warn(f"vkDeviceWaitIdle failed during teardown: {e}")

            self.__destroy_staging_buffer()

            if self._fence is not None:
                vk.vkDestroyFence(self._device, self._fence, None)
                self._fence = None

            if self._command_pool is not None:
                vk.vkDestroyCommandPool(self._device, self._command_pool, None)
                self._command_pool = None
                self._command_buffer = None

        if (
            self._negotiation is not None
            and self._negotiation_used
            and self._negotiation.destroy_device
        ):
            self._negotiation.destroy_device()

        self._negotiation_used = False

        if self._device is not None:
            vk.vkDestroyDevice(self._device, None)
            self._device = None
            self._queue = None

        if self._instance is not None:
            self.__destroy_surface()
            vk.vkDestroyInstance(self._instance, None)
            self._instance = None
            self._gpu = None

        if self._interface is not None:
            _retire_interface(self._interface)

        self._interface = None
        self._interface_refs = None
        self._hw_image = None
        self._hw_frame = None
        self._hw_semaphores = []
        self._core_command_buffers = []
        self._signal_semaphore = 0
        self._sync_index = 0
        self._last_frame_hw = False
        self._core_created_device = False


__all__ = ["VulkanVideoDriver"]
