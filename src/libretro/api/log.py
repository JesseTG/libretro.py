import logging
from ctypes import Structure, c_int
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from libretro.typing import CIntArg, CStringArg, TypedFunctionPointer

RETRO_LOG_DEBUG = 0
RETRO_LOG_INFO = RETRO_LOG_DEBUG + 1
RETRO_LOG_WARN = RETRO_LOG_INFO + 1
RETRO_LOG_ERROR = RETRO_LOG_WARN + 1
RETRO_LOG_DUMMY = 0x7FFFFFFF

retro_log_level = c_int


retro_log_printf_t = TypedFunctionPointer[None, [CIntArg[retro_log_level], CStringArg]]


class LogLevel(IntEnum):
    DEBUG = RETRO_LOG_DEBUG
    INFO = RETRO_LOG_INFO
    WARNING = RETRO_LOG_WARN
    ERROR = RETRO_LOG_ERROR

    def __init__(self, value: int):
        self._type_ = "I"
        self._as_parameter_ = value

    @property
    def logging_level(self) -> int:
        match self:
            case self.DEBUG:
                return logging.DEBUG
            case self.INFO:
                return logging.INFO
            case self.WARNING:
                return logging.WARN
            case self.ERROR:
                return logging.ERROR


@dataclass(init=False, slots=True)
class retro_log_callback(Structure):
    if TYPE_CHECKING:
        log: retro_log_printf_t | None

    _fields_ = [("log", retro_log_printf_t)]

    def __deepcopy__(self, _):
        return retro_log_callback(self.log)


__all__ = [
    "LogLevel",
    "retro_log_callback",
    "retro_log_printf_t",
    "retro_log_level",
]
