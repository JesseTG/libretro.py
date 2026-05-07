"""
Software-rendered :class:`.VideoDriver` implementations.

Used as the default fallback when no hardware-accelerated driver is available
or requested by the core.

.. seealso::

    :mod:`libretro.api.video.frame`
        The frame-format types these drivers consume.
"""

from .array import *
from .base import *
