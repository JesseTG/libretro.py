"""
Vulkan hardware rendering types.

Corresponds to the types in ``libretro_vulkan.h``,
including the mirrored Vulkan API structs
that appear in the libretro ABI by value.

Vulkan handles are represented as plain integers at this layer:
dispatchable handles (``VkInstance``, ``VkDevice``, ...) as :class:`~ctypes.c_void_p`
and non-dispatchable handles (``VkImage``, ``VkSemaphore``, ...) as :class:`~ctypes.c_uint64`.
Only 64-bit platforms are supported.
"""

from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    c_bool,
    c_char_p,
    c_int,
    c_uint,
    c_uint32,
    c_uint64,
    c_void_p,
)

from .negotiate import retro_hw_render_context_negotiation_interface
from .render import retro_hw_render_interface

RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION = 5
RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN_VERSION = 2

# Dispatchable Vulkan handles (pointers to opaque driver objects)
VkInstance = c_void_p
VkPhysicalDevice = c_void_p
VkDevice = c_void_p
VkQueue = c_void_p
VkCommandBuffer = c_void_p

# Non-dispatchable Vulkan handles (64-bit integers)
VkImage = c_uint64
VkImageView = c_uint64
VkSemaphore = c_uint64
VkSurfaceKHR = c_uint64

VkBool32 = c_uint32
VkImageLayout = c_int
VkFormat = c_int
VkStructureType = c_int

PFN_vkGetInstanceProcAddr = c_void_p
"""Treated as an opaque function pointer at the ABI boundary."""

PFN_vkGetDeviceProcAddr = c_void_p
"""Treated as an opaque function pointer at the ABI boundary."""


class VkApplicationInfo(Structure):
    """Corresponds to :c:type:`VkApplicationInfo` in ``vulkan_core.h``."""

    _fields_ = (
        ("sType", VkStructureType),
        ("pNext", c_void_p),
        ("pApplicationName", c_char_p),
        ("applicationVersion", c_uint32),
        ("pEngineName", c_char_p),
        ("engineVersion", c_uint32),
        ("apiVersion", c_uint32),
    )


class VkComponentMapping(Structure):
    """Corresponds to :c:type:`VkComponentMapping` in ``vulkan_core.h``."""

    _fields_ = (
        ("r", c_int),
        ("g", c_int),
        ("b", c_int),
        ("a", c_int),
    )


class VkImageSubresourceRange(Structure):
    """Corresponds to :c:type:`VkImageSubresourceRange` in ``vulkan_core.h``."""

    _fields_ = (
        ("aspectMask", c_uint32),
        ("baseMipLevel", c_uint32),
        ("levelCount", c_uint32),
        ("baseArrayLayer", c_uint32),
        ("layerCount", c_uint32),
    )


class VkImageViewCreateInfo(Structure):
    """Corresponds to :c:type:`VkImageViewCreateInfo` in ``vulkan_core.h``."""

    _fields_ = (
        ("sType", VkStructureType),
        ("pNext", c_void_p),
        ("flags", c_uint32),
        ("image", VkImage),
        ("viewType", c_int),
        ("format", VkFormat),
        ("components", VkComponentMapping),
        ("subresourceRange", VkImageSubresourceRange),
    )


class VkPhysicalDeviceFeatures(Structure):
    """Corresponds to :c:type:`VkPhysicalDeviceFeatures` in ``vulkan_core.h``."""

    _fields_ = tuple(
        (name, VkBool32)
        for name in (
            "robustBufferAccess",
            "fullDrawIndexUint32",
            "imageCubeArray",
            "independentBlend",
            "geometryShader",
            "tessellationShader",
            "sampleRateShading",
            "dualSrcBlend",
            "logicOp",
            "multiDrawIndirect",
            "drawIndirectFirstInstance",
            "depthClamp",
            "depthBiasClamp",
            "fillModeNonSolid",
            "depthBounds",
            "wideLines",
            "largePoints",
            "alphaToOne",
            "multiViewport",
            "samplerAnisotropy",
            "textureCompressionETC2",
            "textureCompressionASTC_LDR",
            "textureCompressionBC",
            "occlusionQueryPrecise",
            "pipelineStatisticsQuery",
            "vertexPipelineStoresAndAtomics",
            "fragmentStoresAndAtomics",
            "shaderTessellationAndGeometryPointSize",
            "shaderImageGatherExtended",
            "shaderStorageImageExtendedFormats",
            "shaderStorageImageMultisample",
            "shaderStorageImageReadWithoutFormat",
            "shaderStorageImageWriteWithoutFormat",
            "shaderUniformBufferArrayDynamicIndexing",
            "shaderSampledImageArrayDynamicIndexing",
            "shaderStorageBufferArrayDynamicIndexing",
            "shaderStorageImageArrayDynamicIndexing",
            "shaderClipDistance",
            "shaderCullDistance",
            "shaderFloat64",
            "shaderInt64",
            "shaderInt16",
            "shaderResourceResidency",
            "shaderResourceMinLod",
            "sparseBinding",
            "sparseResidencyBuffer",
            "sparseResidencyImage2D",
            "sparseResidencyImage3D",
            "sparseResidency2Samples",
            "sparseResidency4Samples",
            "sparseResidency8Samples",
            "sparseResidency16Samples",
            "sparseResidencyAliased",
            "variableMultisampleRate",
            "inheritedQueries",
        )
    )


class retro_vulkan_image(Structure):
    """Corresponds to :c:type:`retro_vulkan_image` in ``libretro_vulkan.h``."""

    _fields_ = (
        ("image_view", VkImageView),
        ("image_layout", VkImageLayout),
        ("create_info", VkImageViewCreateInfo),
    )


class retro_vulkan_context(Structure):
    """Corresponds to :c:type:`retro_vulkan_context` in ``libretro_vulkan.h``."""

    _fields_ = (
        ("gpu", VkPhysicalDevice),
        ("device", VkDevice),
        ("queue", VkQueue),
        ("queue_family_index", c_uint32),
        ("presentation_queue", VkQueue),
        ("presentation_queue_family_index", c_uint32),
    )


retro_vulkan_set_image_t = CFUNCTYPE(
    None, c_void_p, POINTER(retro_vulkan_image), c_uint32, POINTER(VkSemaphore), c_uint32
)
retro_vulkan_get_sync_index_t = CFUNCTYPE(c_uint32, c_void_p)
retro_vulkan_get_sync_index_mask_t = CFUNCTYPE(c_uint32, c_void_p)
retro_vulkan_set_command_buffers_t = CFUNCTYPE(None, c_void_p, c_uint32, POINTER(VkCommandBuffer))
retro_vulkan_wait_sync_index_t = CFUNCTYPE(None, c_void_p)
retro_vulkan_lock_queue_t = CFUNCTYPE(None, c_void_p)
retro_vulkan_unlock_queue_t = CFUNCTYPE(None, c_void_p)
retro_vulkan_set_signal_semaphore_t = CFUNCTYPE(None, c_void_p, VkSemaphore)

retro_vulkan_get_application_info_t = CFUNCTYPE(POINTER(VkApplicationInfo))
retro_vulkan_create_device_t = CFUNCTYPE(
    c_bool,
    POINTER(retro_vulkan_context),
    VkInstance,
    VkPhysicalDevice,
    VkSurfaceKHR,
    PFN_vkGetInstanceProcAddr,
    POINTER(c_char_p),
    c_uint,
    POINTER(c_char_p),
    c_uint,
    POINTER(VkPhysicalDeviceFeatures),
)
retro_vulkan_destroy_device_t = CFUNCTYPE(None)

retro_vulkan_create_instance_wrapper_t = CFUNCTYPE(VkInstance, c_void_p, c_void_p)
"""The second parameter is a ``const VkInstanceCreateInfo *``, opaque at this layer."""

retro_vulkan_create_instance_t = CFUNCTYPE(
    VkInstance,
    PFN_vkGetInstanceProcAddr,
    POINTER(VkApplicationInfo),
    retro_vulkan_create_instance_wrapper_t,
    c_void_p,
)

retro_vulkan_create_device_wrapper_t = CFUNCTYPE(VkDevice, VkPhysicalDevice, c_void_p, c_void_p)
"""The third parameter is a ``const VkDeviceCreateInfo *``, opaque at this layer."""

retro_vulkan_create_device2_t = CFUNCTYPE(
    c_bool,
    POINTER(retro_vulkan_context),
    VkInstance,
    VkPhysicalDevice,
    VkSurfaceKHR,
    PFN_vkGetInstanceProcAddr,
    retro_vulkan_create_device_wrapper_t,
    c_void_p,
)


class retro_hw_render_interface_vulkan(retro_hw_render_interface):
    """
    Corresponds to :c:type:`retro_hw_render_interface_vulkan` in ``libretro_vulkan.h``.

    Filled by the frontend and fetched by the core
    through :attr:`.EnvironmentCall.GET_HW_RENDER_INTERFACE`.
    Extends :class:`.retro_hw_render_interface`,
    so a pointer to this struct may be reinterpreted as its base.
    """

    _fields_ = (
        ("handle", c_void_p),
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


class retro_hw_render_context_negotiation_interface_vulkan(
    retro_hw_render_context_negotiation_interface
):
    """
    Corresponds to :c:type:`retro_hw_render_context_negotiation_interface_vulkan`
    in ``libretro_vulkan.h``.

    Provided by the core
    through :attr:`.EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE`.
    Extends :class:`.retro_hw_render_context_negotiation_interface`.
    This is the version 2 layout;
    cores that only know version 1 leave the trailing fields unset.
    """

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
