# ctypes Structure field descriptors expose .offset at runtime,
# which pyright can't see through the dataclass-style annotations.
# pyright: reportUnknownMemberType=false, reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false

from copy import deepcopy
from ctypes import addressof, sizeof

from libretro.api.video import (
    RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN_VERSION,
    RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION,
    VkApplicationInfo,
    VkComponentMapping,
    VkImageSubresourceRange,
    VkImageViewCreateInfo,
    VkPhysicalDeviceFeatures,
    retro_hw_render_context_negotiation_interface_vulkan,
    retro_hw_render_interface_vulkan,
    retro_vulkan_context,
    retro_vulkan_image,
)

# Reference values computed on a 64-bit platform from the C headers
# (vulkan_core.h 1.4.341 and libretro_vulkan.h negotiation v2).


def test_version_constants():
    assert RETRO_HW_RENDER_INTERFACE_VULKAN_VERSION == 5
    assert RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN_VERSION == 2


def test_vk_struct_sizes():
    assert sizeof(VkApplicationInfo) == 48
    assert sizeof(VkComponentMapping) == 16
    assert sizeof(VkImageSubresourceRange) == 20
    assert sizeof(VkImageViewCreateInfo) == 80
    assert sizeof(VkPhysicalDeviceFeatures) == 220


def test_image_view_create_info_offsets():
    assert VkImageViewCreateInfo.image.offset == 24
    assert VkImageViewCreateInfo.components.offset == 40
    assert VkImageViewCreateInfo.subresourceRange.offset == 56


def test_retro_vulkan_image_layout():
    assert sizeof(retro_vulkan_image) == 96
    assert retro_vulkan_image.image_layout.offset == 8
    assert retro_vulkan_image.create_info.offset == 16


def test_retro_vulkan_context_layout():
    assert sizeof(retro_vulkan_context) == 48
    assert retro_vulkan_context.queue_family_index.offset == 24
    assert retro_vulkan_context.presentation_queue.offset == 32


def test_render_interface_layout():
    assert sizeof(retro_hw_render_interface_vulkan) == 136
    iface = retro_hw_render_interface_vulkan
    assert iface.interface_type.offset == 0
    assert iface.interface_version.offset == 4
    assert iface.handle.offset == 8
    assert iface.instance.offset == 16
    assert iface.gpu.offset == 24
    assert iface.device.offset == 32
    assert iface.get_device_proc_addr.offset == 40
    assert iface.get_instance_proc_addr.offset == 48
    assert iface.queue.offset == 56
    assert iface.queue_index.offset == 64
    assert iface.set_image.offset == 72
    assert iface.get_sync_index.offset == 80
    assert iface.get_sync_index_mask.offset == 88
    assert iface.set_command_buffers.offset == 96
    assert iface.wait_sync_index.offset == 104
    assert iface.lock_queue.offset == 112
    assert iface.unlock_queue.offset == 120
    assert iface.set_signal_semaphore.offset == 128


def test_negotiation_interface_layout():
    assert sizeof(retro_hw_render_context_negotiation_interface_vulkan) == 48
    iface = retro_hw_render_context_negotiation_interface_vulkan
    assert iface.get_application_info.offset == 8
    assert iface.create_device.offset == 16
    assert iface.destroy_device.offset == 24
    assert iface.create_instance.offset == 32
    assert iface.create_device2.offset == 40


def test_physical_device_features_field_count_and_names():
    fields = VkPhysicalDeviceFeatures._fields_
    assert len(fields) == 55
    assert fields[0][0] == "robustBufferAccess"
    assert fields[-1][0] == "inheritedQueries"
    assert fields[20][0] == "textureCompressionETC2"


def test_null_function_pointers_read_as_none():
    iface = retro_hw_render_interface_vulkan()
    assert iface.handle is None
    assert iface.set_image is None
    assert iface.get_sync_index is None
    assert iface.set_signal_semaphore is None

    negotiation = retro_hw_render_context_negotiation_interface_vulkan()
    assert negotiation.get_application_info is None
    assert negotiation.create_device is None
    assert negotiation.create_device2 is None


def test_null_context_handles_read_as_none():
    context = retro_vulkan_context()
    assert context.gpu is None
    assert context.device is None
    assert context.queue is None
    assert context.presentation_queue is None


def test_component_mapping_deepcopy():
    mapping = VkComponentMapping(r=1, g=2, b=3, a=4)
    copied = deepcopy(mapping)
    assert copied is not mapping
    assert addressof(copied) != addressof(mapping)
    assert (copied.r, copied.g, copied.b, copied.a) == (1, 2, 3, 4)


def test_subresource_range_deepcopy():
    subresource = VkImageSubresourceRange(
        aspectMask=1, baseMipLevel=2, levelCount=3, baseArrayLayer=4, layerCount=5
    )
    copied = deepcopy(subresource)
    assert addressof(copied) != addressof(subresource)
    assert copied.aspectMask == 1
    assert copied.layerCount == 5


def test_physical_device_features_deepcopy():
    features = VkPhysicalDeviceFeatures(robustBufferAccess=1, inheritedQueries=1)
    copied = deepcopy(features)
    assert addressof(copied) != addressof(features)
    assert copied.robustBufferAccess == 1
    assert copied.inheritedQueries == 1
    assert copied.geometryShader == 0
