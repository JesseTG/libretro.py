"""
Types and classes for creating temporary directories for the core to use.
"""

import os
from os import PathLike, fsdecode, fsencode
from tempfile import TemporaryDirectory

from libretro._typing import override
from libretro.core import Core

from .driver import PathDriver


class TempDirPathDriver(PathDriver):
    """
    A path driver that creates temporary directories for the core to use.

    Test cases should add required files to these directories before running the core.
    """

    def __init__(
        self,
        corepath: str | bytes | PathLike | Core | None = None,
        prefix: str | bytes = b"libretro.py-",
    ):
        """
        Initializes a new :py:class:`.TempDirPathDriver` and creates the necessary directories.

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

        :param prefix: A prefix that will be applied to the temporary directory's name.
            Can be a :class:`str` or :class:`bytes`.

        :raises TypeError: If any of the arguments are not of the specified types.
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

        self._root: TemporaryDirectory[bytes]
        match prefix:
            case str() | bytes():
                self._root = TemporaryDirectory(prefix=fsencode(prefix))
            case None:
                self._root = TemporaryDirectory(prefix=b"libretro.py-")
            case _:
                raise TypeError(f"Expected prefix to be a str or bytes; got {prefix!r}")

        self._root_path = self._root.name
        self._system_path = os.path.join(self._root.name, b"system")
        self._assets_path = os.path.join(self._root.name, b"assets")
        self._save_path = os.path.join(self._root.name, b"save")
        self._playlist_path = os.path.join(self._root.name, b"playlist")

        os.makedirs(self._system_path)
        os.makedirs(self._assets_path)
        os.makedirs(self._save_path)
        os.makedirs(self._playlist_path)

    @property
    def root_dir(self) -> bytes:
        """
        Path to the root directory created by this driver.
        """
        return self._root_path

    @override
    @property
    def system_dir(self) -> bytes | None:
        return self._system_path

    @override
    @property
    def libretro_path(self) -> bytes | None:
        return self._libretro

    @override
    @property
    def core_assets_dir(self) -> bytes | None:
        return self._assets_path

    @override
    @property
    def save_dir(self) -> bytes | None:
        return self._save_path

    @override
    @property
    def playlist_dir(self) -> bytes | None:
        return self._playlist_path


__all__ = [
    "TempDirPathDriver",
]
