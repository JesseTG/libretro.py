import os
from contextlib import ExitStack, AbstractContextManager, contextmanager
from ctypes import c_ubyte, Array, addressof
from os import PathLike
from typing import Mapping, AnyStr, Sequence, Iterator, override

from .driver import *
from .defs import *
from ..._utils import as_bytes


class StandardContentDriver(ContentDriver):
    def __init__(self, enable_extended_info: bool = True):
        self._subsystems: Subsystems | None = None
        self._overrides: ContentInfoOverrides | None = None
        self._content: Sequence[retro_game_info] | None = None
        self._system_info: retro_system_info | None = None
        self._support_no_game: bool | None = None
        self._enable_extended_info = bool(enable_extended_info)

    @property
    @override
    def enable_extended_info(self) -> bool:
        return self._enable_extended_info

    @enable_extended_info.setter
    def enable_extended_info(self, value: bool) -> None:
        self._enable_extended_info = bool(value)

    @contextmanager
    @override
    def _load(
        self,
        content: Content,
        subsystem: retro_subsystem_info | None = None,
        subsysrom: retro_subsystem_rom_info | None = None
    ) -> AbstractContextManager[LoadedContentFile]:
        if subsystem and not subsysrom:
            raise ValueError("subsystem ROM info must be provided when loading subsystem content")

        if subsysrom and not subsystem:
            raise ValueError("subsystem must be specified when loading subsystem content")

        if subsystem and not self._subsystems:
            raise RuntimeError("Subsystem content was provided, but core did not register subsystems")

        loaded_info: retro_game_info | None = None
        loaded_info_ext: retro_game_info_ext | None = None

        ext = get_extension(content)
        if ext is not None:
            if not subsystem and ext not in self._system_info.extensions:
                raise ValueError(f"Content extension '{ext!r}' is not supported by the system")

            if subsystem and ext not in subsysrom.extensions:
                raise ValueError(f"Content extension '{ext!r}' is not supported by the {subsysrom.desc!r} ROM of subsystem {subsystem.ident!r}")

        # TODO: Handle retro_subsystem_rom_info.required
        # TODO: Handle retro_subsystem_rom_info.block_extract and retro_system_info.block_extract
        need_fullpath = self.__needs_fullpath(ext, subsystem)
        persistent_data = self.__is_data_persistent(ext)

        match content, need_fullpath, persistent_data:
            # For test cases that create a retro_game_info manually
            case retro_game_info(info), True, _ if not info.path:
                # If trying to use a manually-created game info that needs a full path, but didn't give one...
                raise ValueError("Core needs a full path, but none was provided")
            case retro_game_info(info), False, _ if not info.data:
                # If trying to use a manually-created game info that doesn't need a full path, but didn't give data...
                raise ValueError("Core needs retro_game_info to include data, but none was provided")
            case retro_game_info(info), _, persistent_data:
                yield LoadedContentFile(
                    info=info,
                    info_ext=None,  # TODO: Given a retro_game_info, construct a retro_game_info_ext
                    persistent=persistent_data,
                )

            # For test cases with content that needs a full path, but load their own data
            case str(path) | PathLike(path), True, _:
                loaded_info = retro_game_info(os.fsencode(path), None, 0, None)

            case str(path) | PathLike(path), False, persistent:
                w = map_content(path)
                # TODO: Validate that info matches system_info and content overrides
                # TODO: Create a content_ext
                with map_content(path) as info:
                    yield info
                    info.data = None

            # For test cases that provide ROM data directly
            case bytes() | bytearray() | memoryview(), True, _:
                raise ValueError("Core requires a full path, but only raw data was provided")

            case bytes(rom) | bytearray(rom) | memoryview(rom), False, _:
                loaded = self._core.load_game(retro_game_info(None, rom, len(rom), None))

            case SubsystemContent(), _, _ if not self._subsystems:
                raise RuntimeError("Subsystem content was provided, but core did not register subsystems")

            case SubsystemContent(game_type=str(ident) | bytes(ident), info=infos) as subsystem_content:
                idents = tuple(as_bytes(s.ident) for s in self._subsystems)
                if as_bytes(ident) not in idents:
                    raise ValueError(f"Content with unregistered subsystem ident {ident!r} can't be loaded by the core")

                typeid = tuple(s.id for s in self._subsystem_info if as_bytes(s.ident) == as_bytes(ident))
                assert len(typeid) > 0

                #with self.map_content(subsystem_content) as content:
                #    pass

                # TODO: Verify conditions
                loaded = self._core.load_game_special(typeid[0], infos)

            case SubsystemContent(game_type=int(game_type), info=infos):
                ids = tuple(int(s.id) for s in self._subsystem_info)
                if game_type not in ids:
                    raise ValueError(f"Content with unregistered subsystem type {game_type} can't be loaded by the core")

                # TODO: Verify conditions
                loaded = self._core.load_game_special(game_type, infos)

            case None if self._support_no_game:
                loaded = self._core.load_game(None)

            case None:
                raise RuntimeError("No content provided and core did not indicate support for no game.")

        if not persistent_data:
            if loaded_info:
                loaded_info.data = None

            if loaded_info_ext:
                loaded_info_ext.data = None

    @override
    def set_system_info(self, info: retro_system_info | None) -> None:
        self._system_info = info

    @override
    def get_system_info(self) -> retro_system_info | None:
        return self._system_info

    def set_subsystem_info(self, subsystems: Sequence[retro_subsystem_info] | None) -> None:
        self._subsystems = Subsystems(subsystems) if subsystems else None

    def get_subsystem_info(self) -> Subsystems | None:
        return self._subsystems

    def set_support_no_game(self, support: bool) -> None:
        self._support_no_game = support

    def get_support_no_game(self) -> bool | None:
        return self._support_no_game

    def set_overrides(self, overrides: Sequence[retro_system_content_info_override] | None) -> None:
        self._overrides = ContentInfoOverrides(overrides) if overrides else None

    def get_overrides(self) -> ContentInfoOverrides | None:
        return self._overrides

    def __needs_fullpath(
        self,
        extension: bytes | str | None,
        subsystem: bytes | str | retro_subsystem_info | None = None
    ) -> bool:
        if not self._system_info:
            raise RuntimeError("System info not set")

        if subsystem and not self._subsystems:
            raise ValueError(f"Subsystem ROM info provided, but none were registered by the core")

        ext: bytes
        match as_bytes(extension).removeprefix(b'.'), subsystem, self._overrides:
            case None, _, _:
                # If loading any content from in-memory...
                return False
            case bytes(ext), _, ContentInfoOverrides(overrides) if ext in overrides:
                # If loading a content file with a specially-treated extension...
                overrides: ContentInfoOverrides
                return overrides[ext].need_fullpath
            case bytes(ext), None, _ if ext in self._system_info.extensions:
                # If loading a regular content file with no relevant overrides...
                return self._system_info.need_fullpath
            case bytes(ext), None, _:
                # No overrides were found, and the extension's not in the system info.
                raise ValueError(f"Can't determine if regular content extension '{ext!r}' needs a full path (it's not in the overrides or system info)")
            case bytes(ext), retro_subsystem_info(subsys), _:
                # If loading subsystem content with no relevant overrides, and the active subsystem is given directly...
                subsys: retro_subsystem_info
                return subsys.by_extension(ext).need_fullpath
            case bytes(ext), bytes(ident) | str(ident), _:
                # If loading subsystem content with no relevant overrides, and the active subsystem is given by ident...
                return self._subsystems[ident].by_extension(ext).need_fullpath
            case _, _, _:
                raise ValueError(f"Can't determine if subsystem content extension '{extension!r}' needs a full path")

    def __is_data_persistent(self, extension: bytes | str | None) -> bool:
        if not self._system_info:
            raise RuntimeError("System info not set")

        ext: bytes
        match as_bytes(extension).removeprefix(b'.'), self._overrides:
            case None, _:
                # If loading any content from in-memory...
                return True
            case bytes(ext), ContentInfoOverrides(overrides) if ext in overrides:
                # If loading a content file with a specially-treated extension...
                overrides: ContentInfoOverrides
                return overrides[ext].persistent_data
            case bytes(ext), _ if ext in self._system_info.extensions:
                # If loading a regular content file with no relevant overrides...
                return False  # Regular content is not guaranteed to be persistent
            case _, _:
                raise ValueError(f"Can't determine if subsystem content extension '{extension!r}' has persistent data")


__all__ = [
    "StandardContentDriver",
]
