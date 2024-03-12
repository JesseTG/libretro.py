from abc import abstractmethod
from ctypes import Structure, c_char_p, c_uint, c_int8, string_at
from enum import IntEnum
from typing import Protocol, Sequence
from logging import Logger

from ..h import *
from ..retro import FieldsFromTypeHints
from .log import LogLevel


class MessageTarget(IntEnum):
    ALL = RETRO_MESSAGE_TARGET_ALL
    OSD = RETRO_MESSAGE_TARGET_OSD
    LOG = RETRO_MESSAGE_TARGET_LOG

    def __init__(self, value: int):
        self._type_ = 'I'


class MessageType(IntEnum):
    NOTIFICATION = RETRO_MESSAGE_TYPE_NOTIFICATION
    NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    STATUS = RETRO_MESSAGE_TYPE_STATUS
    PROGRESS = RETRO_MESSAGE_TYPE_PROGRESS

    def __init__(self, value: int):
        self._type_ = 'I'


class retro_message(Structure, metaclass=FieldsFromTypeHints):
    msg: c_char_p
    frames: c_uint


class retro_message_ext(Structure, metaclass=FieldsFromTypeHints):
    msg: c_char_p
    duration: c_uint
    priority: c_uint
    level: retro_log_level
    target: retro_message_target
    type: retro_message_type
    progress: c_int8


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


class LoggerMessageInterface(MessageInterface):
    def __init__(self, version: int, logger: Logger | None):
        self._version = version
        self._logger = logger
        self._messages: list[Message] = []
        self._message_exts: list[MessageExt] = []

    def version(self) -> int:
        return self._version

    @property
    def messages(self) -> Sequence[Message]:
        return self._messages

    @property
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
                if self._logger is not None and m.target in (MessageTarget.Log, MessageTarget.All):
                    self._logger.log(m.level.to_logging_level(), m.msg)
                return True
            case _:
                return False
