Running Vulkan Cores
====================

libretro.py includes :class:`.VulkanVideoDriver`,
a headless video driver for cores that render with Vulkan
(``RETRO_HW_CONTEXT_VULKAN``),
such as Azahar or other 3D-heavy emulators
whose OpenGL renderers are unavailable or too slow on some platforms.

The driver implements the full version 5
:class:`.retro_hw_render_interface_vulkan`
and the Vulkan context negotiation interface;
each hardware frame is copied into host memory,
so :meth:`.VideoDriver.screenshot` works the same way it does
with the OpenGL and software drivers.
There is no window or swapchain.

Installation
------------

Install the ``vulkan`` extra alongside libretro.py::

    pip install libretro.py[vulkan]

The driver also needs a Vulkan loader library at runtime:

Linux
    Install the Vulkan loader from your package manager
    (e.g. ``libvulkan1`` on Debian/Ubuntu).

Windows
    ``vulkan-1.dll`` ships with your graphics driver.

macOS
    Install MoltenVK_ and the Vulkan loader,
    e.g. with Homebrew::

        brew install molten-vk vulkan-loader

    A Homebrew-installed Python will find ``libvulkan.dylib`` automatically.
    Other Python builds may need the library path set at launch::

        DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python my_script.py

Usage
-----

When the ``vulkan`` extra is installed,
:data:`.DEFAULT_DRIVER_MAP` automatically maps
:attr:`.HardwareContext.VULKAN` to :class:`.VulkanVideoDriver`,
so a default :class:`.Session` will use it
whenever a core requests a Vulkan context.
To use it explicitly::

    from libretro.drivers.video.vulkan import VulkanVideoDriver

    driver = VulkanVideoDriver()

.. _MoltenVK: https://github.com/KhronosGroup/MoltenVK
