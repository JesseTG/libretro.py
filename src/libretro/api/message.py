from ctypes import Structure, c_char_p, c_int, c_int8, c_uint
from dataclasses import dataclass
from enum import IntEnum

from libretro.api.log import LogLevel, retro_log_level

from ._utils import MemoDict

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


class MessageType(IntEnum):
    NOTIFICATION = RETRO_MESSAGE_TYPE_NOTIFICATION
    NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    STATUS = RETRO_MESSAGE_TYPE_STATUS
    PROGRESS = RETRO_MESSAGE_TYPE_PROGRESS


@dataclass(init=False, slots=True)
class retro_message(Structure):
    msg: bytes | None
    frames: int

    _fields_ = (
        ("msg", c_char_p),
        ("frames", c_uint),
    )

    def __deepcopy__(self, memodict: MemoDict = None):
        return retro_message(msg=self.msg, frames=self.frames)


@dataclass(init=False, slots=True)
class retro_message_ext(Structure):
    msg: bytes | None
    duration: int
    priority: int
    level: LogLevel
    target: MessageTarget
    type: MessageType
    progress: int

    _fields_ = (
        ("msg", c_char_p),
        ("duration", c_uint),
        ("priority", c_uint),
        ("level", retro_log_level),
        ("target", retro_message_target),
        ("type", retro_message_type),
        ("progress", c_int8),
    )

    def __deepcopy__(self, memodict: MemoDict = None):
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
