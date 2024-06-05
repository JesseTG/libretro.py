from os import PathLike, fsencode

from libretro._typing import override

from .driver import PathDriver


class DefaultPathDriver(PathDriver):
    def __init__(
        self,
        corepath: str | bytes | PathLike | None = None,
        system: str | bytes | PathLike | None = None,
        assets: str | bytes | PathLike | None = None,
        save: str | bytes | PathLike | None = None,
        playlist: str | bytes | PathLike | None = None,
    ):
        self._libretro: bytes | None
        match corepath:
            case str():
                self._libretro = corepath.encode()
            case bytes() | None:
                self._libretro = corepath
            case PathLike():
                self._libretro = fsencode(corepath.encode())
            case _:
                raise TypeError(f"Expected str, bytes, PathLike, Core, or None, got {corepath!r}")

        self._system: bytes | None
        match system:
            case str():
                self._system = system.encode()
            case bytes() | None:
                self._system = system
            case PathLike():
                self._system = fsencode(system.encode())
            case _:
                raise TypeError(f"Expected str, bytes, PathLike, or None, got {system!r}")

        self._assets: bytes | None
        match assets:
            case str():
                self._assets = assets.encode()
            case bytes() | None:
                self._assets = assets
            case PathLike():
                self._assets = fsencode(assets.encode())
            case _:
                raise TypeError(f"Expected str, bytes, PathLike, or None, got {assets!r}")

        self._save: bytes | None
        match save:
            case str():
                self._save = save.encode()
            case bytes() | None:
                self._save = save
            case PathLike():
                self._save = fsencode(save.encode())
            case _:
                raise TypeError(f"Expected str, bytes, PathLike, or None, got {save!r}")

        self._playlist: bytes | None
        match playlist:
            case str():
                self._playlist = playlist.encode()
            case bytes() | None:
                self._playlist = playlist
            case PathLike():
                self._playlist = fsencode(playlist.encode())
            case _:
                raise TypeError(f"Expected str, bytes, PathLike, or None, got {playlist!r}")

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


__all__ = ["DefaultPathDriver"]
