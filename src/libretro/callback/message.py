from abc import abstractmethod
from typing import Protocol, NamedTuple
from logging import Logger
import logging

from .._libretro import *
from ..defs import *


class MessageInterface(Protocol):
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def set_message(self, message: retro_message | retro_message_ext | None) -> bool: ...


class Message:
    def __init__(self, message: retro_message):
        self.msg = string_at(message.msg)
        self.frames = int(message.frames)


class MessageExt:
    def __init__(self, message: retro_message_ext):
        self.msg = string_at(message.msg)
        self.duration = int(message.duration)
        self.priority = int(message.priority)
        self.level = LogLevel(message.level)
        self.target = MessageTarget(message.target)
        self.type = MessageType(message.type)
        self.progress = int(message.progress)


class LoggingMessageInterface(MessageInterface):
    def __init__(self, version: int, logger: Logger | None):
        self._version = version
        self._logger = logger
        self._messages: list[Message] = []
        self._message_exts: list[MessageExt] = []

    def version(self) -> int:
        return self._version

    def messages(self) -> Sequence[Message]:
        return self._messages

    def message_exts(self) -> Sequence[MessageExt]:
        return self._message_exts

    def set_message(self, message: retro_message | retro_message_ext | None) -> bool:
        match message:
            case retro_message():
                m = Message(message)
                self._messages.append(m)
                if self._logger is not None:
                    self._logger.info(m.msg)
                return True
            case retro_message_ext() if self._version >= 1:
                m = MessageExt(message)
                self._message_exts.append(m)
                if self._logger is not None:
                    self._logger.log(m.level.to_logging_level(), m.msg)
                return True
            case _:
                return False
