"""
Protocol definition for the power driver interface.

.. seealso::

    :mod:`libretro.api.power`
        Provides the device power structure that :class:`.PowerDriver` implementations report.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.power import retro_device_power


@runtime_checkable
class PowerDriver(Protocol):
    """
    Protocol for drivers that report the device's power state to the core.

    Cores query power state via ``RETRO_ENVIRONMENT_GET_DEVICE_POWER``.

    .. seealso::

        :class:`~libretro.api.power.retro_device_power`
            The C struct whose value this driver returns.
    """

    @property
    @abstractmethod
    def device_power(self) -> retro_device_power:
        """
        The current device power state reported to the core.
        """
        ...


__all__ = [
    "PowerDriver",
]
