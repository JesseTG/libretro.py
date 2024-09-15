import os
from os import PathLike, fsencode

from libretro._typing import override
from libretro.core import Core

from .driver import PathDriver


class ExplicitPathDriver(PathDriver):
    """
    A path driver that supports defining individual locations for each directory.
    """

    def __init__(
        self,
        corepath: str | bytes | PathLike | Core | None = None,
        system: str | bytes | PathLike | None = None,
        assets: str | bytes | PathLike | None = None,
        save: str | bytes | PathLike | None = None,
        playlist: str | bytes | PathLike | None = None,
    ):
        """
        Initialize a new :class:`.ExplicitPathDriver`,
        creating the specified directories if necessary.

        :param corepath:
            May be one of the following:

            :class:`str`, :class:`bytes`, :class:`~os.PathLike`
                Path to the libretro core.
                Will be encoded into UTF-8 if necessary
                and exposed to the core with ``RETRO_ENVIRONMENT_GET_LIBRETRO_PATH``.
                Not validated for existence, permissions, or correctness;
                i.e. this may have a different value than the loaded core's path,
                but you shouldn't do this
                unless you're specifically interested in testing this scenario.

            :class:`.Core`
                Its :py:attr:`~.Core.path` will be used as the libretro core path.
                The driver won't keep a reference to the core itself.

            :obj:`None`
                ``RETRO_ENVIRONMENT_GET_LIBRETRO_PATH`` will be unavailable to cores.

        :param system: The system directory that the core can access.
            Can be a :class:`str`, :class:`bytes`, or :class:`~os.PathLike`.
            If :obj:`None`, ``RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY``
            will not be available to the core.

        :param assets: The directory containing assets for the core.
            Can be a :class:`str`, :class:`bytes`, or :class:`~os.PathLike`.
            If :obj:`None`, ``RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY``
            will not be available to the core.

        :param save: The directory where the core can save data.
            Can be a :class:`str`, :class:`bytes`, or :class:`~os.PathLike`.
            If :obj:`None`, ``RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY``
            will not be available to the core.

        :param playlist: The directory where the core can read playlists.
            Can be a :class:`str`, :class:`bytes`, or :class:`~os.PathLike`.
            If :obj:`None`, ``RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY``
            will not be available to the core.

        :raises TypeError: If any of the arguments are not of the correct type.
        """
        self._libretro: bytes | None
        match corepath:
            case str():
                self._libretro = corepath.encode()
            case bytes() | None:
                self._libretro = corepath
            case PathLike():
                self._libretro = fsencode(corepath)
            case Core():
                self._libretro = corepath.path.encode()
            case _:
                raise TypeError(
                    f"Expected corepath to be a str, bytes, PathLike, Core, or None; got {corepath!r}"
                )

        self._system: bytes | None
        match system:
            case str():
                self._system = system.encode()
            case bytes() | None:
                self._system = system
            case PathLike():
                self._system = fsencode(system.encode())
            case _:
                raise TypeError(
                    f"Expected system to be str, bytes, PathLike, or None, got {system!r}"
                )

        self._assets: bytes | None
        match assets:
            case str():
                self._assets = assets.encode()
            case bytes() | None:
                self._assets = assets
            case PathLike():
                self._assets = fsencode(assets.encode())
            case _:
                raise TypeError(
                    f"Expected assets to be str, bytes, PathLike, or None, got {assets!r}"
                )

        self._save: bytes | None
        match save:
            case str():
                self._save = save.encode()
            case bytes() | None:
                self._save = save
            case PathLike():
                self._save = fsencode(save.encode())
            case _:
                raise TypeError(f"Expected save to be str, bytes, PathLike, or None, got {save!r}")

        self._playlist: bytes | None
        match playlist:
            case str():
                self._playlist = playlist.encode()
            case bytes() | None:
                self._playlist = playlist
            case PathLike():
                self._playlist = fsencode(playlist.encode())
            case _:
                raise TypeError(
                    f"Expected playlist to be str, bytes, PathLike, or None, got {playlist!r}"
                )

        os.makedirs(self._system, exist_ok=True)
        os.makedirs(self._assets, exist_ok=True)
        os.makedirs(self._save, exist_ok=True)
        os.makedirs(self._playlist, exist_ok=True)

    @override
    @property
    def system_dir(self) -> bytes | None:
        return self._system

    @override
    @property
    def libretro_path(self) -> bytes | None:
        return self._libretro

    @override
    @property
    def core_assets_dir(self) -> bytes | None:
        return self._assets

    @override
    @property
    def save_dir(self) -> bytes | None:
        return self._save

    @override
    @property
    def playlist_dir(self) -> bytes | None:
        return self._playlist


__all__ = ["ExplicitPathDriver"]
