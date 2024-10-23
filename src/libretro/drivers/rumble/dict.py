from dataclasses import dataclass

from libretro.api.rumble import RumbleEffect

from .driver import RumbleDriver


@dataclass(slots=True)
class RumbleState:
    """
    Simulated state of a pair of rumble motors.
    """

    strong: int
    weak: int

    def __getitem__(self, item: RumbleEffect) -> int:
        match item:
            case RumbleEffect.STRONG:
                return self.strong
            case RumbleEffect.WEAK:
                return self.weak
            case int(i):
                raise IndexError(f"Expected a valid RumbleEffect, got {i}")
            case e:
                raise TypeError(f"Expected a valid RumbleEffect, got: {type(e).__name__}")

    def __setitem__(self, key: RumbleEffect, value: int):
        match key, value:
            case RumbleEffect.STRONG, int(value):
                self.strong = value
            case RumbleEffect.WEAK, int(value):
                self.weak = value
            case RumbleEffect(), v:
                raise TypeError(f"Expected an int value, got: {type(v).__name__}")
            case int(k), _:
                raise IndexError(f"Expected a RumbleEffect key, got: {k}")
            case _, v:
                raise TypeError(f"Expected an int value, got: {type(v).__name__}")

    def __len__(self):
        return 2


class DictRumbleDriver(RumbleDriver):
    """
    A :class:`RumbleDriver` implementation that
    stores rumble state in a dictionary.
    """

    def __init__(self):
        super().__init__()
        self._rumble_state: dict[int, RumbleState] = {}

    def _set_rumble_state(self, port: int, effect: RumbleEffect, strength: int) -> bool:
        self._rumble_state[port] = RumbleState(effect, strength)
        return True

    def __getitem__(self, port: int) -> RumbleState:
        """
        Gets the state of the virtual rumble motors for a controller port.

        :param port: The controller port to get the rumble state for.
        :return: The rumble state for the controller port.
        """
        match self._rumble_state.get(port, None):
            case RumbleState(strong=strong, weak=weak):
                return RumbleState(strong, weak)
            case None:
                return RumbleState(0, 0)


__all__ = ["DictRumbleDriver", "RumbleState"]
