from typing import *
from os import PathLike

from .retro import *


Directory = str | bytes
DevicePower = retro_device_power | Callable[[], retro_device_power]
Content: TypeAlias = str | bytes | PathLike | retro_game_info

class SpecialContent(NamedTuple):
    game_type: int
    info: Sequence[Content]

