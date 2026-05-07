"""
:class:`.RumbleDriver` implementation that tracks per-port motor strengths in a dictionary.

.. seealso::

    :class:`.RumbleDriver`
        The protocol this driver implements.
"""

from dataclasses import dataclass
from typing import override

from libretro.api.input import Port
from libretro.api.rumble import RumbleEffect

from .driver import RumbleDriver


@dataclass(slots=True)
class RumbleState:
    """Simulated state of a pair of rumble motors."""

    strong: int
    weak: int

    def __getitem__(self, item: RumbleEffect) -> int:
        """Return the strength of the motor identified by ``item``."""
        match item:
            case RumbleEffect.STRONG:
                return self.strong
            case RumbleEffect.WEAK:
                return self.weak
            case int():
                raise IndexError(f"Expected a valid RumbleEffect, got {item}")
            case e:
                raise TypeError(f"Expected a valid RumbleEffect, got: {type(e).__name__}")

    def __setitem__(self, key: RumbleEffect, value: int):
        """Set the strength of the motor identified by ``key``."""
        match key, value:
            case RumbleEffect.STRONG, int(value):
                self.strong = value
            case RumbleEffect.WEAK, int(value):
                self.weak = value
            case RumbleEffect(), v:
                raise TypeError(f"Expected an int value, got: {type(v).__name__}")
            case int(), _:
                raise IndexError(f"Expected a RumbleEffect key, got: {key}")
            case _, v:
                raise TypeError(f"Expected an int value, got: {type(v).__name__}")

    def __len__(self):
        """Return the number of motors (always ``2``: one strong, one weak)."""
        return 2


class DictRumbleDriver(RumbleDriver):
    """
    A :class:`RumbleDriver` implementation that
    stores rumble state in a dictionary.
    """

    def __init__(self):
        """Initialize the driver with an empty per-port rumble state map."""
        super().__init__()
        self._rumble_state: dict[Port, RumbleState] = {}

    @override
    def set_rumble_state(self, port: Port, effect: RumbleEffect, strength: int) -> bool:
        self._rumble_state[port] = RumbleState(effect, strength)
        return True

    def __getitem__(self, port: Port) -> RumbleState:
        """
        Get the state of the virtual rumble motors for a controller port.

        :param port: The controller port to get the rumble state for.
        :return: The rumble state for the controller port.
        """
        match self._rumble_state.get(port, None):
            case RumbleState(strong=strong, weak=weak):
                return RumbleState(strong, weak)
            case None:
                return RumbleState(0, 0)


__all__ = ["DictRumbleDriver", "RumbleState"]
