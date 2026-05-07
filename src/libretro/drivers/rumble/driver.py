"""
:class:`~typing.Protocol` definition for controller rumble feedback drivers.

.. seealso::

    :mod:`libretro.api.rumble`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.input import Port
from libretro.api.rumble import RumbleEffect


@runtime_checkable
class RumbleDriver(Protocol):
    """
    Protocol for drivers that drive controller rumble motors.

    .. seealso::

        :mod:`libretro.api.rumble`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @abstractmethod
    def set_rumble_state(self, port: Port, effect: RumbleEffect, strength: int) -> bool:
        """Set the rumble state of a controller port."""
        ...


__all__ = [
    "RumbleDriver",
]
