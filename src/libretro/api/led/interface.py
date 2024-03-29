from abc import abstractmethod
from typing import runtime_checkable, Protocol

from .defs import *


@runtime_checkable
class LedInterface(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_led_interface()
        self._as_parameter_.set_led_state = retro_set_led_state_t(self.__set_led_state)

    def __set_led_state(self, led: int, state: int) -> None:
        self.set_led_state(led, state)

    @abstractmethod
    def set_led_state(self, led: int, state: int) -> None: ...

    def __setitem__(self, key: int, value: int):
        self.set_led_state(int(key), int(value))


__all__ = ['LedInterface']
