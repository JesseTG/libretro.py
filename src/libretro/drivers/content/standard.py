import os
from collections.abc import Sequence
from contextlib import AbstractContextManager, ExitStack, contextmanager
from ctypes import Array, c_void_p
from os import PathLike
from tempfile import TemporaryDirectory
from zipfile import Path as ZipPath

from libretro._typing import override
from libretro.api import (
    Content,
    ContentInfoOverrides,
    SubsystemContent,
    Subsystems,
    get_extension,
    retro_game_info,
    retro_game_info_ext,
    retro_subsystem_info,
    retro_subsystem_rom_info,
    retro_system_content_info_override,
    retro_system_info,
)
from libretro.api._utils import addressof_buffer, mmap_file

from .driver import (
    ContentAttributes,
    ContentDriver,
    ContentError,
    LoadedContent,
    LoadedContentFile,
)


class _PersistentBuffer:
    def __init__(self, ptr: c_void_p, backing: AbstractContextManager | None):
        self.ptr = ptr
        self.backing = backing

    def __del__(self):
        self.close()

    def close(self) -> None:
        if self.backing:
            self.backing.__exit__(None, None, None)
            del self.backing
            self.backing = None

        if self.ptr:
            del self.ptr
            self.ptr = None


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
        self._persistent_buffers.clear()

    @property
    @override
    def enable_extended_info(self) -> bool:
        return self._enable_extended_info

    @enable_extended_info.setter
    def enable_extended_info(self, value: bool) -> None:
        self._enable_extended_info = bool(value)

    @property
    @override
    def game_info_ext(self) -> Array[retro_game_info_ext] | None:
        if not self._enable_extended_info:
            return None

        if not self._content:
            return None

        return self._content_ext

    @contextmanager
    def load(
        self, content: Content | SubsystemContent | None
    ) -> AbstractContextManager[LoadedContent]:
        if not self._system_info:
            raise RuntimeError("System info not set")

        with ExitStack() as stack:
            # We may be loading several files, each of which needs its own context manager
            # So we use ExitStack to manage all of their lives at once
            loaded_content: Sequence[LoadedContentFile | None] | None
            subsystem: retro_subsystem_info | None = None
            match content:
                case SubsystemContent(game_type=game_type, info=info):
                    subsystem = self.__get_subsystem(content)
                    if len(info) != len(subsystem):
                        raise ValueError(
                            f"Subsystem {subsystem.ident!r} needs exactly {len(subsystem)} ROMs, got {len(info)}"
                        )

                    i: int
                    c: Content
                    loaded_content = [
                        stack.enter_context(self._load(c, subsystem, subsystem[i]))
                        for (i, c) in enumerate(info)
                    ]
                case (
                    ZipPath()
                    | str()
                    | PathLike()
                    | bytes()
                    | bytearray()
                    | memoryview()
                    | retro_game_info()
                ):
                    loaded_content = [stack.enter_context(self._load(content))]
                case None if self.support_no_game:
                    loaded_content = []
                case None:
                    raise ValueError(
                        "No content provided and core did not register support for no-content mode"
                    )
                case _:
                    raise TypeError(
                        f"Expected a content path, data buffer, SubsystemContent, or retro_game_info; got {type(content).__name__}"
                    )

            # Now that we've loaded all the content, let's create the extended info array
            content_ext_type: type[Array] = retro_game_info_ext * len(loaded_content)
            self._content_ext = content_ext_type()
            for i, lc in enumerate(loaded_content):
                self._content_ext[i] = lc.info_ext or retro_game_info_ext()

            # Now we hand off the loaded content to retro_load_game...
            yield subsystem, loaded_content
            # ...and now that retro_load_game has finished, let's clean up the loaded content
            # (but persistent buffers will be kept open in self._persistent_buffers)

            del self._content_ext
            del loaded_content

    @contextmanager
    def _load(
        self,
        content: Content,
        subsystem: retro_subsystem_info | None = None,
        subsysrom: retro_subsystem_rom_info | None = None,
    ) -> AbstractContextManager[LoadedContentFile | None]:
        """
        :param content: The content to load
        :param subsystem: The subsystem we're using for this session, if any
        :param subsysrom: The descriptor for the ROM type we're using, if any
        """
        match subsystem, subsysrom, self._subsystems:
            case (retro_subsystem_info(), _, None) | (
                _,
                retro_subsystem_rom_info(),
                None,
            ):
                raise RuntimeError(
                    "Subsystem info or ROM info was provided, but the core didn't register subsystems"
                )
            case (retro_subsystem_info(), None, _) | (
                None,
                retro_subsystem_rom_info(),
                _,
            ):
                raise ContentError(
                    "Subsystem info and subsystem ROM info must both be provided when loading subsystem content"
                )

        ext = get_extension(content)
        if ext is not None:
            if not subsystem and ext not in self._system_info.extensions:
                raise ContentError(f"Content extension '{ext!r}' is not supported by the system")

            if subsystem and ext not in subsysrom.extensions:
                raise ContentError(
                    f"Content extension '{ext!r}' is not supported by the {subsysrom.desc!r} ROM of subsystem {subsystem.ident!r}"
                )

        attributes = ContentAttributes(
            block_extract=self.__should_block_extract(ext, subsysrom),
            persistent_data=self.__is_data_persistent(ext),
            need_fullpath=self.__needs_fullpath(ext, subsysrom),
            required=self.__is_required(ext, subsysrom),
        )

        def _make_game_info_ext(info: retro_game_info) -> retro_game_info_ext:
            # The frontend can lie to the core and say it extracted the content from an archive
            path: bytes | None
            path, sep, archive_file = (
                info.path.partition(b"#") if info.path else (None, None, None)
            )
            # path will be the content path if content is not in an archive
            # path will be the archive path if content *is* in an archive

            file_in_archive = bool(sep and archive_file)
            _dir = os.path.dirname(path) if path else None
            name = os.path.basename(path) if path else None
            return retro_game_info_ext(
                full_path=info.path if not file_in_archive else None,
                archive_path=path or None,  # Will be None if file_in_archive is False
                archive_file=archive_file or None,  # Will be None if file_in_archive is False
                dir=_dir,  # Will be the content dirname if not an archive
                name=name,
                ext=ext.lower(),
                meta=info.meta,
                data=info.data,
                size=info.size,
                file_in_archive=file_in_archive,
                persistent_data=attributes.persistent_data,
            )

        loaded_info: retro_game_info | None = None
        loaded_info_ext: retro_game_info_ext | None = None
        match content, attributes:
            # For test cases that create a retro_game_info manually.
            case retro_game_info(path=None), ContentAttributes(need_fullpath=True):
                # If trying to use a manually-created game info that needs a full path, but didn't give one...
                raise ValueError("Core needs a full path, but none was provided")
            case retro_game_info(data=None), ContentAttributes(need_fullpath=False):
                # If trying to use a manually-created game info that doesn't need a full path, but didn't give data...
                raise ValueError(
                    "Core needs retro_game_info to include data, but none was provided"
                )
            case retro_game_info(path=None, data=None), _:
                raise ValueError("Core needs a full path or data, but neither was provided")
            case retro_game_info(info), ContentAttributes(persistent_data=persistent_data):
                info: retro_game_info

                loaded_info = info
                loaded_info_ext = _make_game_info_ext(info)

                if persistent_data:
                    self._persistent_buffers.add(_PersistentBuffer(c_void_p(info.data), None))

                # Give the loaded content to the environment
                yield LoadedContentFile(loaded_info, loaded_info_ext)

            case ZipPath(zippath), ContentAttributes(
                need_fullpath=True, block_extract=False, persistent_data=False
            ):
                # If the core needs a full path...
                zippath: ZipPath
                with TemporaryDirectory() as tmp:
                    tmpfile = zippath.root.extract(zippath.at, tmp)
                    loaded_info = retro_game_info(os.fsencode(tmpfile), None, 0, None)
                    loaded_info_ext = _make_game_info_ext(loaded_info)
                    yield LoadedContentFile(loaded_info, loaded_info_ext)
            case ZipPath(zippath), ContentAttributes(need_fullpath=True, block_extract=True):
                # If the core needs a full path and we're blocking extraction...
                raise ContentError(
                    f"Cannot extract {zippath}; core requires a full path, but block_extract is enabled"
                )
            case ZipPath(zippath), ContentAttributes(
                need_fullpath=False
            ):  # TODO: Is block_extract significant here?
                path = f"{zippath.filename}#{zippath.name}".encode()
                data = zippath.read_bytes()
                loaded_info = retro_game_info(path, addressof_buffer(data), len(data), None)
                loaded_info_ext = _make_game_info_ext(loaded_info)

                if attributes.persistent_data:
                    self._persistent_buffers.add(
                        _PersistentBuffer(c_void_p(loaded_info.data), None)
                    )

                yield LoadedContentFile(loaded_info, loaded_info_ext)

            # For test cases that provide content by path
            case (str() | PathLike()) as path, ContentAttributes(need_fullpath=True):
                loaded_info = retro_game_info(os.fsencode(path), None, 0, None)
                loaded_info_ext = _make_game_info_ext(loaded_info)
                yield LoadedContentFile(loaded_info, loaded_info_ext)
                # There's no data to persist, so no cleanup needed
            case (str() | PathLike()) as path, ContentAttributes(persistent_data=False):
                with mmap_file(path) as view:
                    loaded_info = retro_game_info(
                        os.fsencode(path), addressof_buffer(view), len(view), None
                    )
                    loaded_info_ext = _make_game_info_ext(loaded_info)
                    yield LoadedContentFile(loaded_info, loaded_info_ext)
                    # Content is not persistent, so just let the with statement clean up the view
            case (str() | PathLike()) as path, ContentAttributes(persistent_data=True):
                context = mmap_file(path)
                view = context.__enter__()
                loaded_info = retro_game_info(
                    os.fsencode(path), addressof_buffer(view), len(view), None
                )
                loaded_info_ext = _make_game_info_ext(loaded_info)
                self._persistent_buffers.add(
                    _PersistentBuffer(c_void_p(addressof_buffer(view)), context)
                )
                yield LoadedContentFile(loaded_info, loaded_info_ext)
                # Content is persistent, so the view (and backing file) will be cleaned up in __del__ later

            # For test cases that provide ROM data directly
            case bytes() | bytearray() | memoryview(), ContentAttributes(need_fullpath=True):
                raise ValueError("Core requires a full path, but only raw data was provided")
            case bytes(rom) | bytearray(rom) | memoryview(rom), ContentAttributes(
                persistent_data=persistent_data
            ):
                loaded_info = retro_game_info(None, addressof_buffer(rom), len(rom), None)
                loaded_info_ext = _make_game_info_ext(loaded_info)

                if persistent_data:
                    self._persistent_buffers.add(
                        _PersistentBuffer(c_void_p(loaded_info.data), None)
                    )

                yield LoadedContentFile(loaded_info, loaded_info_ext)

            # For test cases that provide no content for certain subsystems
            case None, ContentAttributes(required=False):
                # Optional subsystem content that isn't provided should be repesented as zeroed-out retro_game_infos
                # (Optional *regular* content is handled up in load())
                yield LoadedContentFile(retro_game_info(), retro_game_info_ext())
            case None, _:
                raise ContentError(
                    "No content provided and core did not indicate support for no game."
                )
            case e, _:
                raise TypeError(f"Unexpected content type: {type(e).__name__}")

        if not attributes.persistent_data:
            if loaded_info:
                loaded_info.data = None

            if loaded_info_ext:
                loaded_info_ext.data = None

    @property
    @override
    def system_info(self) -> retro_system_info | None:
        return self._system_info

    @system_info.setter
    @override
    def system_info(self, info: retro_system_info | None) -> None:
        self._system_info = info

    @property
    @override
    def subsystem_info(self) -> Subsystems | None:
        return self._subsystems

    @subsystem_info.setter
    @override
    def subsystem_info(self, subsystems: Sequence[retro_subsystem_info] | None) -> None:
        self._subsystems = Subsystems(subsystems) if subsystems else None

    @property
    @override
    def support_no_game(self) -> bool | None:
        return self._support_no_game

    @support_no_game.setter
    @override
    def support_no_game(self, support: bool) -> None:
        self._support_no_game = support

    @property
    @override
    def overrides(self) -> ContentInfoOverrides | None:
        return self._overrides

    @overrides.setter
    @override
    def overrides(self, overrides: Sequence[retro_system_content_info_override] | None) -> None:
        self._overrides = ContentInfoOverrides(overrides) if overrides else None

    def __needs_fullpath(
        self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None
    ) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        assert subsysrom is None or isinstance(subsysrom, retro_subsystem_rom_info)
        # These params should've been validated by the caller

        match ext, subsysrom, self._overrides:
            case None, _, _:
                # If loading any content from in-memory...
                return False
            case bytes(), _, ContentInfoOverrides() as overrides if ext in overrides:
                # If loading a content file with a specially-treated extension...
                overrides: ContentInfoOverrides
                return overrides[ext].need_fullpath
            case bytes(), None, _ if ext.removeprefix(b".") in self._system_info.extensions:
                # If loading a regular content file with no relevant overrides...
                return self._system_info.need_fullpath
            case bytes(), None, _:
                # No overrides were found, and the extension's not in the system info.
                raise ValueError(
                    f"Can't determine if regular content extension '{ext!r}' needs a full path (it's not in the overrides or system info)"
                )
            case bytes(), retro_subsystem_rom_info(), _:
                # If loading subsystem content with no relevant overrides, and the active subsystem is given directly...
                return subsysrom.need_fullpath
            case _, _, _:
                raise ValueError(
                    f"Can't determine if subsystem content extension '{ext!r}' needs a full path"
                )

    def __is_data_persistent(self, ext: bytes | None) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        # These params should've been validated by the caller

        match ext, self._overrides:
            case None, _:
                # If loading any content from in-memory...
                return True
            case bytes(ext), ContentInfoOverrides() as overrides if ext in overrides:
                # If loading a content file with a specially-treated extension...
                overrides: ContentInfoOverrides
                return overrides[ext].persistent_data
            case bytes(ext), _ if ext in self._system_info.extensions:
                # If loading a regular content file with no relevant overrides...
                return False  # Regular content is not guaranteed to be persistent
            case _, _:
                raise ValueError(
                    f"Can't determine if subsystem content extension '{ext!r}' has persistent data"
                )

    def __should_block_extract(
        self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None
    ) -> bool:
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
                raise ValueError(
                    f"Can't determine if subsystem content extension '{ext!r}' should block extraction"
                )

    def __is_required(
        self, ext: bytes | None, subsysrom: retro_subsystem_rom_info | None = None
    ) -> bool:
        assert self._system_info is not None
        assert ext is None or isinstance(ext, bytes)
        assert subsysrom is None or isinstance(subsysrom, retro_subsystem_rom_info)
        # These params should've been validated by the caller

        # NOTE: retro_content_info_override and retro_system_info do not have required,
        # but retro_system_info does use RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME

        match ext, subsysrom:
            case (None, _) | (_, None):
                # If loading any content from in-memory or if not using a subsystem...
                return not self._support_no_game
            case bytes(), retro_subsystem_rom_info():
                # If loading a subsystem ROM...
                overrides: ContentInfoOverrides
                return subsysrom.required
            case _, _:
                raise ValueError(
                    f"Can't determine if subsystem content extension '{ext!r}' is required"
                )

    def __get_subsystem(
        self, content: Content | SubsystemContent | None
    ) -> retro_subsystem_info | None:
        if not isinstance(content, SubsystemContent):
            return None

        if not self.subsystem_info:
            raise RuntimeError(
                "Subsystem content was provided, but core did not register subsystems"
            )

        match content.game_type:
            case int(id):
                for s in self.subsystem_info:
                    if s.id == id:
                        return s

                raise ValueError(f"Core did not register a subsystem with a numeric ID of {id}")

            case str(ident) | bytes(ident):
                return self.subsystem_info[ident]

            case e:
                raise TypeError(
                    f"Expected a subsystem identifier of types int, str, or bytes; got {type(e).__name__}"
                )


__all__ = [
    "StandardContentDriver",
]
