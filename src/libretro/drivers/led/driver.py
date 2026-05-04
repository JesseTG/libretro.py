"""
Protocol definition for the LED driver interface.

.. seealso::

    :mod:`libretro.api.led`
        Provides the LED interface structure that :class:`.LedDriver` implementations use.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class LedDriver(Protocol):
    """
    Protocol for drivers that track the state of virtual LEDs exposed to the core.

    Cores control LED state via ``RETRO_ENVIRONMENT_GET_LED_INTERFACE``.

    .. seealso::

        :class:`~libretro.api.led.retro_led_interface`
            The C interface struct that this protocol abstracts over.
    """

    @abstractmethod
    def set_led_state(self, led: int, state: int) -> None:
        """
        Sets the state of a virtual LED.

        Corresponds to :c:type:`retro_set_led_state_t`.

        :param led: Zero-based LED index.
        :param state: Non-zero to turn the LED on, zero to turn it off.
        """
        ...

    def __setitem__(self, key: int, value: int):
        """
        Sets the state of a virtual LED.
        Equivalent to :meth:`set_led_state`.

        :param key: Zero-based LED index.
        :param value: Non-zero to turn the LED on, zero to turn it off.
        """
        self.set_led_state(int(key), int(value))

    @abstractmethod
    def get_led_state(self, led: int) -> int:
        """
        Returns the current state of a virtual LED.

        :param led: Zero-based LED index.
        :return: The LED state (non-zero means on).
        """
        ...

    def __getitem__(self, key: int) -> int:
        """
        Returns the current state of a virtual LED.
        Equivalent to :meth:`get_led_state`.

        :param key: Zero-based LED index.
        :return: The LED state (non-zero means on).
        """
        return self.get_led_state(int(key))


__all__ = ["LedDriver"]
