from ctypes import Structure, c_bool, c_double, c_float, c_uint
from enum import IntEnum

from .._utils import FieldsFromTypeHints, String
from ..h import *


class Region(IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL

    def __init__(self, value: int):
        self._type_ = 'I'


class Language(IntEnum):
    ENGLISH = RETRO_LANGUAGE_ENGLISH
    JAPANESE = RETRO_LANGUAGE_JAPANESE
    FRENCH = RETRO_LANGUAGE_FRENCH
    SPANISH = RETRO_LANGUAGE_SPANISH
    GERMAN = RETRO_LANGUAGE_GERMAN
    ITALIAN = RETRO_LANGUAGE_ITALIAN
    DUTCH = RETRO_LANGUAGE_DUTCH
    PORTUGUESE_BRAZIL = RETRO_LANGUAGE_PORTUGUESE_BRAZIL
    PORTUGUESE_PORTUGAL = RETRO_LANGUAGE_PORTUGUESE_PORTUGAL
    RUSSIAN = RETRO_LANGUAGE_RUSSIAN
    KOREAN = RETRO_LANGUAGE_KOREAN
    CHINESE_TRADITIONAL = RETRO_LANGUAGE_CHINESE_TRADITIONAL
    CHINESE_SIMPLIFIED = RETRO_LANGUAGE_CHINESE_SIMPLIFIED
    ESPERANTO = RETRO_LANGUAGE_ESPERANTO
    POLISH = RETRO_LANGUAGE_POLISH
    VIETNAMESE = RETRO_LANGUAGE_VIETNAMESE
    ARABIC = RETRO_LANGUAGE_ARABIC
    GREEK = RETRO_LANGUAGE_GREEK
    TURKISH = RETRO_LANGUAGE_TURKISH
    SLOVAK = RETRO_LANGUAGE_SLOVAK
    PERSIAN = RETRO_LANGUAGE_PERSIAN
    HEBREW = RETRO_LANGUAGE_HEBREW
    ASTURIAN = RETRO_LANGUAGE_ASTURIAN
    FINNISH = RETRO_LANGUAGE_FINNISH
    INDONESIAN = RETRO_LANGUAGE_INDONESIAN
    SWEDISH = RETRO_LANGUAGE_SWEDISH
    UKRAINIAN = RETRO_LANGUAGE_UKRAINIAN
    CZECH = RETRO_LANGUAGE_CZECH
    CATALAN_VALENCIA = RETRO_LANGUAGE_CATALAN_VALENCIA
    CATALAN = RETRO_LANGUAGE_CATALAN
    BRITISH_ENGLISH = RETRO_LANGUAGE_BRITISH_ENGLISH
    HUNGARIAN = RETRO_LANGUAGE_HUNGARIAN
    BELARUSIAN = RETRO_LANGUAGE_BELARUSIAN

    def __init__(self, value):
        self._type_ = 'I'


class retro_system_info(Structure, metaclass=FieldsFromTypeHints):
    library_name: String
    library_version: String
    valid_extensions: String
    need_fullpath: c_bool
    block_extract: c_bool


class retro_game_geometry(Structure, metaclass=FieldsFromTypeHints):
    base_width: c_uint
    base_height: c_uint
    max_width: c_uint
    max_height: c_uint
    aspect_ratio: c_float


class retro_system_timing(Structure, metaclass=FieldsFromTypeHints):
    fps: c_double
    sample_rate: c_double


class retro_system_av_info(Structure, metaclass=FieldsFromTypeHints):
    geometry: retro_game_geometry
    timing: retro_system_timing
