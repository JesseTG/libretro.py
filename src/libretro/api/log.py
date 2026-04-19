"""
Types for allowing :class:`.Core`\\s to log messages.

.. seealso::
    :class:`.LogDriver`
        The protocol that uses these types to implement logging support in libretro.py.

    :mod:`libretro.drivers.log`
        libretro.py's included :class:`.LogDriver` implementations.
"""

import logging
from ctypes import Structure, c_int
from dataclasses import dataclass
from enum import IntEnum

from libretro.ctypes import CIntArg, CStringArg, TypedFunctionPointer

RETRO_LOG_DEBUG = 0
RETRO_LOG_INFO = RETRO_LOG_DEBUG + 1
RETRO_LOG_WARN = RETRO_LOG_INFO + 1
RETRO_LOG_ERROR = RETRO_LOG_WARN + 1
RETRO_LOG_DUMMY = 0x7FFFFFFF

retro_log_level = c_int


retro_log_printf_t = TypedFunctionPointer[None, [CIntArg[retro_log_level], CStringArg]]
"""
A :c:func:`printf`-style logging function.

.. warning::
    :c:type:`retro_log_printf_t` normally has :c:func:`printf`-style variadic arguments,
    but :mod:`!ctypes` :python-issue:`doesn't currently support variadic callbacks <135620>`.

    As a workaround, your :class:`.Core` can format log messages with :c:func:`sprintf` or similar,
    then pass it as the format string.
"""


class LogLevel(IntEnum):
    """
    libretro's defined log severity levels.

    Corresponds to :c:type:`retro_log_level` in ``libretro.h``.
    """

    DEBUG = RETRO_LOG_DEBUG
    INFO = RETRO_LOG_INFO
    WARNING = RETRO_LOG_WARN
    ERROR = RETRO_LOG_ERROR

    def __init__(self, value: int):
        self._type_ = "I"
        self._as_parameter_ = value

    @property
    def logging_level(self) -> int:
        """Returns the equivalent :mod:`logging` level.

        >>> import logging
        >>> from libretro.api import LogLevel
        >>> LogLevel.WARNING.logging_level == logging.WARN
        True
        """
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
    """
    Provides the :class:`.Core` with a logging function.

    Corresponds to :c:type:`retro_log_callback` in ``libretro.h``.
    """

    log: retro_log_printf_t | None
    """A printf-style logging function. Set by the frontend."""

    _fields_ = (("log", retro_log_printf_t),)

    def __deepcopy__(self, _):
        """
        Returns a shallow copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_log_callback(self.log)


__all__ = [
    "LogLevel",
    "retro_log_callback",
    "retro_log_printf_t",
    "retro_log_level",
]
