"""
Driver protocols and implementations for video output and rendering.

Includes a software fallback and optional hardware-accelerated backends.

.. seealso::

    :mod:`libretro.api.video`
        The matching :mod:`ctypes` types and callback definitions.
"""

from .driver import *
from .multi import *
from .software import *

try:
    from .opengl import *
except ImportError:
    pass
