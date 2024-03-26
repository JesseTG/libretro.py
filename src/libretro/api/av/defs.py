from ctypes import Structure, c_uint, c_float, c_double
from dataclasses import dataclass
from enum import IntFlag, CONFORM, IntEnum

from ..._utils import FieldsFromTypeHints
from ...h import *


class Region(IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL

    def __init__(self, value: int):
        self._type_ = 'I'


class AvEnableFlags(IntFlag, boundary=CONFORM):
    VIDEO = RETRO_AV_ENABLE_VIDEO
    AUDIO = RETRO_AV_ENABLE_AUDIO
    FAST_SAVESTATES = RETRO_AV_ENABLE_FAST_SAVESTATES
    HARD_DISABLE_AUDIO = RETRO_AV_ENABLE_HARD_DISABLE_AUDIO


@dataclass(init=False)
class retro_game_geometry(Structure, metaclass=FieldsFromTypeHints):
    base_width: c_uint
    base_height: c_uint
    max_width: c_uint
    max_height: c_uint
    aspect_ratio: c_float

    def __deepcopy__(self, _):
        return retro_game_geometry(
            base_width=self.base_width,
            base_height=self.base_height,
            max_width=self.max_width,
            max_height=self.max_height,
            aspect_ratio=self.aspect_ratio,
        )


@dataclass(init=False)
class retro_system_timing(Structure, metaclass=FieldsFromTypeHints):
    fps: c_double
    sample_rate: c_double

    def __deepcopy__(self, _):
        return retro_system_timing(self.fps, self.sample_rate)


@dataclass(init=False)
class retro_system_av_info(Structure, metaclass=FieldsFromTypeHints):
    geometry: retro_game_geometry
    timing: retro_system_timing

    def __deepcopy__(self, _):
        return retro_system_av_info(self.geometry, self.timing)


__all__ = [
    "Region",
    "AvEnableFlags",
    "retro_game_geometry",
    "retro_system_timing",
    "retro_system_av_info",
]
