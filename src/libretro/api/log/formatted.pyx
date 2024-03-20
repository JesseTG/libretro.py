import cython
import logging
from collections.abc import Sequence
from logging import Logger, LogRecord


from .interface import LogCallback
from .defs import *

cdef extern from "stdarg.h":
    ctypedef struct va_list:
        pass
    ctypedef struct fake_type:
        pass
    void va_start(va_list, void* arg)
    void* va_arg(va_list, fake_type)
    void va_end(va_list)
    fake_type int_type "int"


cdef int foo(int n, ...):
    print "starting"
    cdef va_list args
    va_start(args, <void*>n)
    while n != 0:
        print n
        n = <int>va_arg(args, int_type)
    va_end(args)
    print "done"
class FormattedLogger(LogCallback):
    def __init__(self, logger: Logger | None = None):
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
