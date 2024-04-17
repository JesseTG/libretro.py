from copy import deepcopy
from logging import Logger
from typing import Sequence

from libretro.api import LogLevel, MessageTarget, retro_message, retro_message_ext

from .driver import MessageInterface


class LoggerMessageInterface(MessageInterface):
    def __init__(self, version: int = 1, logger: Logger | None = None):
        self._version = version
        self._logger = logger
        self._messages: list[retro_message] = []
        self._message_exts: list[retro_message_ext] = []

    @property
    def version(self) -> int:
        return self._version

    @property
    def messages(self) -> Sequence[retro_message]:
        return self._messages

    @property
    def message_exts(self) -> Sequence[retro_message_ext]:
        return self._message_exts

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
    "LoggerMessageInterface",
]
