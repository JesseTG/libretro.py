from ctypes import Structure, c_double, c_float, c_uint
from dataclasses import dataclass
from enum import CONFORM, IntEnum, IntFlag
from typing import TYPE_CHECKING

RETRO_REGION_NTSC = 0
RETRO_REGION_PAL = 1

retro_av_enable_flags = c_uint
RETRO_AV_ENABLE_VIDEO = 1 << 0
RETRO_AV_ENABLE_AUDIO = 1 << 1
RETRO_AV_ENABLE_FAST_SAVESTATES = 1 << 2
RETRO_AV_ENABLE_HARD_DISABLE_AUDIO = 1 << 3
RETRO_AV_ENABLE_DUMMY = 0x7FFFFFFF


class Region(IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL

    def __init__(self, value: int):
        self._type_ = "I"


class AvEnableFlags(IntFlag, boundary=CONFORM):
    VIDEO = RETRO_AV_ENABLE_VIDEO
    AUDIO = RETRO_AV_ENABLE_AUDIO
    FAST_SAVESTATES = RETRO_AV_ENABLE_FAST_SAVESTATES
    HARD_DISABLE_AUDIO = RETRO_AV_ENABLE_HARD_DISABLE_AUDIO

    ALL = VIDEO | AUDIO | FAST_SAVESTATES | HARD_DISABLE_AUDIO


@dataclass(init=False)
class retro_game_geometry(Structure):
    if TYPE_CHECKING:
        # Structure subclasses implicitly convert primitive fields
        # to and from their ctypes equivalents, so we can define these
        # as their natural types for better type checking and readability.
        base_width: int
        base_height: int
        max_width: int
        max_height: int
        aspect_ratio: float
    else:
        _fields_ = [
            ("base_width", c_uint),
            ("base_height", c_uint),
            ("max_width", c_uint),
            ("max_height", c_uint),
            ("aspect_ratio", c_float),
        ]

    def __deepcopy__(self, _):
        return retro_game_geometry(
            base_width=self.base_width,
            base_height=self.base_height,
            max_width=self.max_width,
            max_height=self.max_height,
            aspect_ratio=self.aspect_ratio,
        )

    @property
    def base_size(self) -> tuple[int, int]:
        return self.base_width, self.base_height

    @property
    def max_size(self) -> tuple[int, int]:
        return self.max_width, self.max_height


@dataclass(init=False)
class retro_system_timing(Structure):
    if TYPE_CHECKING:
        fps: float
        sample_rate: float
    else:
        _fields_ = [
            ("fps", c_double),
            ("sample_rate", c_double),
        ]

    def __deepcopy__(self, _):
        return retro_system_timing(self.fps, self.sample_rate)


@dataclass(init=False)
class retro_system_av_info(Structure):
    if TYPE_CHECKING:
        geometry: retro_game_geometry
        timing: retro_system_timing
    else:
        _fields_ = [
            ("geometry", retro_game_geometry),
            ("timing", retro_system_timing),
        ]

    def __deepcopy__(self, _):
        return retro_system_av_info(self.geometry, self.timing)


__all__ = [
    "Region",
    "AvEnableFlags",
    "retro_game_geometry",
    "retro_system_timing",
    "retro_system_av_info",
    "retro_av_enable_flags",
]
