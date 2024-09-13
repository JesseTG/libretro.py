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
        Corresponds to :py:attr:`.EnvironmentCall.GET_SYSTEM_DIRECTORY`.

        If :py:obj:`None`, a core's call to ``RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY`` should return ``false``.
        """
        ...

    @property
    @abstractmethod
    def libretro_path(self) -> bytes | None:
        """
        Corresponds to :py:attr:`.EnvironmentCall.GET_LIBRETRO_PATH`.

        If :py:obj:`None`, a core's call to ``RETRO_ENVIRONMENT_GET_LIBRETRO_PATH`` should return ``false``.
        """
        ...

    @property
    @abstractmethod
    def core_assets_dir(self) -> bytes | None:
        """
        Corresponds to :py:attr:`.EnvironmentCall.GET_CORE_ASSETS_DIRECTORY`.

        If :py:obj:`None`, a core's call to ``RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY`` should return ``false``.
        """
        ...

    @property
    @abstractmethod
    def save_dir(self) -> bytes | None:
        """
        Corresponds to :py:attr:`.EnvironmentCall.GET_SAVE_DIRECTORY`.

        If :py:obj:`None`, a core's call to ``RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY`` should return ``false``.
        """
        ...

    @property
    @abstractmethod
    def playlist_dir(self) -> bytes | None:
        """
        Corresponds to :py:attr:`.EnvironmentCall.GET_PLAYLIST_DIRECTORY`.

        If :py:obj:`None`, a core's call to ``RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY`` should return ``false``.
        """
        ...


__all__ = [
    "PathDriver",
]
