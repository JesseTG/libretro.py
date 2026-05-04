"""
A message driver that stores core messages and optionally logs them.

.. seealso::

    :mod:`libretro.api.message`
        Defines the message types this driver records.
"""

from collections.abc import Sequence
from copy import deepcopy
from logging import Logger
from typing import override

from libretro.api import LogLevel, MessageTarget, retro_message, retro_message_ext

from .driver import MessageDriver


class LoggerMessageDriver(MessageDriver):
    """
    A :class:`.MessageDriver` that stores all messages in memory
    and optionally forwards them to a standard Python :class:`~logging.Logger`.
    """

    def __init__(self, version: int = 1, logger: Logger | None = None):
        """
        :param version: The message interface version to advertise (``0`` or ``1``).
        :param logger: An optional :class:`~logging.Logger` to write messages to.
        """
        self._version = version
        self._logger = logger
        self._messages: list[retro_message] = []
        self._message_exts: list[retro_message_ext] = []

    @property
    @override
    def version(self) -> int:
        return self._version

    @property
    def messages(self) -> Sequence[retro_message]:
        """
        All basic messages received from the core, in order.
        """
        return self._messages

    @property
    def message_exts(self) -> Sequence[retro_message_ext]:
        """
        All extended messages received from the core, in order.
        """
        return self._message_exts

    @override
    def set_message(self, message: retro_message | retro_message_ext | None) -> bool:
        match message:
            case retro_message():
                self._messages.append(deepcopy(message))
                if self._logger is not None:
                    self._logger.info(message.msg)
                return True
            case retro_message_ext() if self._version >= 1:
                self._message_exts.append(deepcopy(message))
                if self._logger is not None and message.target in (
                    MessageTarget.LOG,
                    MessageTarget.ALL,
                ):
                    self._logger.log(LogLevel(message.level).logging_level, message.msg)
                return True
            case _:
                return False


__all__ = [
    "LoggerMessageDriver",
]
