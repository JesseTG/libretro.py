"""
Video callback and rendering types.

.. seealso::

    :class:`.VideoDriver`
        The :class:`~typing.Protocol` that uses these types to implement video output support in libretro.py.

    :mod:`libretro.drivers.video`
        libretro.py's included :class:`.VideoDriver` implementations.
"""

from .context import *
from .frame import *
from .negotiate import *
from .render import *
