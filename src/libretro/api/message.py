"""
Types that allow :class:`.Core`\\s to display notifications on the frontend's OSD.

.. seealso::
    :class:`.MessageDriver`
        The :class:`.Protocol` that uses these types to implement notification support in libretro.py.

    :mod:`libretro.drivers.message`
        libretro.py's included :class:`.MessageDriver` implementations.
"""

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
"""Corresponds to :c:type:`retro_message_target` in ``libretro.h``."""

retro_message_type = c_int
"""Corresponds to :c:type:`retro_message_type` in ``libretro.h``."""


class MessageTarget(IntEnum):
    """
    Where a message should be displayed.

    :class:`.MessageDriver`\\s can interpret these however they want.

    >>> from libretro.api import MessageTarget
    >>> MessageTarget.OSD
    <MessageTarget.OSD: 1>
    """

    ALL = RETRO_MESSAGE_TARGET_ALL
    OSD = RETRO_MESSAGE_TARGET_OSD
    LOG = RETRO_MESSAGE_TARGET_LOG


class MessageType(IntEnum):
    """
    The presentation style of a message.

    :class:`.MessageDriver`\\s can interpret these however they want.
    """

    NOTIFICATION = RETRO_MESSAGE_TYPE_NOTIFICATION
    NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    STATUS = RETRO_MESSAGE_TYPE_STATUS
    PROGRESS = RETRO_MESSAGE_TYPE_PROGRESS


@dataclass(init=False, slots=True)
class retro_message(Structure):
    """
    A short-lived on-screen notification.

    Corresponds to :c:type:`retro_message` in ``libretro.h``.
    """

    msg: bytes | None
    """Null-terminated message text to display."""

    frames: int
    """Duration in frames to show the message."""

    _fields_ = (
        ("msg", c_char_p),
        ("frames", c_uint),
    )

    def __deepcopy__(self, memodict: MemoDict = None):
        """
        Returns a copy of this object,
        including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_message(msg=self.msg, frames=self.frames)


@dataclass(init=False, slots=True)
class retro_message_ext(Structure):
    """
    An extended version of :class:`retro_message` with more display options.

    Corresponds to :c:type:`retro_message_ext` in ``libretro.h``.
    """

    msg: bytes | None
    """Null-terminated message text to display."""
    duration: int
    """Duration in milliseconds to show the message."""
    priority: int
    """Priority of the message. Higher values take precedence."""
    level: LogLevel
    """Log severity level of the message."""
    target: MessageTarget
    """Where the message should be displayed."""
    type: MessageType
    """Presentation style of the message."""
    progress: int
    """
    A value from -1 to 100 representing task progress. -1 for indefinite.

    Assigned values are bitwise-masked to fit into a :c:type:`uint8_t`.
    """

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
        """
        Returns a copy of this object,
        including all strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_message_ext
        >>> copy.deepcopy(retro_message_ext()).duration
        0
        """
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
