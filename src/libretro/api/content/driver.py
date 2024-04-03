import os.path
from abc import abstractmethod
from collections.abc import Sequence, Mapping, Iterator, Generator, Iterable
from contextlib import contextmanager, ExitStack, AbstractContextManager
from ctypes import Array
from enum import Enum, auto
from os import PathLike
from typing import Protocol, runtime_checkable, AnyStr, TypeAlias, NamedTuple, BinaryIO

from .defs import *


class ContentAttributes(NamedTuple):
    block_extract: bool
    persistent_data: bool
    need_fullpath: bool
    required: bool


class LoadedContentFile:
    def __init__(self, info: retro_game_info, info_ext: retro_game_info_ext | None = None, persistent: bool = False, io: BinaryIO | None = None):
        if not isinstance(info, retro_game_info):
            raise TypeError(f"Expected retro_game_info, got {type(info).__name__}")

        if info_ext is not None and not isinstance(info_ext, retro_game_info_ext):
            raise TypeError(f"Expected retro_game_info_ext or None, got {type(info_ext).__name__}")

        if io is not None and not isinstance(io, BinaryIO):
            raise TypeError(f"Expected BinaryIO or None, got {type(io).__name__}")

        self._info = info
        self._info_ext = info_ext
        self._io = io
        self._persistent = bool(persistent)

    def __del__(self):
        self.close()

    def close(self):
        # Gotta clean up the pointers first,
        # since they may be holding on to references to the mapped buffer
        # (and freeing a mapped memory buffer before the pointers are cleared
        # may result in an exception)
        if self._info.data:
            self._info.data = None

        if self._info_ext:
            self._info_ext.data = None

        if self._io:
            self._io.close()

            del self._io

    @property
    def info(self) -> retro_game_info:
        return self._info

    @property
    def info_ext(self) -> retro_game_info_ext | None:
        return self._info_ext

    @property
    def persistent_data(self) -> bool:
        return self._persistent


LoadedContent = tuple[retro_subsystem_info | None, Sequence[LoadedContentFile] | None]


class ContentError(RuntimeError):
    pass


@runtime_checkable
class ContentDriver(Protocol):
    @contextmanager
    def load(self, content: Content | SubsystemContent | None) -> AbstractContextManager[LoadedContent]:
        if not self.system_info:
            raise RuntimeError("System info not set")

        with ExitStack() as stack:
            loaded_content: Sequence[LoadedContentFile] | None
            subsystem: retro_subsystem_info | None = None
            match content:
                case SubsystemContent(game_type=game_type, info=info):
                    subsystem = self.__get_subsystem(game_type)
                    if len(info) != len(subsystem):
                        raise ValueError(f"Subsystem {subsystem.ident!r} needs {len(subsystem)} ROMs, got {len(info)}")

                    i: int
                    c: Content
                    loaded_content = [stack.enter_context(self._load(i, subsystem, subsystem[i])) for (i, c) in enumerate(info)]
                case str() | PathLike() | bytes() | bytearray() | memoryview() | retro_game_info():
                    loaded_content = [stack.enter_context(self._load(content))]
                case None if self.support_no_game:
                    loaded_content = []
                case None:
                    raise ValueError("No content provided and core did not register support for no-content mode")
                case _:
                    raise TypeError(f"Expected a content path, data buffer, SubsystemContent, or retro_game_info; got {type(content).__name__}")

            yield subsystem, loaded_content

    @abstractmethod
    def _load(
        self,
        content: Content,
        subsystem: retro_subsystem_info | None = None,
        subsysrom: retro_subsystem_rom_info | None = None
    ) -> AbstractContextManager[LoadedContentFile]:
        """
        TODO load stuff

        :param content: The content to load.
        :param subsystem: The subsystem that content is being loaded for, defaults to ``None``.
            TODO write more
        :param subsysrom: The subsystem ROM that content is being loaded for, defaults to ``None``.
        """
        ...

    @property
    @abstractmethod
    def enable_extended_info(self) -> bool: ...

    @abstractmethod
    def get_game_info_ext(self) -> Array[retro_game_info_ext] | None: ...

    @property
    def game_info_ext(self) -> Array[retro_game_info_ext] | None:
        return self.get_game_info_ext()

    @abstractmethod
    def set_system_info(self, info: retro_system_info | None) -> None: ...

    @abstractmethod
    def get_system_info(self) -> retro_system_info | None: ...

    @property
    def system_info(self) -> retro_system_info | None:
        return self.get_system_info()

    @system_info.setter
    def system_info(self, info: retro_system_info) -> None:
        self.set_system_info(info)

    @system_info.deleter
    def system_info(self) -> None:
        self.set_system_info(None)

    @abstractmethod
    def set_overrides(self, overrides: Sequence[retro_system_content_info_override] | None) -> None: ...

    @abstractmethod
    def get_overrides(self) -> ContentInfoOverrides | None: ...

    @property
    def overrides(self) -> Sequence[retro_system_content_info_override] | None:
        return self.get_overrides()

    @overrides.setter
    def overrides(self, overrides: Sequence[retro_system_content_info_override]) -> None:
        self.set_overrides(overrides)

    @abstractmethod
    def set_subsystem_info(self, subsystems: Sequence[retro_subsystem_info] | None) -> None: ...

    @abstractmethod
    def get_subsystem_info(self) -> Subsystems | None: ...

    @property
    def subsystem_info(self) -> Subsystems | None:
        return self.get_subsystem_info()

    @subsystem_info.setter
    def subsystem_info(self, subsystems: Sequence[retro_subsystem_info]) -> None:
        self.set_subsystem_info(subsystems)

    @abstractmethod
    def set_support_no_game(self, support: bool) -> None: ...

    @abstractmethod
    def get_support_no_game(self) -> bool | None: ...

    @property
    def support_no_game(self) -> bool | None:
        return self.get_support_no_game()

    @support_no_game.setter
    def support_no_game(self, support: bool) -> None:
        self.set_support_no_game(support)

    def __get_subsystem(self, content: Content | SubsystemContent | None) -> retro_subsystem_info | None:
        if not isinstance(content, SubsystemContent):
            return None

        if not self.subsystem_info:
            raise RuntimeError("Subsystem content was provided, but core did not register subsystems")

        match content.game_type:
            case int(id):
                for s in self.subsystem_info:
                    if s.id == id:
                        return s

                raise ValueError(f"Core did not register a subsystem with a numeric ID of {id}")

            case str(ident) | bytes(ident):
                return self.subsystem_info[ident]

            case e:
                raise TypeError(f"Expected a subsystem identifier of types int, str, or bytes; got {type(e).__name__}")


__all__ = [
    "ContentDriver",
    "LoadedContentFile",
    "LoadedContent",
    "ContentError",
]
