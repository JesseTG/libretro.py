from abc import abstractmethod
from collections.abc import Sequence
from contextlib import AbstractContextManager
from ctypes import Array
from typing import NamedTuple, Protocol, runtime_checkable

from libretro.api import (
    Content,
    ContentInfoOverrides,
    SubsystemContent,
    Subsystems,
    retro_game_info,
    retro_game_info_ext,
    retro_subsystem_info,
    retro_system_content_info_override,
    retro_system_info,
)


class ContentAttributes(NamedTuple):
    block_extract: bool
    persistent_data: bool
    need_fullpath: bool
    required: bool


class LoadedContentFile:
    def __init__(self, info: retro_game_info, info_ext: retro_game_info_ext | None = None):
        if not isinstance(info, retro_game_info):
            raise TypeError(f"Expected retro_game_info, got {type(info).__name__}")

        if info_ext is not None and not isinstance(info_ext, retro_game_info_ext):
            raise TypeError(f"Expected retro_game_info_ext or None, got {type(info_ext).__name__}")

        self._info = info
        self._info_ext = info_ext

    @property
    def info(self) -> retro_game_info:
        return self._info

    @property
    def info_ext(self) -> retro_game_info_ext | None:
        return self._info_ext


LoadedContent = tuple[retro_subsystem_info | None, Sequence[LoadedContentFile] | None]


class ContentError(RuntimeError):
    pass


@runtime_checkable
class ContentDriver(Protocol):
    """
    Driver protocol for loading content and enforcing content attributes.
    """

    @abstractmethod
    def load(
        self, content: Content | SubsystemContent | None
    ) -> AbstractContextManager[LoadedContent]:
        """
        Loads all content files.

        The ``content`` parameter may be one of the following:

        - ``None``, which will result in no content being loaded.
        - A ``zipfile.Path`` object representing a file within a ZIP archive.
        - A ``str`` or a ``PathLike`` object representing a file path.
          The loaded content will not be part of a subsystem.
          If ``self.system_info.needs_fullpath`` is ``False``
          and no override for this extension defines ``need_fullpath`` as ``True``,
          the driver will load the content as a file.
          Otherwise, the path will be provided to the core without opening the file.
        - A ``bytes``, ``bytearray``, ``memoryview``, or ``Buffer`` object that represents content data.
          The loaded content will be passed directly to the core without being set to a path.
        - A ``retro_game_info`` object, which will be passed to the core as-is.

        :param content: The content to load.
        :raises FileNotFoundError: If ``content`` is a path to a non-existent file.
        :raises ContentError: If loading ``None`` and the core requires content,
            or if ``content`` is a ``retro_game_info``
            whose attributes are inconsistent with `needs_fullpath` and `block_extract`.
        :raises RuntimeError: If called before ``system_info`` is set.
        :return: A context manager that yields a tuple containing the subsystem info and a sequence of loaded content files.
            Non-persistent content files will be closed when the context manager exits.

        .. note::
            All files not marked as persistent will be closed when the context manager exits.
            The ones that are persistent will be closed when the driver is destroyed.
        """
        ...

    @property
    @abstractmethod
    def enable_extended_info(self) -> bool: ...

    @property
    @abstractmethod
    def game_info_ext(self) -> Array[retro_game_info_ext] | None: ...

    @property
    @abstractmethod
    def system_info(self) -> retro_system_info | None: ...

    @system_info.setter
    @abstractmethod
    def system_info(self, info: retro_system_info) -> None: ...

    @property
    @abstractmethod
    def overrides(self) -> Sequence[retro_system_content_info_override] | None: ...

    @overrides.setter
    @abstractmethod
    def overrides(self, overrides: Sequence[retro_system_content_info_override]) -> None: ...

    @property
    @abstractmethod
    def subsystem_info(self) -> Subsystems | None: ...

    @subsystem_info.setter
    @abstractmethod
    def subsystem_info(self, subsystems: Sequence[retro_subsystem_info]) -> None: ...

    @property
    @abstractmethod
    def support_no_game(self) -> bool | None: ...

    @support_no_game.setter
    @abstractmethod
    def support_no_game(self, support: bool) -> None: ...


__all__ = [
    "ContentDriver",
    "ContentAttributes",
    "LoadedContentFile",
    "LoadedContent",
    "ContentError",
]
