"""
Typed declarations for the subset of the :mod:`vulkan` package
used by :class:`.VulkanVideoDriver`.

The :mod:`vulkan` package is generated CFFI code without type information,
so this module declares the functions, struct constructors, and constants
that the driver uses, in the spirit of :mod:`libretro.ctypes`:
the declarations exist only for static analysis
and erase to the real (untyped) module at runtime.

Vulkan handles and structs are opaque CFFI ``cdata`` objects (``CData``,
from the :mod:`cffi` type stubs), and memory mapped with ``vkMapMemory``
is a CFFI buffer (``CBuffer``).
"""

# pyright: reportPrivateUsage=false
# The cffi type stubs only expose the cdata type under a private name.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any, Protocol

    from _cffi_backend import _CDataBase
    from cffi import FFI

    type CData = _CDataBase
    """An opaque CFFI ``cdata`` object, e.g. a Vulkan handle or struct."""

    class CBuffer(Protocol):
        """
        The slice of the CFFI ``buffer`` interface used by the driver:
        reading a slice yields :class:`bytes`, writing accepts them,
        and the whole mapping can be re-exported through the buffer protocol.
        """

        def __len__(self) -> int: ...
        def __getitem__(self, index: slice, /) -> bytes: ...
        def __setitem__(self, index: slice, value: bytes, /) -> None: ...
        def __buffer__(self, flags: int, /) -> memoryview: ...

    class _VulkanModule(Protocol):
        """The names the driver uses from the :mod:`vulkan` package."""

        VK_TRUE: int
        VK_QUEUE_FAMILY_IGNORED: int

        VK_ACCESS_MEMORY_READ_BIT: int
        VK_ACCESS_MEMORY_WRITE_BIT: int
        VK_ACCESS_TRANSFER_READ_BIT: int
        VK_ACCESS_TRANSFER_WRITE_BIT: int
        VK_BUFFER_USAGE_TRANSFER_DST_BIT: int
        VK_BUFFER_USAGE_TRANSFER_SRC_BIT: int
        VK_COMMAND_BUFFER_LEVEL_PRIMARY: int
        VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT: int
        VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT: int
        VK_IMAGE_ASPECT_COLOR_BIT: int
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL: int
        VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL: int
        VK_IMAGE_LAYOUT_UNDEFINED: int
        VK_IMAGE_TILING_OPTIMAL: int
        VK_IMAGE_TYPE_2D: int
        VK_IMAGE_USAGE_TRANSFER_DST_BIT: int
        VK_IMAGE_USAGE_TRANSFER_SRC_BIT: int
        VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR: int
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT: int
        VK_MEMORY_PROPERTY_HOST_CACHED_BIT: int
        VK_MEMORY_PROPERTY_HOST_COHERENT_BIT: int
        VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT: int
        VK_PIPELINE_STAGE_ALL_COMMANDS_BIT: int
        VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT: int
        VK_PIPELINE_STAGE_TRANSFER_BIT: int
        VK_QUEUE_COMPUTE_BIT: int
        VK_QUEUE_GRAPHICS_BIT: int
        VK_SAMPLE_COUNT_1_BIT: int
        VK_SHARING_MODE_EXCLUSIVE: int

        VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME: str
        VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME: str
        VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME: str

        # Struct constructors; their keyword arguments mirror the C fields
        VkApplicationInfo: Callable[..., CData]
        VkBufferCreateInfo: Callable[..., CData]
        VkBufferImageCopy: Callable[..., CData]
        VkCommandBufferAllocateInfo: Callable[..., CData]
        VkCommandBufferBeginInfo: Callable[..., CData]
        VkCommandPoolCreateInfo: Callable[..., CData]
        VkDeviceCreateInfo: Callable[..., CData]
        VkDeviceQueueCreateInfo: Callable[..., CData]
        VkExtent3D: Callable[..., CData]
        VkFenceCreateInfo: Callable[..., CData]
        VkHeadlessSurfaceCreateInfoEXT: Callable[..., CData]
        VkImageCreateInfo: Callable[..., CData]
        VkImageMemoryBarrier: Callable[..., CData]
        VkImageSubresourceLayers: Callable[..., CData]
        VkImageSubresourceRange: Callable[..., CData]
        VkInstanceCreateInfo: Callable[..., CData]
        VkMemoryAllocateInfo: Callable[..., CData]
        VkOffset3D: Callable[..., CData]
        VkSubmitInfo: Callable[..., CData]

        def vkCreateInstance(self, create_info: Any, allocator: None, /) -> CData: ...
        def vkDestroyInstance(self, instance: CData, allocator: None, /) -> None: ...
        def vkGetInstanceProcAddr(
            self, instance: CData | None, name: str, /
        ) -> Callable[..., Any] | None: ...
        def vkEnumeratePhysicalDevices(self, instance: CData, /) -> Sequence[CData]: ...
        def vkEnumerateInstanceExtensionProperties(
            self, layer_name: str | None, /
        ) -> Sequence[Any]: ...
        def vkEnumerateDeviceExtensionProperties(
            self, gpu: CData, layer_name: str | None, /
        ) -> Sequence[Any]: ...
        def vkGetPhysicalDeviceQueueFamilyProperties(self, gpu: CData, /) -> Sequence[Any]: ...
        def vkGetPhysicalDeviceFeatures(self, gpu: CData, /) -> CData: ...
        def vkGetPhysicalDeviceMemoryProperties(self, gpu: CData, /) -> Any: ...
        def vkCreateDevice(self, gpu: CData, create_info: Any, allocator: None, /) -> CData: ...
        def vkDestroyDevice(self, device: CData, allocator: None, /) -> None: ...
        def vkDeviceWaitIdle(self, device: CData, /) -> None: ...
        def vkGetDeviceQueue(self, device: CData, family: int, index: int, /) -> CData: ...
        def vkQueueSubmit(
            self, queue: CData, count: int, submits: Sequence[CData], fence: CData, /
        ) -> None: ...
        def vkQueueWaitIdle(self, queue: CData, /) -> None: ...
        def vkCreateCommandPool(
            self, device: CData, create_info: Any, allocator: None, /
        ) -> CData: ...
        def vkDestroyCommandPool(self, device: CData, pool: CData, allocator: None, /) -> None: ...
        def vkAllocateCommandBuffers(self, device: CData, info: Any, /) -> Sequence[CData]: ...
        def vkResetCommandBuffer(self, cmd: CData, flags: int, /) -> None: ...
        def vkBeginCommandBuffer(self, cmd: CData, info: Any, /) -> None: ...
        def vkEndCommandBuffer(self, cmd: CData, /) -> None: ...
        def vkCreateFence(self, device: CData, info: Any, allocator: None, /) -> CData: ...
        def vkDestroyFence(self, device: CData, fence: CData, allocator: None, /) -> None: ...
        def vkWaitForFences(
            self,
            device: CData,
            count: int,
            fences: Sequence[CData],
            wait_all: int,
            timeout: int,
            /,
        ) -> None: ...
        def vkResetFences(self, device: CData, count: int, fences: Sequence[CData], /) -> None: ...
        def vkCreateBuffer(self, device: CData, info: Any, allocator: None, /) -> CData: ...
        def vkDestroyBuffer(self, device: CData, buffer: CData, allocator: None, /) -> None: ...
        def vkCreateImage(self, device: CData, info: Any, allocator: None, /) -> CData: ...
        def vkDestroyImage(self, device: CData, image: CData, allocator: None, /) -> None: ...
        def vkGetBufferMemoryRequirements(self, device: CData, buffer: CData, /) -> Any: ...
        def vkGetImageMemoryRequirements(self, device: CData, image: CData, /) -> Any: ...
        def vkAllocateMemory(self, device: CData, info: Any, allocator: None, /) -> CData: ...
        def vkFreeMemory(self, device: CData, memory: CData, allocator: None, /) -> None: ...
        def vkBindBufferMemory(
            self, device: CData, buffer: CData, memory: CData, offset: int, /
        ) -> None: ...
        def vkBindImageMemory(
            self, device: CData, image: CData, memory: CData, offset: int, /
        ) -> None: ...
        def vkMapMemory(
            self, device: CData, memory: CData, offset: int, size: int, flags: int, /
        ) -> CBuffer: ...
        def vkUnmapMemory(self, device: CData, memory: CData, /) -> None: ...
        def vkCmdPipelineBarrier(
            self,
            cmd: CData,
            src_stage_mask: int,
            dst_stage_mask: int,
            dependency_flags: int,
            memory_barrier_count: int,
            memory_barriers: Sequence[CData] | None,
            buffer_barrier_count: int,
            buffer_barriers: Sequence[CData] | None,
            image_barrier_count: int,
            image_barriers: Sequence[CData] | None,
            /,
        ) -> None: ...
        def vkCmdCopyBufferToImage(
            self,
            cmd: CData,
            buffer: CData,
            image: CData,
            layout: int,
            count: int,
            regions: Sequence[CData],
            /,
        ) -> None: ...
        def vkCmdCopyImageToBuffer(
            self,
            cmd: CData,
            image: CData,
            layout: int,
            buffer: CData,
            count: int,
            regions: Sequence[CData],
            /,
        ) -> None: ...

    vk: _VulkanModule
    ffi: FFI
else:
    import vulkan as vk
    from vulkan import ffi

    # Placeholders so the names above are importable at runtime;
    # they only carry meaning for static analysis
    CData = object
    CBuffer = object

__all__ = ["CBuffer", "CData", "ffi", "vk"]
