"""
Types that define serialization quirks and savestate contexts.
"""

from ctypes import c_int
from enum import IntEnum, IntFlag

RETRO_SERIALIZATION_QUIRK_INCOMPLETE = 1 << 0
RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE = 1 << 1
RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE = 1 << 2
RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE = 1 << 3
RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION = 1 << 4
RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT = 1 << 5
RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT = 1 << 6

retro_savestate_context = c_int
"""Corresponds to :c:type:`retro_savestate_context` in ``libretro.h``."""

RETRO_SAVESTATE_CONTEXT_NORMAL = 0
RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE = 1
RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY = 2
RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY = 3
RETRO_SAVESTATE_CONTEXT_UNKNOWN = 0x7FFFFFFF


class SerializationQuirks(IntFlag):
    """
    Flags describing quirks of a core's serialization (savestate) support.

    Corresponds to the ``RETRO_SERIALIZATION_QUIRK_*`` constants in ``libretro.h``.
    """

    INCOMPLETE = RETRO_SERIALIZATION_QUIRK_INCOMPLETE
    """
    Set by the :class:`.Core` to indicate that serialized state is incomplete in some way.

    The :class:`.Core` should set this bit if serialization is usable
    for the common case of saving and loading game state,
    but not for frame-sensitive frontend features
    such as netplay or rerecording.
    """

    MUST_INITIALIZE = RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE
    """
    Set by the :class:`.Core` to indicate that it must perform some initialization
    before :meth:`.Core.serialize` returns non-:obj:`None`.
    """

    CORE_VARIABLE_SIZE = RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE
    """
    Set by the :class:`.Core` to indicate that the return value of :meth:`.Core.serialize_size`
    may change within a single session.
    """

    FRONTEND_VARIABLE_SIZE = RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE
    """
    Set by libretro.py to indicate that it supports cores that set :attr:`.CORE_VARIABLE_SIZE`.
    """

    SINGLE_SESSION = RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION
    """
    Set by the :class:`.Core` to indicate that savestates are only valid within a single session.
    """

    ENDIAN_DEPENDENT = RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT
    """
    Set by the :class:`.Core` to indicate that savestates
    can't be loaded on a platform with a different endianness than the one they were created on.
    """

    PLATFORM_DEPENDENT = RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT
    """
    Set by the :class:`.Core` to indicate that its savestates
    can't be loaded on a different platform than the one they were created on
    for reasons besides endianness, such as pointer size or structure packing differences.
    """

    ALL = (
        INCOMPLETE
        | MUST_INITIALIZE
        | CORE_VARIABLE_SIZE
        | FRONTEND_VARIABLE_SIZE
        | SINGLE_SESSION
        | ENDIAN_DEPENDENT
        | PLATFORM_DEPENDENT
    )


class SavestateContext(IntEnum):
    """
    Denotes what a savestate returned by a :class:`.Core` will be used for.

    Corresponds to the ``RETRO_SAVESTATE_CONTEXT_*`` constants in ``libretro.h``.
    """

    NORMAL = RETRO_SAVESTATE_CONTEXT_NORMAL
    """
    Standard savestate written to disk.
    """

    RUNAHEAD_SAME_INSTANCE = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE
    """
    Denotes a savestate that is suitable for same-instance runahead.
    This means that you should only use the savestate within a single session
    and not send it to disk or across the network.
    """

    RUNAHEAD_SAME_BINARY = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY
    """
    Denotes a savestate that is suitable for second-instance runahead.
    This means that it shouldn't contain pointers.
    """

    ROLLBACK_NETPLAY = RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY
    """
    Denotes a savestate that is suitable for rollback netplay.
    Must not contain pointers, and integers must be in big-endian format.
    """


__all__ = [
    "SerializationQuirks",
    "SavestateContext",
    "retro_savestate_context",
]
