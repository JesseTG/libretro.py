"""
A power driver that always returns a fixed power state.

.. seealso::

    :mod:`libretro.api.power`
        Defines the device power structure this driver always returns.
"""

from typing import override

from libretro.api.power import NO_ESTIMATE, PowerState, retro_device_power

from .driver import PowerDriver


class ConstantPowerDriver(PowerDriver):
    """A :class:`.PowerDriver` that always reports a fixed :class:`~libretro.api.power.retro_device_power`."""

    def __init__(self, device_power: retro_device_power | None = None):
        """
        :param device_power: The power state to always report to the core.
        :raises TypeError: If ``device_power`` is not a :class:`~libretro.api.power.retro_device_power`.
        """
        if not device_power:
            device_power = retro_device_power(
                state=PowerState.PLUGGED_IN, seconds=NO_ESTIMATE, percent=NO_ESTIMATE
            )

        self._device_power = device_power

    @property
    @override
    def device_power(self) -> retro_device_power:
        return self._device_power

    @device_power.setter
    def device_power(self, device_power: retro_device_power) -> None:
        if not isinstance(device_power, retro_device_power):
            raise TypeError(f"Expected a retro_device_power, got: {type(device_power).__name__}")
        self._device_power = device_power


__all__ = ("ConstantPowerDriver",)
