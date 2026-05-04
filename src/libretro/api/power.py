"""
Types for exposing a frontend's power status to a :class:`.Core`.

.. seealso::

    :class:`.PowerDriver`
        The :class:`~typing.Protocol` that uses these types to expose power status to a :class:`.Core`.

    :mod:`libretro.drivers.power`
        libretro.py's included :class:`.PowerDriver` implementations.
"""

from ctypes import Structure, c_int, c_int8
from dataclasses import dataclass
from enum import IntEnum

retro_power_state = c_int
"""Corresponds to :c:type:`retro_power_state` in ``libretro.h``."""

RETRO_POWERSTATE_UNKNOWN = 0
RETRO_POWERSTATE_DISCHARGING = RETRO_POWERSTATE_UNKNOWN + 1
RETRO_POWERSTATE_CHARGING = RETRO_POWERSTATE_DISCHARGING + 1
RETRO_POWERSTATE_CHARGED = RETRO_POWERSTATE_CHARGING + 1
RETRO_POWERSTATE_PLUGGED_IN = RETRO_POWERSTATE_CHARGED + 1
RETRO_POWERSTATE_NO_ESTIMATE = -1

NO_ESTIMATE = RETRO_POWERSTATE_NO_ESTIMATE
"""Sentinel value indicating that the remaining time or charge is unknown."""


class PowerState(IntEnum):
    """
    Enumeration of device power states.

    Corresponds to the ``RETRO_POWERSTATE_*`` constants in ``libretro.h``.

    >>> from libretro.api import PowerState
    >>> PowerState.CHARGING
    <PowerState.CHARGING: 2>
    """

    UNKNOWN = RETRO_POWERSTATE_UNKNOWN
    DISCHARGING = RETRO_POWERSTATE_DISCHARGING
    CHARGING = RETRO_POWERSTATE_CHARGING
    CHARGED = RETRO_POWERSTATE_CHARGED
    PLUGGED_IN = RETRO_POWERSTATE_PLUGGED_IN


@dataclass(init=False, slots=True)
class retro_device_power(Structure):
    """
    Reports the power status of the host device,
    or whatever lies that libretro.py tells it to report.

    Corresponds to :c:type:`retro_device_power` in ``libretro.h``.
    """

    state: PowerState
    """Current power state of the device."""

    seconds: int
    """Estimated remaining battery time in seconds, or :const:`NO_ESTIMATE` if unknown."""

    percent: int
    """Battery charge percentage (0-100), or :const:`NO_ESTIMATE` if unknown."""

    _fields_ = (
        ("state", retro_power_state),
        ("seconds", c_int),
        ("percent", c_int8),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_device_power(state=self.state, seconds=self.seconds, percent=self.percent)


__all__ = [
    "PowerState",
    "retro_device_power",
    "retro_power_state",
    "NO_ESTIMATE",
]
