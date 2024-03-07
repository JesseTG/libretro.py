from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
import logging
from logging import Logger, LogRecord

from ..defs import LogLevel
from ..retro import retro_log_callback, retro_log_printf_t


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
        loglevel = {
            LogLevel.Debug: logging.DEBUG,
            LogLevel.Info: logging.INFO,
            LogLevel.Warning: logging.WARN,
            LogLevel.Error: logging.ERROR,
        }[level]

        self._logger.log(loglevel, fmt, args)

