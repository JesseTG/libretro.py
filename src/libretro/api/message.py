from ctypes import Structure, c_char_p, c_int, c_int8, c_uint
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints
from libretro.api.log import retro_log_level

RETRO_MESSAGE_TARGET_ALL = 0
RETRO_MESSAGE_TARGET_OSD = RETRO_MESSAGE_TARGET_ALL + 1
RETRO_MESSAGE_TARGET_LOG = RETRO_MESSAGE_TARGET_OSD + 1
RETRO_MESSAGE_TYPE_NOTIFICATION = 0
RETRO_MESSAGE_TYPE_NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION + 1
RETRO_MESSAGE_TYPE_STATUS = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT + 1
RETRO_MESSAGE_TYPE_PROGRESS = RETRO_MESSAGE_TYPE_STATUS + 1

retro_message_target = c_int
retro_message_type = c_int


class MessageTarget(IntEnum):
    ALL = RETRO_MESSAGE_TARGET_ALL
    OSD = RETRO_MESSAGE_TARGET_OSD
    LOG = RETRO_MESSAGE_TARGET_LOG

    def __init__(self, value: int):
        self._type_ = "I"


class MessageType(IntEnum):
    NOTIFICATION = RETRO_MESSAGE_TYPE_NOTIFICATION
    NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    STATUS = RETRO_MESSAGE_TYPE_STATUS
    PROGRESS = RETRO_MESSAGE_TYPE_PROGRESS

    def __init__(self, value: int):
        self._type_ = "I"


@dataclass(init=False)
class retro_message(Structure, metaclass=FieldsFromTypeHints):
    msg: c_char_p
    frames: c_uint

    def __deepcopy__(self, memodict):
        return retro_message(msg=self.msg, frames=self.frames)


@dataclass(init=False)
class retro_message_ext(Structure, metaclass=FieldsFromTypeHints):
    msg: c_char_p
    duration: c_uint
    priority: c_uint
    level: retro_log_level
    target: retro_message_target
    type: retro_message_type
    progress: c_int8

    def __deepcopy__(self, _):
        return retro_message_ext(
            msg=self.msg,
            duration=self.duration,
            priority=self.priority,
            level=self.level,
            target=self.target,
            type=self.type,
            progress=self.progress,
        )


__all__ = ["MessageTarget", "MessageType", "retro_message", "retro_message_ext"]
