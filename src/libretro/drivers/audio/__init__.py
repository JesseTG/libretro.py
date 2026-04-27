"""
Drivers that receive and optionally process audio data emitted by the core.

.. seealso::

    :mod:`libretro.api.audio`
        Defines the C callback signatures and sample types that audio drivers use.
"""

from .array import *
from .driver import *
from .wave import *
