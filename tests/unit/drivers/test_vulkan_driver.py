# The vulkan package is untyped CFFI; see the note in the driver module.
# These tests also assert on the driver's private frame-path state,
# and call the render interface's function pointers the way a C core would
# (passing NULL handles and byref pointers that the declared types don't admit).
# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportPrivateUsage=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false
# pyright: reportArgumentType=false, reportCallIssue=false
# pyright: reportOptionalCall=false, reportOptionalMemberAccess=false

from ctypes import byref, c_ubyte

import pytest

vk = pytest.importorskip("vulkan", reason="the libretro.py[vulkan] extra is not installed")

from vulkan import ffi  # noqa: E402

from libretro.api.av import (  # noqa: E402
    retro_game_geometry,
    retro_system_av_info,
    retro_system_timing,
)
from libretro.api.video import (  # noqa: E402
    ContextNegotiationInterfaceType,
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    VkImageSubresourceRange,
    VkImageViewCreateInfo,
    retro_hw_context_reset_t,
    retro_hw_render_callback,
    retro_hw_render_context_negotiation_interface_vulkan,
    retro_hw_render_interface_vulkan,
    retro_vulkan_create_device2_t,
    retro_vulkan_create_device_t,
    retro_vulkan_create_instance_t,
    retro_vulkan_image,
)
from libretro.drivers.video import FrameBufferSpecial, UnsupportedContextError  # noqa: E402
from libretro.drivers.video.vulkan import VulkanVideoDriver  # noqa: E402

pytestmark = [pytest.mark.vulkan, pytest.mark.isolated]

WIDTH = 64
HEIGHT = 48

VK_FORMAT_R8G8B8A8_UNORM = 37
VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL = 5
VK_IMAGE_ASPECT_COLOR_BIT = 1


def _av_info() -> retro_system_av_info:
    return retro_system_av_info(
        geometry=retro_game_geometry(
            base_width=WIDTH,
            base_height=HEIGHT,
            max_width=WIDTH,
            max_height=HEIGHT,
            aspect_ratio=WIDTH / HEIGHT,
        ),
        timing=retro_system_timing(fps=60.0, sample_rate=44100.0),
    )


def _vulkan_callback() -> retro_hw_render_callback:
    return retro_hw_render_callback(
        context_type=HardwareContext.VULKAN,
        version_major=1,
        version_minor=1,
    )


def test_driver_contexts():
    driver = VulkanVideoDriver()
    assert HardwareContext.VULKAN in driver.supported_contexts
    assert HardwareContext.NONE in driver.supported_contexts
    assert driver.preferred_context == HardwareContext.VULKAN
    assert driver.active_context == HardwareContext.NONE


def test_driver_rejects_opengl_context():
    driver = VulkanVideoDriver()
    with pytest.raises(UnsupportedContextError):
        driver.set_context(retro_hw_render_callback(context_type=HardwareContext.OPENGL))


def test_software_frame_screenshot():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()

    # One red XRGB8888 (B, G, R, X) frame
    frame = bytearray(b"\x00\x00\xff\x00" * (WIDTH * HEIGHT))
    driver.refresh(memoryview(frame), WIDTH, HEIGHT, WIDTH * 4)

    # Software frames go through a VkImage, like the GL driver's texture upload
    assert driver._hw_frame is not None

    shot = driver.screenshot()
    assert shot is not None
    assert (shot.width, shot.height) == (WIDTH, HEIGHT)
    assert bytes(shot.data[:4]) == b"\xff\x00\x00\xff"


def test_software_frame_with_padded_pitch():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()

    pitch = WIDTH * 4 + 32  # Rows padded past the visible width
    frame = bytearray(pitch * HEIGHT)
    for y in range(HEIGHT):
        frame[y * pitch : y * pitch + WIDTH * 4] = b"\x00\xff\x00\x00" * WIDTH  # Green
    driver.refresh(memoryview(frame), WIDTH, HEIGHT, pitch)

    assert driver._hw_frame is not None
    shot = driver.screenshot()
    assert shot is not None
    assert bytes(shot.data[:4]) == b"\x00\xff\x00\xff"
    end = (WIDTH * HEIGHT - 1) * 4
    assert bytes(shot.data[end : end + 4]) == b"\x00\xff\x00\xff"


def test_software_frame_rgb565():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.RGB565
    driver.system_av_info = _av_info()

    # Pure blue in RGB565 is 0x001F (little-endian bytes 1F 00)
    frame = bytearray(b"\x1f\x00" * (WIDTH * HEIGHT))
    driver.refresh(memoryview(frame), WIDTH, HEIGHT, WIDTH * 2)

    assert driver._hw_frame is not None
    shot = driver.screenshot()
    assert shot is not None
    assert bytes(shot.data[:4]) == b"\x00\x00\xff\xff"


def _init_hw_driver() -> tuple[VulkanVideoDriver, list[int]]:
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    resets: list[int] = []
    callback = _vulkan_callback()
    callback.context_reset = retro_hw_context_reset_t(lambda: resets.append(1))
    driver.set_context(callback)
    driver.system_av_info = _av_info()  # triggers reinit
    return driver, resets


def test_hw_context_bringup():
    driver, resets = _init_hw_driver()

    assert resets == [1]
    iface = driver.hw_render_interface
    assert isinstance(iface, retro_hw_render_interface_vulkan)
    assert iface.interface_version == 5
    assert iface.instance
    assert iface.gpu
    assert iface.device
    assert iface.queue
    assert iface.get_instance_proc_addr
    assert iface.get_device_proc_addr

    # The callbacks must be usable through the ABI, like a core would use them
    n = driver.sync_indices
    assert iface.get_sync_index_mask(iface.handle) == (1 << n) - 1
    index = iface.get_sync_index(iface.handle)
    assert 0 <= index < n
    iface.lock_queue(iface.handle)
    iface.unlock_queue(iface.handle)
    iface.wait_sync_index(iface.handle)


class _FakeCoreImage:
    """Stands in for a core's Vulkan renderer: clears an image to a color."""

    def __init__(self, iface: retro_hw_render_interface_vulkan):
        # Interface handles are c_void_ptr instances; CFFI needs their raw addresses
        self.device = ffi.cast("VkDevice", iface.device.value)
        self.gpu = ffi.cast("VkPhysicalDevice", iface.gpu.value)
        self.queue = ffi.cast("VkQueue", iface.queue.value)
        self.queue_index = iface.queue_index
        self.iface = iface

        image_info = vk.VkImageCreateInfo(
            imageType=vk.VK_IMAGE_TYPE_2D,
            format=VK_FORMAT_R8G8B8A8_UNORM,
            extent=vk.VkExtent3D(WIDTH, HEIGHT, 1),
            mipLevels=1,
            arrayLayers=1,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            tiling=vk.VK_IMAGE_TILING_OPTIMAL,
            usage=(
                vk.VK_IMAGE_USAGE_TRANSFER_SRC_BIT
                | vk.VK_IMAGE_USAGE_TRANSFER_DST_BIT
                | vk.VK_IMAGE_USAGE_SAMPLED_BIT
            ),
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
        )
        self.image = vk.vkCreateImage(self.device, image_info, None)

        reqs = vk.vkGetImageMemoryRequirements(self.device, self.image)
        mem_props = vk.vkGetPhysicalDeviceMemoryProperties(self.gpu)
        type_index = next(
            i
            for i in range(mem_props.memoryTypeCount)
            if (reqs.memoryTypeBits >> i) & 1
            and mem_props.memoryTypes[i].propertyFlags & vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        )
        self.memory = vk.vkAllocateMemory(
            self.device,
            vk.VkMemoryAllocateInfo(allocationSize=reqs.size, memoryTypeIndex=type_index),
            None,
        )
        vk.vkBindImageMemory(self.device, self.image, self.memory, 0)

        view_info = vk.VkImageViewCreateInfo(
            image=self.image,
            viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
            format=VK_FORMAT_R8G8B8A8_UNORM,
            components=vk.VkComponentMapping(0, 0, 0, 0),
            subresourceRange=vk.VkImageSubresourceRange(VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1),
        )
        self.view = vk.vkCreateImageView(self.device, view_info, None)

        self.pool = vk.vkCreateCommandPool(
            self.device,
            vk.VkCommandPoolCreateInfo(
                flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
                queueFamilyIndex=self.queue_index,
            ),
            None,
        )
        self.cmd = vk.vkAllocateCommandBuffers(
            self.device,
            vk.VkCommandBufferAllocateInfo(
                commandPool=self.pool,
                level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
                commandBufferCount=1,
            ),
        )[0]
        self.fence = vk.vkCreateFence(self.device, vk.VkFenceCreateInfo(), None)

    def render(self, r: float, g: float, b: float) -> None:
        vk.vkResetCommandBuffer(self.cmd, 0)
        vk.vkBeginCommandBuffer(
            self.cmd,
            vk.VkCommandBufferBeginInfo(flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT),
        )
        subresource = vk.VkImageSubresourceRange(VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1)
        to_dst = vk.VkImageMemoryBarrier(
            srcAccessMask=0,
            dstAccessMask=vk.VK_ACCESS_TRANSFER_WRITE_BIT,
            oldLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            newLayout=vk.VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
            srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,
            dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,
            image=self.image,
            subresourceRange=subresource,
        )
        vk.vkCmdPipelineBarrier(
            self.cmd,
            vk.VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
            vk.VK_PIPELINE_STAGE_TRANSFER_BIT,
            0,
            0,
            None,
            0,
            None,
            1,
            [to_dst],
        )
        color = vk.VkClearColorValue(float32=[r, g, b, 1.0])
        vk.vkCmdClearColorImage(
            self.cmd,
            self.image,
            vk.VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
            color,
            1,
            [subresource],
        )
        to_shader = vk.VkImageMemoryBarrier(
            srcAccessMask=vk.VK_ACCESS_TRANSFER_WRITE_BIT,
            dstAccessMask=vk.VK_ACCESS_SHADER_READ_BIT,
            oldLayout=vk.VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
            newLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
            srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,
            dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,
            image=self.image,
            subresourceRange=subresource,
        )
        vk.vkCmdPipelineBarrier(
            self.cmd,
            vk.VK_PIPELINE_STAGE_TRANSFER_BIT,
            vk.VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT,
            0,
            0,
            None,
            0,
            None,
            1,
            [to_shader],
        )
        vk.vkEndCommandBuffer(self.cmd)

        submit = vk.VkSubmitInfo(commandBufferCount=1, pCommandBuffers=[self.cmd])
        self.iface.lock_queue(self.iface.handle)
        try:
            vk.vkQueueSubmit(self.queue, 1, [submit], self.fence)
        finally:
            self.iface.unlock_queue(self.iface.handle)
        vk.vkWaitForFences(self.device, 1, [self.fence], vk.VK_TRUE, 10_000_000_000)
        vk.vkResetFences(self.device, 1, [self.fence])

    def libretro_image(self) -> retro_vulkan_image:
        raw_view = int(ffi.cast("uint64_t", self.view))
        raw_image = int(ffi.cast("uint64_t", self.image))
        return retro_vulkan_image(
            image_view=raw_view,
            image_layout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
            create_info=VkImageViewCreateInfo(
                image=raw_image,
                format=VK_FORMAT_R8G8B8A8_UNORM,
                subresourceRange=VkImageSubresourceRange(VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1),
            ),
        )


def test_hw_frame_capture_and_screenshot():
    driver, _ = _init_hw_driver()
    iface = driver.hw_render_interface
    assert isinstance(iface, retro_hw_render_interface_vulkan)

    core = _FakeCoreImage(iface)
    core.render(1.0, 0.0, 0.0)  # pure red

    image = core.libretro_image()
    iface.set_image(iface.handle, byref(image), 0, None, iface.queue_index)

    index_before = iface.get_sync_index(iface.handle)
    driver.refresh(FrameBufferSpecial.HARDWARE, WIDTH, HEIGHT, 0)
    index_after = iface.get_sync_index(iface.handle)
    assert index_after == (index_before + 1) % driver.sync_indices

    shot = driver.screenshot()
    assert shot is not None
    assert (shot.width, shot.height) == (WIDTH, HEIGHT)
    assert bytes(shot.data[:4]) == b"\xff\x00\x00\xff"
    # A pixel in the middle too, not just the first one
    mid = (HEIGHT // 2 * WIDTH + WIDTH // 2) * 4
    assert bytes(shot.data[mid : mid + 4]) == b"\xff\x00\x00\xff"


def test_hw_frame_dupe_keeps_frame():
    driver, _ = _init_hw_driver()
    iface = driver.hw_render_interface
    assert isinstance(iface, retro_hw_render_interface_vulkan)

    core = _FakeCoreImage(iface)
    core.render(0.0, 1.0, 0.0)  # pure green
    image = core.libretro_image()
    iface.set_image(iface.handle, byref(image), 0, None, iface.queue_index)
    driver.refresh(FrameBufferSpecial.HARDWARE, WIDTH, HEIGHT, 0)

    driver.refresh(FrameBufferSpecial.DUPE, WIDTH, HEIGHT, 0)
    shot = driver.screenshot()
    assert shot is not None
    assert bytes(shot.data[:4]) == b"\x00\xff\x00\xff"


def test_context_destroy_called_on_teardown():
    driver, _ = _init_hw_driver()
    assert driver.hw_render_interface is not None

    # Requesting a software context and reinitializing must tear down Vulkan
    driver.set_context(retro_hw_render_callback(context_type=HardwareContext.NONE))
    driver.reinit()
    assert driver.hw_render_interface is None


def test_software_dupe_keeps_frame():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()

    frame = bytearray(b"\x00\x00\xff\x00" * (WIDTH * HEIGHT))  # Red
    driver.refresh(memoryview(frame), WIDTH, HEIGHT, WIDTH * 4)
    driver.refresh(FrameBufferSpecial.DUPE, WIDTH, HEIGHT, 0)

    shot = driver.screenshot()
    assert shot is not None
    assert bytes(shot.data[:4]) == b"\xff\x00\x00\xff"


def test_rotation_applies_to_vulkan_frames():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()
    driver.rotation = Rotation.NINETY

    frame = bytearray(b"\x00\x00\xff\x00" * (WIDTH * HEIGHT))
    driver.refresh(memoryview(frame), WIDTH, HEIGHT, WIDTH * 4)

    shot = driver.screenshot()
    assert shot is not None
    assert (shot.width, shot.height) == (HEIGHT, WIDTH)
    assert shot.rotation == Rotation.NINETY


def test_reinit_fails_without_vulkan(monkeypatch: pytest.MonkeyPatch):
    import libretro.drivers.video.vulkan.driver as driver_module

    def _no_loader():
        raise RuntimeError("No Vulkan loader for this test")

    monkeypatch.setattr(driver_module, "_load_loader", _no_loader)

    driver = VulkanVideoDriver()
    with pytest.raises(RuntimeError):
        driver.system_av_info = _av_info()


def test_geometry_reports_rendered_frame_size():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()

    geometry = driver.geometry
    assert geometry is not None
    assert (geometry.base_width, geometry.base_height) == (WIDTH, HEIGHT)

    half_w, half_h = WIDTH // 2, HEIGHT // 2
    frame = bytearray(b"\x00\x00\xff\x00" * (half_w * half_h))
    driver.refresh(memoryview(frame), half_w, half_h, half_w * 4)

    geometry = driver.geometry
    assert geometry is not None
    assert (geometry.base_width, geometry.base_height) == (half_w, half_h)


def test_get_software_framebuffer_maps_vulkan_memory():
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.system_av_info = _av_info()

    fb = driver.get_software_framebuffer(WIDTH, HEIGHT, MemoryAccess.WRITE | MemoryAccess.READ)
    assert fb is not None
    assert fb.data is not None
    assert fb.format == PixelFormat.XRGB8888
    assert fb.pitch == WIDTH * 4

    # Render into the mapped Vulkan memory like a core would,
    # then present it through the ordinary refresh path
    buf = (c_ubyte * (HEIGHT * fb.pitch)).from_address(fb.data.value)
    view = memoryview(buf).cast("B")
    view[:] = b"\x00\xff\x00\x00" * (WIDTH * HEIGHT)  # Green
    driver.refresh(view, WIDTH, HEIGHT, fb.pitch)

    shot = driver.screenshot()
    assert shot is not None
    assert bytes(shot.data[:4]) == b"\x00\xff\x00\xff"


def test_negotiation_version_delegated_to_driver():
    assert (
        VulkanVideoDriver().context_negotiation_version(ContextNegotiationInterfaceType.VULKAN)
        == 2
    )

    driver = VulkanVideoDriver(negotiation_version=1)
    assert driver.context_negotiation_version(ContextNegotiationInterfaceType.VULKAN) == 1

    with pytest.raises(ValueError):
        VulkanVideoDriver(negotiation_version=0)

    with pytest.raises(ValueError):
        VulkanVideoDriver(negotiation_version=3)


def _negotiation_recorder(
    calls: list[str],
) -> retro_hw_render_context_negotiation_interface_vulkan:
    """A fake core-side negotiation interface that records calls and always fails."""

    def _create_device(*_args: object) -> bool:
        calls.append("create_device")
        return False

    def _create_device2(*_args: object) -> bool:
        calls.append("create_device2")
        return False

    def _create_instance(*_args: object) -> int:
        calls.append("create_instance")
        return 0

    return retro_hw_render_context_negotiation_interface_vulkan(
        interface_type=ContextNegotiationInterfaceType.VULKAN,
        interface_version=2,
        create_device=retro_vulkan_create_device_t(_create_device),
        create_instance=retro_vulkan_create_instance_t(_create_instance),
        create_device2=retro_vulkan_create_device2_t(_create_device2),
    )


def test_v2_negotiation_uses_v2_callbacks():
    calls: list[str] = []
    driver = VulkanVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    driver.set_context(_vulkan_callback())
    driver.context_negotiation_interface = _negotiation_recorder(calls)
    driver.system_av_info = _av_info()

    assert "create_instance" in calls
    assert "create_device2" in calls


def test_v1_frontend_skips_v2_negotiation_callbacks():
    calls: list[str] = []
    driver = VulkanVideoDriver(negotiation_version=1)
    driver.pixel_format = PixelFormat.XRGB8888
    driver.set_context(_vulkan_callback())
    driver.context_negotiation_interface = _negotiation_recorder(calls)
    driver.system_av_info = _av_info()

    assert "create_device" in calls
    assert "create_instance" not in calls
    assert "create_device2" not in calls
