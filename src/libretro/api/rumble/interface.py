from abc import abstractmethod
from typing import Protocol, runtime_checkable

from .defs import *


@runtime_checkable
class RumbleInterface(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_rumble_interface()
        self._as_parameter_.set_rumble_state = retro_set_rumble_state_t(self.__set_rumble_state)

    @abstractmethod
    def set_rumble_state(self, port: int, effect: RumbleEffect, strength: int) -> bool: ...

    def __set_rumble_state(self, port: int, effect: int, strength: int) -> bool:
        if effect not in RumbleEffect:
            return False

        return self.set_rumble_state(port, RumbleEffect(effect), strength)


__all__ = [
    'RumbleInterface',
]
