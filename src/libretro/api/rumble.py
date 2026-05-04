"""
Rumble (force feedback) interface types.

Corresponds to :c:type:`retro_rumble_interface` in ``libretro.h``.

.. seealso::

    :class:`.RumbleDriver`
        The :class:`~typing.Protocol` that uses these types to implement rumble support in libretro.py.

    :mod:`libretro.drivers.rumble`
        libretro.py's included :class:`.RumbleDriver` implementations.
"""

from ctypes import Structure, c_bool, c_int, c_uint, c_uint16
from dataclasses import dataclass
from enum import IntEnum

from libretro.ctypes import CIntArg, TypedFunctionPointer

retro_rumble_effect = c_int
"""Corresponds to :c:type:`retro_rumble_effect` in ``libretro.h``."""

RETRO_RUMBLE_STRONG = 0
RETRO_RUMBLE_WEAK = 1
RETRO_RUMBLE_DUMMY = 0x7FFFFFFF


retro_set_rumble_state_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CIntArg[retro_rumble_effect], CIntArg[c_uint16]]
]
"""
Sets the rumble state for the controller assigned to a given input port.

.. seealso::

    :attr:`.RumbleDriver.set_rumble_state`
        The suggested entry point for implementing rumble support in a core.
"""


class RumbleEffect(IntEnum):
    """
    Enumeration of rumble motor types.

    >>> from libretro.api import RumbleEffect
    >>> RumbleEffect.STRONG
    <RumbleEffect.STRONG: 0>
    """

    STRONG = RETRO_RUMBLE_STRONG
    WEAK = RETRO_RUMBLE_WEAK


@dataclass(init=False, slots=True)
class retro_rumble_interface(Structure):
    """
    Interface for a :class:`.Core` to provide rumble (force feedback) support.

    Corresponds to :c:type:`retro_rumble_interface` in ``libretro.h``.
    """

    set_rumble_state: retro_set_rumble_state_t | None
    """
    Sets the rumble intensity for the controller assigned to a given input port.
    """

    _fields_ = (("set_rumble_state", retro_set_rumble_state_t),)

    def __deepcopy__(self, _):
        """
        Returns copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_rumble_interface(self.set_rumble_state)


__all__ = [
    "retro_set_rumble_state_t",
    "RumbleEffect",
    "retro_rumble_interface",
    "retro_rumble_effect",
]
