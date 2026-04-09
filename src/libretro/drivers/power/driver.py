from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.power import retro_device_power


@runtime_checkable
class PowerDriver(Protocol):
    @property
    @abstractmethod
    def device_power(self) -> retro_device_power: ...


__all__ = [
    "PowerDriver",
]
