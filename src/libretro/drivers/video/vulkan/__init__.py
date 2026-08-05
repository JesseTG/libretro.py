"""
Vulkan-backed :class:`.VideoDriver` implementation.

Imports lazily so the rest of :mod:`libretro.drivers.video`
remains usable when the :mod:`vulkan` package
or a Vulkan loader library is not installed.
(The :mod:`vulkan` package loads the Vulkan loader at import time,
which raises :class:`OSError` when no loader is available.)

.. seealso::

    :mod:`libretro.api.video.vulkan`
        The :mod:`ctypes` types from ``libretro_vulkan.h`` this driver implements.
"""

try:
    from .driver import VulkanVideoDriver as VulkanVideoDriver
except (ImportError, OSError):
    __all__ = []
else:
    # An explicit __all__ keeps ``from .vulkan import *`` in the parent package
    # from re-exporting this package's ``driver`` submodule attribute,
    # which would shadow ``libretro.drivers.video.driver``
    __all__ = ["VulkanVideoDriver"]
