from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.rumble import (
    RumbleEffect,
    retro_rumble_interface,
    retro_set_rumble_state_t,
)


@runtime_checkable
class RumbleInterface(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_rumble_interface()
        self._as_parameter_.set_rumble_state = retro_set_rumble_state_t(self.__set_rumble_state)

    @abstractmethod
    def _set_rumble_state(self, port: int, effect: RumbleEffect, strength: int) -> bool: ...

    def set_rumble_state(self, port: int, effect: RumbleEffect | int, strength: int) -> bool:
        """
        Set the rumble state of a controller port.

        Validates the input and calls the implementation of _set_rumble_state.
        """
        if not isinstance(port, int):
            raise TypeError(f"port must be an int, not {type(port).__name__}")

        if not (0 <= port < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= port < 2**32 - 1, got {port}")

        if effect not in RumbleEffect:
            raise ValueError(f"effect must be a RumbleEffect or int, not {effect}")

        if not isinstance(strength, int):
            raise TypeError(f"strength must be an int, not {type(strength).__name__}")

        if not (0 <= strength < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= strength < 2**32 - 1, got {strength}")

        return self._set_rumble_state(port, RumbleEffect(effect), strength)

    def __set_rumble_state(self, port: int, effect: int, strength: int) -> bool:
        return self.set_rumble_state(port, RumbleEffect(effect), strength)


__all__ = [
    "RumbleInterface",
]
