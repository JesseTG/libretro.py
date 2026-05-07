"""
A LED driver that stores LED state in a dictionary.

.. seealso::

    :mod:`libretro.api.led`
        Defines the LED interface structure this driver implements.
"""

from typing import override

from .driver import LedDriver


class DictLedDriver(LedDriver):
    """A :class:`.LedDriver` that stores LED states in an in-memory :class:`dict`."""

    def __init__(self):
        """Initialize the driver with an empty LED-state dictionary."""
        self._leds: dict[int, int] = {}

    @override
    def set_led_state(self, led: int, state: int) -> None:
        """
        :param led: Zero-based LED index.
        :param state: Non-zero to turn the LED on, zero to turn it off.
        """
        self._leds[led] = state

    @override
    def get_led_state(self, led: int) -> int:
        """
        :param led: Zero-based LED index.
        :return: The stored LED state, or ``0`` if the LED has never been set.
        """
        return self._leds.get(led, 0)


__all__ = ["DictLedDriver"]
