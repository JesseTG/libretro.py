import logging

from abc import abstractmethod
from collections.abc import Sequence
from ctypes import CFUNCTYPE, Structure
from enum import IntEnum
from typing import Protocol
from logging import Logger, LogRecord

from ..h import *
from .._utils import FieldsFromTypeHints, String

retro_log_printf_t = CFUNCTYPE(None, retro_log_level, String)


class LogLevel(IntEnum):
    DEBUG = RETRO_LOG_DEBUG
    INFO = RETRO_LOG_INFO
    WARNING = RETRO_LOG_WARN
    ERROR = RETRO_LOG_ERROR

    def __init__(self, value: int):
        self._type_ = 'I'

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


class LogCallback(Protocol):
    @abstractmethod
    def log(self, message: LogLevel, fmt: bytes, *args) -> None: ...


class StandardLogger(LogCallback):
    def __init__(self, logger: Logger | None):
        self._logger = logger
        self._records: list[LogRecord] = []
        def _log_record(record: LogRecord):
            self._records.append(record)
            return True

        if self._logger is None:
            self._logger = logging.getLogger('libretro')
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.addFilter(_log_record)

        self._as_parameter_ = retro_log_callback(retro_log_printf_t(self.log))

    @property
    def records(self) -> Sequence[LogRecord]:
        return self._records

    def log(self, level: LogLevel, fmt: bytes, *args) -> None:
        self._logger.log(level.logging_level, fmt, args)
