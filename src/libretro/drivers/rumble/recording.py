"""
:class:`.RumbleDriver` implementation that records every rumble request it receives.

.. seealso::

    :class:`.DictRumbleDriver`
        The driver this one extends,
        which tracks the latest motor strengths but not the calls that set them.
"""

from collections.abc import Sequence
from typing import NamedTuple, override

from libretro.api.input import Port
from libretro.api.rumble import RumbleEffect

from .dict import DictRumbleDriver


class RumbleCall(NamedTuple):
    """A single request to change one motor's strength."""

    port: Port
    """The controller :term:`port` that was addressed."""

    effect: RumbleEffect
    """The motor that was addressed."""

    strength: int
    """The requested motor intensity, in the range ``[0, 0xFFFF]``."""


class RecordingRumbleDriver(DictRumbleDriver):
    """
    A :class:`.DictRumbleDriver` that also keeps a log of every call it receives.

    Use this to assert on a core's rumble *behavior* rather than its final state,
    such as how often the core updates the motors
    or the order in which it addresses them.

    .. seealso::

        :mod:`libretro.api.rumble`
            The matching :mod:`ctypes` types and callback definitions.
    """

    def __init__(self):
        """Initialize the driver with an empty motor state map and an empty call log."""
        super().__init__()
        self._calls: list[RumbleCall] = []

    @override
    def set_rumble_state(self, port: Port, effect: RumbleEffect, strength: int) -> bool:
        result = super().set_rumble_state(port, effect, strength)
        self._calls.append(RumbleCall(Port(port), RumbleEffect(effect), strength))
        return result

    @property
    def calls(self) -> Sequence[RumbleCall]:
        """
        Every rumble request this driver has received, in the order they arrived.

        :return: A snapshot of the call log.
        """
        return tuple(self._calls)

    def clear(self) -> None:
        """
        Discard the recorded call log.

        The motors' current strengths are left as they are;
        only the record of how they got there is dropped.
        """
        self._calls.clear()


__all__ = ["RecordingRumbleDriver", "RumbleCall"]
