from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.input import Port
from libretro.api.rumble import RumbleEffect


@runtime_checkable
class RumbleDriver(Protocol):

    @abstractmethod
    def set_rumble_state(self, port: Port, effect: RumbleEffect, strength: int) -> bool:
        """
        Set the rumble state of a controller port.
        """
        ...


__all__ = [
    "RumbleDriver",
]
