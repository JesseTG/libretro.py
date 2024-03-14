from abc import abstractmethod
from copy import deepcopy
from ctypes import Structure, c_char_p, c_uint, c_int8, string_at
from enum import IntEnum
from typing import Protocol, Sequence, runtime_checkable
from logging import Logger

from ..h import *
from .._utils import FieldsFromTypeHints
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

    def __deepcopy__(self, memodict):
        return retro_message(
            msg=bytes(self.msg),
            frames=int(self.frames)
        )


class retro_message_ext(Structure, metaclass=FieldsFromTypeHints):
    msg: c_char_p
    duration: c_uint
    priority: c_uint
    level: retro_log_level
    target: retro_message_target
    type: retro_message_type
    progress: c_int8

    def __deepcopy__(self, memodict):
        return retro_message_ext(
            msg=bytes(self.msg),
            duration=int(self.duration),
            priority=int(self.priority),
            level=LogLevel(int(self.level)),
            target=MessageTarget(int(self.target)),
            type=MessageType(int(self.type)),
            progress=int(self.progress)
        )


@runtime_checkable
class MessageInterface(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def set_message(self, message: retro_message | retro_message_ext | None) -> bool: ...


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
                if self._logger is not None and message.target in (MessageTarget.LOG, MessageTarget.ALL):
                    self._logger.log(LogLevel(message.level).logging_level, message.msg)
                return True
            case _:
                return False
