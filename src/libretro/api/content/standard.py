import os
from contextlib import ExitStack, AbstractContextManager, contextmanager
from ctypes import c_ubyte, addressof, Array, c_void_p
from os import PathLike
from typing import Mapping, AnyStr, Sequence, Iterator, override, NamedTuple, BinaryIO
from zipfile import Path as ZipPath

from .driver import *
from .defs import *
from ..._utils import as_bytes


class _PersistentBuffer(NamedTuple):
    ptr: c_void_p
    backing: BinaryIO


class StandardContentDriver(ContentDriver):

    def __init__(self, enable_extended_info: bool = True):
        self._subsystems: Subsystems | None = None
        self._overrides: ContentInfoOverrides | None = None
        self._content: Sequence[retro_game_info] | None = None
        self._content_ext: Array[retro_game_info_ext] | None = None
        self._system_info: retro_system_info | None = None
        self._support_no_game: bool | None = None
        self._enable_extended_info = bool(enable_extended_info)
        self._persistent_buffers: set[_PersistentBuffer] = set()

    def __del__(self):
        for buf in self._persistent_buffers:
            del buf.ptr
            buf.backing.close()
            del buf.backing

    @property
    @override
    def enable_extended_info(self) -> bool:
        return self._enable_extended_info

    @enable_extended_info.setter
    def enable_extended_info(self, value: bool) -> None:
        self._enable_extended_info = bool(value)

    def get_game_info_ext(self) -> Array[retro_game_info_ext] | None:
        if not self._enable_extended_info:
            return None

        if not self._content:
            return None

        if not self._content_ext:
            arraytype: type[Array] = retro_game_info_ext * len(self._content)
            self._content_ext = arraytype()

            for i, info in enumerate(self._content):
                self._content_ext[i] = retro_game_info_ext(
                )

        return self._content_ext

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
                        raise ValueError(f"Subsystem {subsystem.ident!r} needs exactly {len(subsystem)} ROMs, got {len(info)}")

                    i: int
                    c: Content
                    loaded_content = [stack.enter_context(self._load(i, subsystem, subsystem[i])) for (i, c) in enumerate(info)]
                case ZipPath() | str() | PathLike() | bytes() | bytearray() | memoryview() | retro_game_info():
                    loaded_content = [stack.enter_context(self._load(content))]
                case None if self.support_no_game:
                    loaded_content = []
                case None:
                    raise ValueError("No content provided and core did not register support for no-content mode")
                case _:
                    raise TypeError(f"Expected a content path, data buffer, SubsystemContent, or retro_game_info; got {type(content).__name__}")

            yield subsystem, loaded_content

    @contextmanager
    def _load(
        self,
        content: Content,
        subsystem: retro_subsystem_info | None = None,
        subsysrom: retro_subsystem_rom_info | None = None
    ) -> AbstractContextManager[LoadedContentFile]:
        """
        :param content: The content to load
        :param subsystem: The subsystem we're using for this session, if any
        :param subsysrom: The descriptor for the ROM type we're using, if any
        """
        match subsystem, subsysrom, self._subsystems:
            case (retro_subsystem_info(), _, None) | (_, retro_subsystem_rom_info(), None):
                raise RuntimeError("Subsystem info or ROM info was provided, but the core didn't register subsystems")
            case (retro_subsystem_info(), None, _) | (None, retro_subsystem_rom_info(), _):
                raise ContentError("Subsystem info and subsystem ROM info must both be provided when loading subsystem content")

        loaded_info: retro_game_info | None = None
        loaded_info_ext: retro_game_info_ext | None = None

        ext = get_extension(content)
        if ext is not None:
            if not subsystem and ext not in self._system_info.extensions:
                raise ValueError(f"Content extension '{ext!r}' is not supported by the system")

            if subsystem and ext not in subsysrom.extensions:
                raise ValueError(f"Content extension '{ext!r}' is not supported by the {subsysrom.desc!r} ROM of subsystem {subsystem.ident!r}")

        need_fullpath = self.__needs_fullpath(ext, subsysrom)
        persistent_data = self.__is_data_persistent(ext)
        block_extract = self.__should_block_extract(ext, subsysrom)
        is_required = self.__is_required(ext, subsysrom)

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

    def __needs_fullpath(self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        assert subsysrom is None or isinstance(subsysrom, retro_subsystem_rom_info)
        # These params should've been validated by the caller

        match ext, subsysrom, self._overrides:
            case None, _, _:
                # If loading any content from in-memory...
                return False
            case bytes(), _, ContentInfoOverrides(overrides) if ext in overrides:
                # If loading a content file with a specially-treated extension...
                overrides: ContentInfoOverrides
                return overrides[ext].need_fullpath
            case bytes(), None, _ if ext.removeprefix(b'.') in self._system_info.extensions:
                # If loading a regular content file with no relevant overrides...
                return self._system_info.need_fullpath
            case bytes(), None, _:
                # No overrides were found, and the extension's not in the system info.
                raise ValueError(f"Can't determine if regular content extension '{ext!r}' needs a full path (it's not in the overrides or system info)")
            case bytes(), retro_subsystem_rom_info(), _:
                # If loading subsystem content with no relevant overrides, and the active subsystem is given directly...
                return subsysrom.need_fullpath
            case _, _, _:
                raise ValueError(f"Can't determine if subsystem content extension '{ext!r}' needs a full path")

    def __is_data_persistent(self, ext: bytes | None) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        # These params should've been validated by the caller

        match ext, self._overrides:
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
                raise ValueError(f"Can't determine if subsystem content extension '{ext!r}' has persistent data")

    def __should_block_extract(self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        assert subsysrom is None or isinstance(subsysrom, retro_subsystem_rom_info)
        # These params should've been validated by the caller

        # NOTE: retro_content_info_override does not have block_extract
        match ext, subsysrom:
            case (None, _) | (_, None):
                # If loading any content from in-memory or if not using a subsystem...
                return self._system_info.block_extract
            case bytes(), retro_subsystem_rom_info():
                # If loading a subsystem ROM...
                overrides: ContentInfoOverrides
                return subsysrom.block_extract
            case _, _:
                raise ValueError(f"Can't determine if subsystem content extension '{ext!r}' should block extraction")

    def __is_required(self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        assert subsysrom is None or isinstance(subsysrom, retro_subsystem_rom_info)
        # These params should've been validated by the caller

        # NOTE: retro_content_info_override and retro_system_info do not have required,
        # but retro_system_info does use RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME

        match ext, subsysrom:
            case (None, _) | (_, None):
                # If loading any content from in-memory or if not using a subsystem...
                return self._system_info.required
            case bytes(), retro_subsystem_rom_info():
                # If loading a subsystem ROM...
                overrides: ContentInfoOverrides
                return subsysrom.required
            case _, _:
                raise ValueError(f"Can't determine if subsystem content extension '{ext!r}' is required")


__all__ = [
    "StandardContentDriver",
]
