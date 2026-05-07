"""
Protocol definition for the log driver interface.

.. seealso::

    :mod:`libretro.api.log`
        Provides the C callback structure that :class:`.LogDriver` implementations use.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.log import LogLevel


@runtime_checkable
class LogDriver(Protocol):
    """
    Protocol for drivers that receive log output from the core.

    Cores request logging via ``RETRO_ENVIRONMENT_GET_LOG_INTERFACE``.

    .. seealso::

        :class:`~libretro.api.log.retro_log_callback`
            The C callback struct whose ``log`` function pointer this protocol implements.
    """

    @abstractmethod
    def log(self, level: LogLevel, fmt: bytes) -> None:
        """
        Emit a log message from the core.

        Corresponds to :c:type:`retro_log_printf_t`.

        .. warning::
            :c:type:`retro_log_printf_t` normally has :c:func:`printf`-style variadic arguments,
            but :mod:`!ctypes` :python-issue:`doesn't currently support variadic callbacks <135620>`.

            As a workaround, your :class:`.Core` can format log messages with :c:func:`sprintf` or similar,
            then pass it as the format string.

        :param level: The severity of the message.
        :param fmt: The message as a null-terminated byte string.

        .. seealso::

            :attr:`.retro_log_callback.log`
                The function pointer field in the callback struct that this method implements.
        """
        ...


__all__ = ["LogDriver"]
