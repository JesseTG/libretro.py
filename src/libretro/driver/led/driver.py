from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api import retro_led_interface, retro_set_led_state_t


@runtime_checkable
class LedDriver(Protocol):
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

    @abstractmethod
    def get_led_state(self, led: int) -> int: ...

    def __getitem__(self, key: int) -> int:
        return self.get_led_state(int(key))


__all__ = ["LedDriver"]
