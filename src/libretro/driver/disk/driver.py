from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.disk import (
    retro_disk_control_callback,
    retro_disk_control_ext_callback,
)


@runtime_checkable
class DiskDriver(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @property
    @abstractmethod
    def callback(
        self,
    ) -> retro_disk_control_callback | retro_disk_control_ext_callback | None: ...

    @callback.setter
    @abstractmethod
    def callback(
        self, value: retro_disk_control_callback | retro_disk_control_ext_callback
    ) -> None: ...

    @callback.deleter
    @abstractmethod
    def callback(self) -> None: ...

    @property
    @abstractmethod
    def eject_state(self) -> bool: ...

    @eject_state.setter
    @abstractmethod
    def eject_state(self, value: bool) -> None: ...


__all__ = [
    "DiskDriver",
]
