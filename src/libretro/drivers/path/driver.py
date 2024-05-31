from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class PathDriver(Protocol):
    """
    Interface for a driver that defines various paths exposed to libretro cores.
    """

    @property
    @abstractmethod
    def system_dir(self) -> bytes | None:
        """
        Corresponds to ``EnvironmentCall.GET_SYSTEM_DIRECTORY``.
        """
        ...

    @property
    @abstractmethod
    def libretro_path(self) -> bytes | None: ...

    @property
    @abstractmethod
    def core_assets_dir(self) -> bytes | None: ...

    @property
    @abstractmethod
    def save_dir(self) -> bytes | None: ...

    @property
    @abstractmethod
    def playlist_dir(self) -> bytes | None: ...


__all__ = [
    "PathDriver",
]
