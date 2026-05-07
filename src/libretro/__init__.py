"""
A libretro frontend for Python intended for testing cores.

Top-level package that re-exports the public API
from :mod:`libretro.api`, :mod:`libretro.drivers`,
:class:`.Core`, :class:`.Session`, and :class:`.SessionBuilder`.
"""

from .api import *
from .builder import *
from .core import *
from .drivers import *
from .error import *
from .session import *
