"""
Types for allowing :class:`.Core`\\s to control LED indicators on the host device.

.. seealso::

    :class:`.LedDriver`
        The protocol that uses these types to implement LED control support in libretro.py.

    :mod:`libretro.drivers.led`
        libretro.py's included :class:`.LedDriver` implementations.
"""

from ctypes import Structure, c_int
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer

retro_set_led_state_t = TypedFunctionPointer[None, [CIntArg[c_int], CIntArg[c_int]]]
"""
Called by the :class:`.Core` to set the state of an LED.

.. seealso::
    :attr:`.LedDriver.set_led_state`
        The suggested entry point for this callback.
"""


@dataclass(init=False, slots=True)
class retro_led_interface(Structure):
    """
    Defines a callback that :class:`.Core`\\s can use
    to control LED indicators on the host device.

    Corresponds to :c:type:`retro_led_interface` in ``libretro.h``.
    """

    set_led_state: retro_set_led_state_t | None
    """
    Called by the :class:`.Core` to set the state of an LED.
    """

    _fields_ = (("set_led_state", retro_set_led_state_t),)

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_led_interface
        >>> copy.deepcopy(retro_led_interface()).set_led_state is None
        True
        """
        return retro_led_interface(self.set_led_state)


__all__ = ["retro_led_interface", "retro_set_led_state_t"]
