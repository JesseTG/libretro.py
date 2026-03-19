from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from libretro.api.location import retro_location_lifetime_status_t


@dataclass(frozen=True, slots=True)
class Position:
    latitude: float | None
    longitude: float | None
    horizontal_accuracy: float | None
    vertical_accuracy: float | None


@runtime_checkable
class LocationDriver(Protocol):
    @abstractmethod
    def start(self) -> bool: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def get_position(self) -> Position | None: ...

    @abstractmethod
    def set_interval(self, interval: int, distance: int) -> None: ...

    @property
    @abstractmethod
    def initialized(self) -> retro_location_lifetime_status_t | None: ...

    @initialized.setter
    @abstractmethod
    def initialized(self, value: retro_location_lifetime_status_t | None) -> None: ...

    @property
    @abstractmethod
    def deinitialized(self) -> retro_location_lifetime_status_t | None: ...

    @deinitialized.setter
    @abstractmethod
    def deinitialized(self, value: retro_location_lifetime_status_t | None) -> None: ...


__all__ = [
    "LocationDriver",
    "Position",
]
