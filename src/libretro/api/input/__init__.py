"""
Types for input device, state representations, and callbacks.

.. seealso::

    :class:`.InputDriver`
        The :class:`~typing.Protocol` that uses these types to implement input support in libretro.py.

    :mod:`libretro.drivers.input`
        libretro.py's included :class:`.InputDriver` implementations.
"""

from .analog import *
from .device import *
from .joypad import *
from .keyboard import *
from .lightgun import *
from .mouse import *
from .pointer import *
