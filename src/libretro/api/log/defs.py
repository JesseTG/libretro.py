
import logging

from ctypes import CFUNCTYPE, Structure, c_char_p
from enum import IntEnum

from ...h import *
from ..._utils import FieldsFromTypeHints

retro_log_printf_t = CFUNCTYPE(None, retro_log_level, c_char_p)


class LogLevel(IntEnum):
    DEBUG = RETRO_LOG_DEBUG
    INFO = RETRO_LOG_INFO
    WARNING = RETRO_LOG_WARN
    ERROR = RETRO_LOG_ERROR

    def __init__(self, value: int):
        self._type_ = 'I'
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


class retro_log_callback(Structure, metaclass=FieldsFromTypeHints):
    log: retro_log_printf_t


__all__ = ['LogLevel', 'retro_log_callback', 'retro_log_printf_t']
