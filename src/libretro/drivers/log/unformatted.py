import logging
from collections.abc import Sequence
from logging import Logger, LogRecord
from typing import override

from libretro.api.log import LogLevel

from .driver import LogDriver


class UnformattedLogDriver(LogDriver):
    _logger: Logger

    def __init__(self, logger: Logger | None = None):
        self._records: list[LogRecord] = []
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger("libretro")
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.addFilter(self._log_record)

    def _log_record(self, record: LogRecord):
        self._records.append(record)
        return True

    @property
    def records(self) -> Sequence[LogRecord]:
        return self._records

    @override
    def log(self, level: LogLevel, fmt: bytes) -> None:
        self._logger.log(level.logging_level, fmt.decode(errors="replace").rstrip())


__all__ = ["UnformattedLogDriver"]
