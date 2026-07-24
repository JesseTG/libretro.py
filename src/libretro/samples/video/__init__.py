"""
Video-rendering sample cores from libretro-samples ``video/``.

Names exposed by this subpackage:

* ``software_rendering`` — pure software rasteriser.
* ``software_direct_to_vram`` — uses ``GET_CURRENT_SOFTWARE_FRAMEBUFFER`` for zero-copy output.
* ``gl_fixedfunction`` — legacy OpenGL 1.x fixed-function pipeline.
* ``gl_shaders`` — OpenGL 2.x core profile with vertex/fragment shaders.
* ``gl_compute_shaders`` — OpenGL 4.3 compute shader demo (C++).
* ``vulkan_rendering`` — Vulkan triangle demo using the HW render interface.

OpenGL- and Vulkan-backed cores are only present on platforms where the build
environment included the matching graphics headers; on systems without them
the core build is skipped and lookup raises :class:`ImportError`.

.. seealso::

    :mod:`libretro.samples`
        Overview of all sample-core categories and their lazy-loading semantics.
"""

from libretro.samples._loader import load_sample_core

_NAMES = (
    "software_rendering",
    "software_direct_to_vram",
    "gl_fixedfunction",
    "gl_shaders",
    #    "gl_compute_shaders",
    "vulkan_rendering",
)


def __getattr__(name: str):
    """Lazily load a sample core by name from this category."""
    if name in _NAMES:
        return load_sample_core("video", name)
    raise AttributeError(f"module 'libretro.samples.video' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_NAMES]
