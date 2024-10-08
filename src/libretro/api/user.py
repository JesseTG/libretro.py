from ctypes import c_int
from enum import IntEnum

retro_language = c_int
RETRO_LANGUAGE_ENGLISH = 0
RETRO_LANGUAGE_JAPANESE = 1
RETRO_LANGUAGE_FRENCH = 2
RETRO_LANGUAGE_SPANISH = 3
RETRO_LANGUAGE_GERMAN = 4
RETRO_LANGUAGE_ITALIAN = 5
RETRO_LANGUAGE_DUTCH = 6
RETRO_LANGUAGE_PORTUGUESE_BRAZIL = 7
RETRO_LANGUAGE_PORTUGUESE_PORTUGAL = 8
RETRO_LANGUAGE_RUSSIAN = 9
RETRO_LANGUAGE_KOREAN = 10
RETRO_LANGUAGE_CHINESE_TRADITIONAL = 11
RETRO_LANGUAGE_CHINESE_SIMPLIFIED = 12
RETRO_LANGUAGE_ESPERANTO = 13
RETRO_LANGUAGE_POLISH = 14
RETRO_LANGUAGE_VIETNAMESE = 15
RETRO_LANGUAGE_ARABIC = 16
RETRO_LANGUAGE_GREEK = 17
RETRO_LANGUAGE_TURKISH = 18
RETRO_LANGUAGE_SLOVAK = 19
RETRO_LANGUAGE_PERSIAN = 20
RETRO_LANGUAGE_HEBREW = 21
RETRO_LANGUAGE_ASTURIAN = 22
RETRO_LANGUAGE_FINNISH = 23
RETRO_LANGUAGE_INDONESIAN = 24
RETRO_LANGUAGE_SWEDISH = 25
RETRO_LANGUAGE_UKRAINIAN = 26
RETRO_LANGUAGE_CZECH = 27
RETRO_LANGUAGE_CATALAN_VALENCIA = 28
RETRO_LANGUAGE_CATALAN = 29
RETRO_LANGUAGE_BRITISH_ENGLISH = 30
RETRO_LANGUAGE_HUNGARIAN = 31
RETRO_LANGUAGE_BELARUSIAN = 32
RETRO_LANGUAGE_GALICIAN = 33
RETRO_LANGUAGE_NORWEGIAN = 34
RETRO_LANGUAGE_LAST = RETRO_LANGUAGE_NORWEGIAN + 1
RETRO_LANGUAGE_DUMMY = 0x7FFFFFFF


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
    GALICIAN = RETRO_LANGUAGE_GALICIAN
    NORWEGIAN = RETRO_LANGUAGE_NORWEGIAN

    def __init__(self, value):
        self._type_ = "I"


__all__ = [
    "Language",
    "retro_language",
]
