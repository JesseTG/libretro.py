import logging
from collections.abc import *
from typing import *
import enum
from os import PathLike

from .retro import *


Directory = str | bytes
DevicePower = retro_device_power | Callable[[], retro_device_power]

if sys.version_info >= (3, 12):
    Content: TypeAlias = PathLike | bytes | bytearray | memoryview | Buffer
    # Buffer was added in Python 3.12
else:
    Content: TypeAlias = PathLike | bytes | bytearray | memoryview


