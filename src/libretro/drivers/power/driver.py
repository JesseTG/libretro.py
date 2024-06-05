from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro._typing import override
from libretro.api.power import retro_device_power


@runtime_checkable
class PowerDriver(Protocol):
    @property
    @abstractmethod
    def device_power(self) -> retro_device_power: ...


class ConstantPowerDriver(PowerDriver):
    def __init__(self, device_power: retro_device_power):
        self._device_power: retro_device_power
        self.device_power = device_power

    @property
    @override
    def device_power(self) -> retro_device_power:
        return self._device_power

    @device_power.setter
    def device_power(self, device_power: retro_device_power) -> None:
        if not isinstance(device_power, retro_device_power):
            raise TypeError(f"Expected a retro_device_power, got: {type(device_power).__name__}")
        self._device_power = device_power


__all__ = [
    "PowerDriver",
    "ConstantPowerDriver",
]
