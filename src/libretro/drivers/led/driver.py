from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class LedDriver(Protocol):
    @abstractmethod
    def set_led_state(self, led: int, state: int) -> None: ...

    def __setitem__(self, key: int, value: int):
        self.set_led_state(int(key), int(value))

    @abstractmethod
    def get_led_state(self, led: int) -> int: ...

    def __getitem__(self, key: int) -> int:
        return self.get_led_state(int(key))


__all__ = ["LedDriver"]
