import logging
from collections.abc import Sequence
from logging import Logger, LogRecord


from .interface import LogCallback
from .defs import *


class UnformattedLogger(LogCallback):
    def __init__(self, logger: Logger | None = None):
        super().__init__()
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

    @property
    def records(self) -> Sequence[LogRecord]:
        return self._records

    def log(self, level: int, fmt: bytes, *args) -> None:
        lvl = LogLevel(level)
        self._logger.log(lvl.logging_level, fmt)
