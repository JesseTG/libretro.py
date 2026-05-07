"""
OpenGL-backed :class:`.VideoDriver` implementations.

Imports lazily so the rest of :mod:`libretro.drivers.video`
remains usable when :mod:`moderngl` or PyOpenGL are not installed.

.. seealso::

    :mod:`libretro.api.video.render`
        The hardware-render callback types these drivers implement.
"""

try:
    from .moderngl import *
except ImportError:
    pass
