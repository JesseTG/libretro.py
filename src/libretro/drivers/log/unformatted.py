import logging
from collections.abc import Sequence
from logging import Logger, LogRecord

from libretro.api.log import LogLevel

from .driver import LogDriver


class UnformattedLogDriver(LogDriver):
    def __init__(self, logger: Logger | None = None):
        super().__init__()
        self._logger = logger
        self._records: list[LogRecord] = []

        def _log_record(record: LogRecord):
            self._records.append(record)
            return True

        if self._logger is None:
            self._logger = logging.getLogger("libretro")
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.addFilter(_log_record)

    @property
    def records(self) -> Sequence[LogRecord]:
        return self._records

    def log(self, level: LogLevel, fmt: bytes, *args) -> None:
        self._logger.log(level.logging_level, fmt.decode(errors="replace").rstrip())


__all__ = ["UnformattedLogDriver"]
