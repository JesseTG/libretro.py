"""
A log driver that forwards core messages to Python's :mod:`logging` module.

.. seealso::

    :mod:`libretro.api.log`
        Defines the log callback structure this driver implements.
"""

import logging
from collections.abc import Sequence
from logging import Logger, LogRecord
from typing import override

from libretro.api.log import LogLevel

from .driver import LogDriver


class UnformattedLogDriver(LogDriver):
    """
    A :class:`.LogDriver` that forwards core log messages
    to a Python :class:`~logging.Logger`.

    All received messages are also stored in :attr:`records`
    for later inspection.
    """

    _logger: Logger

    def __init__(self, logger: Logger | None = None):
        """
        :param logger: An existing :class:`~logging.Logger` to forward messages to.
            If :obj:`None`, a default logger named ``"libretro"`` is created
            that writes to :data:`sys.stderr` at :data:`~logging.DEBUG` level.
        """
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
        """
        All log records received from the core, in the order they were emitted.
        """
        return self._records

    @override
    def log(self, level: LogLevel, fmt: bytes) -> None:
        self._logger.log(level.logging_level, fmt.decode(errors="replace").rstrip())


__all__ = ["UnformattedLogDriver"]
