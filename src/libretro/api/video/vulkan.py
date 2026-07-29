"""
Vulkan hardware rendering types.

Corresponds to the types in ``libretro_vulkan.h``,
including the mirrored Vulkan API structs
that appear in the libretro ABI by value.

Dispatchable Vulkan handles (``VkInstance``, ``VkDevice``, ...)
are represented as :class:`.c_void_ptr`
and non-dispatchable handles (``VkImage``, ``VkSemaphore``, ...)
as plain integers backed by :class:`~ctypes.c_uint64`.
Only 64-bit platforms are supported.
"""

from ctypes import Structure, c_bool, c_char_p, c_int, c_uint, c_uint32, c_uint64
from dataclasses import dataclass

from libretro.api._utils import NullPointerToNoneMixin
from libretro.ctypes import (
    CIntArg,
    TypedFunctionPointer,
    TypedPointer,
    c_void_ptr,
)

from .negotiate import retro_hw_render_context_negotiation_interface
from .render import retro_hw_render_interface

RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION = 5
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN_VERSION = 2

# Dispatchable Vulkan handles (pointers to opaque driver objects)
VkInstance = c_void_ptr
VkPhysicalDevice = c_void_ptr
VkDevice = c_void_ptr
VkQueue = c_void_ptr
VkCommandBuffer = c_void_ptr

# Non-dispatchable Vulkan handles (64-bit integers)
VkImage = c_uint64
VkImageView = c_uint64
VkSemaphore = c_uint64
VkSurfaceKHR = c_uint64

VkBool32 = c_uint32
VkImageLayout = c_int
VkFormat = c_int
VkStructureType = c_int

PFN_vkGetInstanceProcAddr = c_void_ptr
"""Treated as an opaque function pointer at the ABI boundary."""

PFN_vkGetDeviceProcAddr = c_void_ptr
"""Treated as an opaque function pointer at the ABI boundary."""


@dataclass(init=False, slots=True)
class VkApplicationInfo(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`VkApplicationInfo` in ``vulkan_core.h``.

    >>> from libretro.api.video import VkApplicationInfo
    >>> info = VkApplicationInfo()
    >>> info.pApplicationName is None
    True
    """

    sType: int
    """Structure type tag (:c:type:`VkStructureType`)."""
    pNext: c_void_ptr | None
    """Pointer to an extension structure, if any."""
    pApplicationName: bytes | None
    """Name of the application, if provided."""
    applicationVersion: int
    """Application-defined version number."""
    pEngineName: bytes | None
    """Name of the engine, if provided."""
    engineVersion: int
    """Engine-defined version number."""
    apiVersion: int
    """Highest Vulkan API version the application intends to use."""

    _fields_ = (
        ("sType", VkStructureType),
        ("pNext", c_void_ptr),
        ("pApplicationName", c_char_p),
        ("applicationVersion", c_uint32),
        ("pEngineName", c_char_p),
        ("engineVersion", c_uint32),
        ("apiVersion", c_uint32),
    )


@dataclass(init=False, slots=True)
class VkComponentMapping(Structure):
    """
    Corresponds to :c:type:`VkComponentMapping` in ``vulkan_core.h``.

    >>> from libretro.api.video import VkComponentMapping
    >>> VkComponentMapping().r
    0
    """

    r: int
    """Swizzle for the red component (:c:type:`VkComponentSwizzle`)."""
    g: int
    """Swizzle for the green component (:c:type:`VkComponentSwizzle`)."""
    b: int
    """Swizzle for the blue component (:c:type:`VkComponentSwizzle`)."""
    a: int
    """Swizzle for the alpha component (:c:type:`VkComponentSwizzle`)."""

    _fields_ = (
        ("r", c_int),
        ("g", c_int),
        ("b", c_int),
        ("a", c_int),
    )

    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> from copy import deepcopy
        >>> from ctypes import addressof
        >>> from libretro.api.video import VkComponentMapping
        >>> mapping = VkComponentMapping(r=1)
        >>> mapping_copy = deepcopy(mapping)
        >>> addressof(mapping) == addressof(mapping_copy)
        False
        >>> mapping_copy.r
        1
        """
        return VkComponentMapping(r=self.r, g=self.g, b=self.b, a=self.a)


@dataclass(init=False, slots=True)
class VkImageSubresourceRange(Structure):
    """
    Corresponds to :c:type:`VkImageSubresourceRange` in ``vulkan_core.h``.

    >>> from libretro.api.video import VkImageSubresourceRange
    >>> VkImageSubresourceRange().levelCount
    0
    """

    aspectMask: int
    """Bitmask of the image aspects included in the range."""
    baseMipLevel: int
    """First mipmap level in the range."""
    levelCount: int
    """Number of mipmap levels in the range."""
    baseArrayLayer: int
    """First array layer in the range."""
    layerCount: int
    """Number of array layers in the range."""

    _fields_ = (
        ("aspectMask", c_uint32),
        ("baseMipLevel", c_uint32),
        ("levelCount", c_uint32),
        ("baseArrayLayer", c_uint32),
        ("layerCount", c_uint32),
    )

    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> from copy import deepcopy
        >>> from ctypes import addressof
        >>> from libretro.api.video import VkImageSubresourceRange
        >>> subresource = VkImageSubresourceRange(layerCount=1)
        >>> subresource_copy = deepcopy(subresource)
        >>> addressof(subresource) == addressof(subresource_copy)
        False
        >>> subresource_copy.layerCount
        1
        """
        return VkImageSubresourceRange(
            aspectMask=self.aspectMask,
            baseMipLevel=self.baseMipLevel,
            levelCount=self.levelCount,
            baseArrayLayer=self.baseArrayLayer,
            layerCount=self.layerCount,
        )


@dataclass(init=False, slots=True)
class VkImageViewCreateInfo(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`VkImageViewCreateInfo` in ``vulkan_core.h``.

    >>> from libretro.api.video import VkImageViewCreateInfo
    >>> VkImageViewCreateInfo().pNext is None
    True
    """

    sType: int
    """Structure type tag (:c:type:`VkStructureType`)."""
    pNext: c_void_ptr | None
    """Pointer to an extension structure, if any."""
    flags: int
    """Reserved :c:type:`VkImageViewCreateFlags`."""
    image: int
    """The :c:type:`VkImage` the view was created from."""
    viewType: int
    """Type of the image view (:c:type:`VkImageViewType`)."""
    format: int
    """Pixel format of the view (:c:type:`VkFormat`)."""
    components: VkComponentMapping
    """Component swizzle applied by the view."""
    subresourceRange: VkImageSubresourceRange
    """Subresource range the view covers."""

    _fields_ = (
        ("sType", VkStructureType),
        ("pNext", c_void_ptr),
        ("flags", c_uint32),
        ("image", VkImage),
        ("viewType", c_int),
        ("format", VkFormat),
        ("components", VkComponentMapping),
        ("subresourceRange", VkImageSubresourceRange),
    )


@dataclass(init=False, slots=True)
class VkPhysicalDeviceFeatures(Structure):
    """
    Corresponds to :c:type:`VkPhysicalDeviceFeatures` in ``vulkan_core.h``.

    Each field is a :c:type:`VkBool32` indicating whether the feature is
    supported (when queried) or requested (when creating a device).

    >>> from libretro.api.video import VkPhysicalDeviceFeatures
    >>> VkPhysicalDeviceFeatures().geometryShader
    0
    """

    robustBufferAccess: int
    fullDrawIndexUint32: int
    imageCubeArray: int
    independentBlend: int
    geometryShader: int
    tessellationShader: int
    sampleRateShading: int
    dualSrcBlend: int
    logicOp: int
    multiDrawIndirect: int
    drawIndirectFirstInstance: int
    depthClamp: int
    depthBiasClamp: int
    fillModeNonSolid: int
    depthBounds: int
    wideLines: int
    largePoints: int
    alphaToOne: int
    multiViewport: int
    samplerAnisotropy: int
    textureCompressionETC2: int
    textureCompressionASTC_LDR: int
    textureCompressionBC: int
    occlusionQueryPrecise: int
    pipelineStatisticsQuery: int
    vertexPipelineStoresAndAtomics: int
    fragmentStoresAndAtomics: int
    shaderTessellationAndGeometryPointSize: int
    shaderImageGatherExtended: int
    shaderStorageImageExtendedFormats: int
    shaderStorageImageMultisample: int
    shaderStorageImageReadWithoutFormat: int
    shaderStorageImageWriteWithoutFormat: int
    shaderUniformBufferArrayDynamicIndexing: int
    shaderSampledImageArrayDynamicIndexing: int
    shaderStorageBufferArrayDynamicIndexing: int
    shaderStorageImageArrayDynamicIndexing: int
    shaderClipDistance: int
    shaderCullDistance: int
    shaderFloat64: int
    shaderInt64: int
    shaderInt16: int
    shaderResourceResidency: int
    shaderResourceMinLod: int
    sparseBinding: int
    sparseResidencyBuffer: int
    sparseResidencyImage2D: int
    sparseResidencyImage3D: int
    sparseResidency2Samples: int
    sparseResidency4Samples: int
    sparseResidency8Samples: int
    sparseResidency16Samples: int
    sparseResidencyAliased: int
    variableMultisampleRate: int
    inheritedQueries: int

    _fields_ = (
        ("robustBufferAccess", VkBool32),
        ("fullDrawIndexUint32", VkBool32),
        ("imageCubeArray", VkBool32),
        ("independentBlend", VkBool32),
        ("geometryShader", VkBool32),
        ("tessellationShader", VkBool32),
        ("sampleRateShading", VkBool32),
        ("dualSrcBlend", VkBool32),
        ("logicOp", VkBool32),
        ("multiDrawIndirect", VkBool32),
        ("drawIndirectFirstInstance", VkBool32),
        ("depthClamp", VkBool32),
        ("depthBiasClamp", VkBool32),
        ("fillModeNonSolid", VkBool32),
        ("depthBounds", VkBool32),
        ("wideLines", VkBool32),
        ("largePoints", VkBool32),
        ("alphaToOne", VkBool32),
        ("multiViewport", VkBool32),
        ("samplerAnisotropy", VkBool32),
        ("textureCompressionETC2", VkBool32),
        ("textureCompressionASTC_LDR", VkBool32),
        ("textureCompressionBC", VkBool32),
        ("occlusionQueryPrecise", VkBool32),
        ("pipelineStatisticsQuery", VkBool32),
        ("vertexPipelineStoresAndAtomics", VkBool32),
        ("fragmentStoresAndAtomics", VkBool32),
        ("shaderTessellationAndGeometryPointSize", VkBool32),
        ("shaderImageGatherExtended", VkBool32),
        ("shaderStorageImageExtendedFormats", VkBool32),
        ("shaderStorageImageMultisample", VkBool32),
        ("shaderStorageImageReadWithoutFormat", VkBool32),
        ("shaderStorageImageWriteWithoutFormat", VkBool32),
        ("shaderUniformBufferArrayDynamicIndexing", VkBool32),
        ("shaderSampledImageArrayDynamicIndexing", VkBool32),
        ("shaderStorageBufferArrayDynamicIndexing", VkBool32),
        ("shaderStorageImageArrayDynamicIndexing", VkBool32),
        ("shaderClipDistance", VkBool32),
        ("shaderCullDistance", VkBool32),
        ("shaderFloat64", VkBool32),
        ("shaderInt64", VkBool32),
        ("shaderInt16", VkBool32),
        ("shaderResourceResidency", VkBool32),
        ("shaderResourceMinLod", VkBool32),
        ("sparseBinding", VkBool32),
        ("sparseResidencyBuffer", VkBool32),
        ("sparseResidencyImage2D", VkBool32),
        ("sparseResidencyImage3D", VkBool32),
        ("sparseResidency2Samples", VkBool32),
        ("sparseResidency4Samples", VkBool32),
        ("sparseResidency8Samples", VkBool32),
        ("sparseResidency16Samples", VkBool32),
        ("sparseResidencyAliased", VkBool32),
        ("variableMultisampleRate", VkBool32),
        ("inheritedQueries", VkBool32),
    )

    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> from copy import deepcopy
        >>> from ctypes import addressof
        >>> from libretro.api.video import VkPhysicalDeviceFeatures
        >>> features = VkPhysicalDeviceFeatures(geometryShader=1)
        >>> features_copy = deepcopy(features)
        >>> addressof(features) == addressof(features_copy)
        False
        >>> features_copy.geometryShader
        1
        """
        return VkPhysicalDeviceFeatures(
            **{field[0]: getattr(self, field[0]) for field in VkPhysicalDeviceFeatures._fields_}
        )


@dataclass(init=False, slots=True)
class retro_vulkan_image(Structure):
    """
    Corresponds to :c:type:`retro_vulkan_image` in ``libretro_vulkan.h``.

    >>> from libretro.api.video import retro_vulkan_image
    >>> retro_vulkan_image().image_view
    0
    """

    image_view: int
    """The :c:type:`VkImageView` the core rendered into."""
    image_layout: int
    """Layout of the image at the time of ``set_image`` (:c:type:`VkImageLayout`)."""
    create_info: VkImageViewCreateInfo
    """The create info used to make ``image_view``."""

    _fields_ = (
        ("image_view", VkImageView),
        ("image_layout", VkImageLayout),
        ("create_info", VkImageViewCreateInfo),
    )


@dataclass(init=False, slots=True)
class retro_vulkan_context(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`retro_vulkan_context` in ``libretro_vulkan.h``.

    Filled by a core's ``create_device`` or ``create_device2``
    to hand the negotiated device back to the frontend.

    >>> from libretro.api.video import retro_vulkan_context
    >>> context = retro_vulkan_context()
    >>> context.device is None
    True
    """

    gpu: VkPhysicalDevice | None
    """The physical device the core selected, if any."""
    device: VkDevice | None
    """The logical device the core created."""
    queue: VkQueue | None
    """The queue the frontend should use for its own work."""
    queue_family_index: int
    """Queue family that ``queue`` belongs to."""
    presentation_queue: VkQueue | None
    """Queue to present with; may equal ``queue``."""
    presentation_queue_family_index: int
    """Queue family that ``presentation_queue`` belongs to."""

    _fields_ = (
        ("gpu", VkPhysicalDevice),
        ("device", VkDevice),
        ("queue", VkQueue),
        ("queue_family_index", c_uint32),
        ("presentation_queue", VkQueue),
        ("presentation_queue_family_index", c_uint32),
    )


retro_vulkan_set_image_t = TypedFunctionPointer[
    None,
    [
        c_void_ptr,
        TypedPointer[retro_vulkan_image],
        CIntArg[c_uint32],
        TypedPointer[VkSemaphore],
        CIntArg[c_uint32],
    ],
]
"""
Give the frontend the image the core rendered into,
plus semaphores to wait on (if any) and the source queue family.

Corresponds to :c:type:`retro_vulkan_set_image_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_get_sync_index_t = TypedFunctionPointer[c_uint32, [c_void_ptr]]
"""
Return the frontend's current frame-in-flight index.

Corresponds to :c:type:`retro_vulkan_get_sync_index_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_get_sync_index_mask_t = TypedFunctionPointer[c_uint32, [c_void_ptr]]
"""
Return a bitmask of all valid sync indices.

Corresponds to :c:type:`retro_vulkan_get_sync_index_mask_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_set_command_buffers_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[c_uint32], TypedPointer[VkCommandBuffer]]
]
"""
Give the frontend command buffers to submit alongside its own work.

Corresponds to :c:type:`retro_vulkan_set_command_buffers_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_wait_sync_index_t = TypedFunctionPointer[None, [c_void_ptr]]
"""
Block until the frontend has finished all work for the current sync index.

Corresponds to :c:type:`retro_vulkan_wait_sync_index_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_lock_queue_t = TypedFunctionPointer[None, [c_void_ptr]]
"""
Acquire exclusive access to the shared :c:type:`VkQueue`.

Corresponds to :c:type:`retro_vulkan_lock_queue_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_unlock_queue_t = TypedFunctionPointer[None, [c_void_ptr]]
"""
Release exclusive access to the shared :c:type:`VkQueue`.

Corresponds to :c:type:`retro_vulkan_unlock_queue_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_set_signal_semaphore_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[VkSemaphore]]
]
"""
Give the frontend a semaphore to signal when it finishes the current frame.

Corresponds to :c:type:`retro_vulkan_set_signal_semaphore_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_get_application_info_t = TypedFunctionPointer[TypedPointer[VkApplicationInfo], []]
"""
Return the :c:type:`VkApplicationInfo` the frontend should create its instance with.

Corresponds to :c:type:`retro_vulkan_get_application_info_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_create_device_t = TypedFunctionPointer[
    c_bool,
    [
        TypedPointer[retro_vulkan_context],
        VkInstance,
        VkPhysicalDevice,
        CIntArg[VkSurfaceKHR],
        PFN_vkGetInstanceProcAddr,
        TypedPointer[c_char_p],
        CIntArg[c_uint],
        TypedPointer[c_char_p],
        CIntArg[c_uint],
        TypedPointer[VkPhysicalDeviceFeatures],
    ],
]
"""
Ask the core to create the :c:type:`VkDevice` itself
(version 1 of the negotiation interface).

Corresponds to :c:type:`retro_vulkan_create_device_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_destroy_device_t = TypedFunctionPointer[None, []]
"""
Tell the core that the device it created is about to be destroyed.

Corresponds to :c:type:`retro_vulkan_destroy_device_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_create_instance_wrapper_t = TypedFunctionPointer[VkInstance, [c_void_ptr, c_void_ptr]]
"""
Frontend-provided wrapper around :c:func:`vkCreateInstance`.
The second parameter is a ``const VkInstanceCreateInfo *``, opaque at this layer.

Corresponds to :c:type:`retro_vulkan_create_instance_wrapper_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_create_instance_t = TypedFunctionPointer[
    VkInstance,
    [
        PFN_vkGetInstanceProcAddr,
        TypedPointer[VkApplicationInfo],
        retro_vulkan_create_instance_wrapper_t,
        c_void_ptr,
    ],
]
"""
Ask the core to create the :c:type:`VkInstance` itself
(version 2 of the negotiation interface).

Corresponds to :c:type:`retro_vulkan_create_instance_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_create_device_wrapper_t = TypedFunctionPointer[
    VkDevice, [VkPhysicalDevice, c_void_ptr, c_void_ptr]
]
"""
Frontend-provided wrapper around :c:func:`vkCreateDevice`.
The third parameter is a ``const VkDeviceCreateInfo *``, opaque at this layer.

Corresponds to :c:type:`retro_vulkan_create_device_wrapper_t` in ``libretro_vulkan.h``.
"""

retro_vulkan_create_device2_t = TypedFunctionPointer[
    c_bool,
    [
        TypedPointer[retro_vulkan_context],
        VkInstance,
        VkPhysicalDevice,
        CIntArg[VkSurfaceKHR],
        PFN_vkGetInstanceProcAddr,
        retro_vulkan_create_device_wrapper_t,
        c_void_ptr,
    ],
]
"""
Ask the core to create the :c:type:`VkDevice` itself
(version 2 of the negotiation interface).

Corresponds to :c:type:`retro_vulkan_create_device2_t` in ``libretro_vulkan.h``.
"""


@dataclass(init=False, slots=True)
class retro_hw_render_interface_vulkan(retro_hw_render_interface, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`retro_hw_render_interface_vulkan` in ``libretro_vulkan.h``.

    Filled by the frontend and fetched by the core
    through :attr:`.EnvironmentCall.GET_HW_RENDER_INTERFACE`.
    Extends :class:`.retro_hw_render_interface`,
    so a pointer to this struct may be reinterpreted as its base.

    >>> from libretro.api.video import retro_hw_render_interface_vulkan
    >>> iface = retro_hw_render_interface_vulkan()
    >>> iface.set_image is None
    True
    """

    handle: c_void_ptr | None
    """Opaque frontend handle passed back to every callback."""
    instance: VkInstance | None
    """The frontend's :c:type:`VkInstance`."""
    gpu: VkPhysicalDevice | None
    """The frontend's :c:type:`VkPhysicalDevice`."""
    device: VkDevice | None
    """The frontend's :c:type:`VkDevice`."""
    get_device_proc_addr: PFN_vkGetDeviceProcAddr | None
    """Device-level proc address loader for the core."""
    get_instance_proc_addr: PFN_vkGetInstanceProcAddr | None
    """Instance-level proc address loader for the core."""
    queue: VkQueue | None
    """The :c:type:`VkQueue` shared between core and frontend."""
    queue_index: int
    """Queue family that ``queue`` belongs to."""
    set_image: retro_vulkan_set_image_t | None
    """Gives the frontend the core's rendered image."""
    get_sync_index: retro_vulkan_get_sync_index_t | None
    """Returns the current frame-in-flight index."""
    get_sync_index_mask: retro_vulkan_get_sync_index_mask_t | None
    """Returns a bitmask of all valid sync indices."""
    set_command_buffers: retro_vulkan_set_command_buffers_t | None
    """Gives the frontend command buffers to submit."""
    wait_sync_index: retro_vulkan_wait_sync_index_t | None
    """Blocks until the current sync index is idle."""
    lock_queue: retro_vulkan_lock_queue_t | None
    """Acquires exclusive access to the shared queue."""
    unlock_queue: retro_vulkan_unlock_queue_t | None
    """Releases exclusive access to the shared queue."""
    set_signal_semaphore: retro_vulkan_set_signal_semaphore_t | None
    """Gives the frontend a semaphore to signal each frame."""

    _fields_ = (
        ("handle", c_void_ptr),
        ("instance", VkInstance),
        ("gpu", VkPhysicalDevice),
        ("device", VkDevice),
        ("get_device_proc_addr", PFN_vkGetDeviceProcAddr),
        ("get_instance_proc_addr", PFN_vkGetInstanceProcAddr),
        ("queue", VkQueue),
        ("queue_index", c_uint),
        ("set_image", retro_vulkan_set_image_t),
        ("get_sync_index", retro_vulkan_get_sync_index_t),
        ("get_sync_index_mask", retro_vulkan_get_sync_index_mask_t),
        ("set_command_buffers", retro_vulkan_set_command_buffers_t),
        ("wait_sync_index", retro_vulkan_wait_sync_index_t),
        ("lock_queue", retro_vulkan_lock_queue_t),
        ("unlock_queue", retro_vulkan_unlock_queue_t),
        ("set_signal_semaphore", retro_vulkan_set_signal_semaphore_t),
    )


@dataclass(init=False, slots=True)
class retro_hw_render_context_negotiation_interface_vulkan(
    retro_hw_render_context_negotiation_interface, NullPointerToNoneMixin
):
    """
    Corresponds to :c:type:`retro_hw_render_context_negotiation_interface_vulkan`
    in ``libretro_vulkan.h``.

    Provided by the core
    through :attr:`.EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE`.
    Extends :class:`.retro_hw_render_context_negotiation_interface`.
    This is the version 2 layout;
    cores that only know version 1 leave the trailing fields unset.

    >>> from libretro.api.video import retro_hw_render_context_negotiation_interface_vulkan
    >>> iface = retro_hw_render_context_negotiation_interface_vulkan()
    >>> iface.create_device is None
    True
    """

    get_application_info: retro_vulkan_get_application_info_t | None
    """Returns the application info for the frontend's instance."""
    create_device: retro_vulkan_create_device_t | None
    """Creates the device on the core's terms (version 1)."""
    destroy_device: retro_vulkan_destroy_device_t | None
    """Notifies the core before its device is destroyed."""
    create_instance: retro_vulkan_create_instance_t | None
    """Creates the instance on the core's terms (version 2)."""
    create_device2: retro_vulkan_create_device2_t | None
    """Creates the device on the core's terms (version 2)."""

    _fields_ = (
        ("get_application_info", retro_vulkan_get_application_info_t),
        ("create_device", retro_vulkan_create_device_t),
        ("destroy_device", retro_vulkan_destroy_device_t),
        ("create_instance", retro_vulkan_create_instance_t),
        ("create_device2", retro_vulkan_create_device2_t),
    )


__all__ = [
    "RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION",
    "RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN_VERSION",
    "VkInstance",
    "VkPhysicalDevice",
    "VkDevice",
    "VkQueue",
    "VkCommandBuffer",
    "VkImage",
    "VkImageView",
    "VkSemaphore",
    "VkSurfaceKHR",
    "VkBool32",
    "VkImageLayout",
    "VkFormat",
    "VkStructureType",
    "PFN_vkGetInstanceProcAddr",
    "PFN_vkGetDeviceProcAddr",
    "VkApplicationInfo",
    "VkComponentMapping",
    "VkImageSubresourceRange",
    "VkImageViewCreateInfo",
    "VkPhysicalDeviceFeatures",
    "retro_vulkan_image",
    "retro_vulkan_context",
    "retro_vulkan_set_image_t",
    "retro_vulkan_get_sync_index_t",
    "retro_vulkan_get_sync_index_mask_t",
    "retro_vulkan_set_command_buffers_t",
    "retro_vulkan_wait_sync_index_t",
    "retro_vulkan_lock_queue_t",
    "retro_vulkan_unlock_queue_t",
    "retro_vulkan_set_signal_semaphore_t",
    "retro_vulkan_get_application_info_t",
    "retro_vulkan_create_device_t",
    "retro_vulkan_destroy_device_t",
    "retro_vulkan_create_instance_wrapper_t",
    "retro_vulkan_create_instance_t",
    "retro_vulkan_create_device_wrapper_t",
    "retro_vulkan_create_device2_t",
    "retro_hw_render_interface_vulkan",
    "retro_hw_render_context_negotiation_interface_vulkan",
]
