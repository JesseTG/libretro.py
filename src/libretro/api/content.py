import os
from collections.abc import Generator, Iterator, Mapping, Sequence
from contextlib import contextmanager
from ctypes import (
    POINTER,
    Array,
    Structure,
    addressof,
    c_bool,
    c_char_p,
    c_size_t,
    c_ubyte,
    c_uint,
    c_void_p,
)
from dataclasses import dataclass
from os import PathLike
from types import MappingProxyType
from typing import Any, NamedTuple, TypeAlias, overload
from zipfile import Path as ZipPath

from libretro._typing import Buffer
from libretro.api._utils import (
    FieldsFromTypeHints,
    as_bytes,
    deepcopy_array,
    deepcopy_buffer,
    mmap_file,
)


@dataclass(init=False)
class retro_system_info(Structure, metaclass=FieldsFromTypeHints):
    library_name: c_char_p
    library_version: c_char_p
    valid_extensions: c_char_p
    need_fullpath: c_bool
    block_extract: c_bool

    def __deepcopy__(self, _):
        return retro_system_info(
            library_name=self.library_name,
            library_version=self.library_version,
            valid_extensions=self.valid_extensions,
            need_fullpath=self.need_fullpath,
            block_extract=self.block_extract,
        )

    @property
    def extensions(self) -> Iterator[bytes]:
        if self.valid_extensions:
            yield from self.valid_extensions.split(b"|")


@dataclass(init=False)
class retro_game_info(Structure, metaclass=FieldsFromTypeHints):
    path: c_char_p
    data: c_void_p
    size: c_size_t
    meta: c_char_p

    def __deepcopy__(self, _):
        return retro_game_info(
            path=self.path,
            data=deepcopy_buffer(self.data, self.size),
            size=self.size,
            meta=self.meta,
        )


ContentPath = str | PathLike | ZipPath
ContentData = bytes | bytearray | memoryview | Buffer
Content: TypeAlias = ContentPath | ContentData | retro_game_info


class SubsystemContent(NamedTuple):
    game_type: int | str | bytes
    info: Sequence[Content]


@dataclass(init=False)
class retro_subsystem_memory_info(Structure, metaclass=FieldsFromTypeHints):
    extension: c_char_p
    type: c_uint

    def __deepcopy__(self, _):
        return retro_subsystem_memory_info(self.extension, self.type)


@dataclass(init=False)
class retro_subsystem_rom_info(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    valid_extensions: c_char_p
    need_fullpath: c_bool
    block_extract: c_bool
    required: c_bool
    memory: POINTER(retro_subsystem_memory_info)
    num_memory: c_uint

    def __len__(self):
        return int(self.num_memory)

    @overload
    def __getitem__(self, index: int) -> retro_subsystem_memory_info: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[retro_subsystem_memory_info]: ...

    def __getitem__(self, index):
        if not self.memory:
            raise ValueError("No subsystem ROM memory types available")

        match index:
            case int(i):
                if not (0 <= i < self.num_memory):
                    raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
                return self.memory[i]

            case slice() as s:
                s: slice
                return self.memory[s]

            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __deepcopy__(self, memo):
        return retro_subsystem_rom_info(
            desc=self.desc,
            valid_extensions=self.valid_extensions,
            need_fullpath=self.need_fullpath,
            block_extract=self.block_extract,
            required=self.required,
            memory=(deepcopy_array(self.memory, self.num_memory, memo) if self.memory else None),
            num_memory=self.num_memory,
        )

    @property
    def extensions(self) -> Iterator[bytes]:
        if self.valid_extensions:
            yield from self.valid_extensions.split(b"|")


@dataclass(init=False)
class retro_subsystem_info(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    ident: c_char_p
    roms: POINTER(retro_subsystem_rom_info)
    num_roms: c_uint
    id: c_uint

    def __len__(self):
        return int(self.num_roms)

    @overload
    def __getitem__(self, index: int) -> retro_subsystem_rom_info: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[retro_subsystem_rom_info]: ...

    def __getitem__(self, index):
        if not self.roms:
            raise ValueError("No subsystem ROM types available")

        match index:
            case int(i):
                if not (0 <= i < self.num_roms):
                    raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
                return self.roms[i]

            case slice() as s:
                s: slice
                return self.roms[s]

            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __deepcopy__(self, memo):
        return retro_subsystem_info(
            desc=self.desc,
            ident=self.ident,
            roms=deepcopy_array(self.roms, self.num_roms, memo) if self.roms else None,
            num_roms=self.num_roms,
            id=self.id,
        )

    @property
    def extensions(self) -> Iterator[bytes]:
        for rom in self:
            yield from rom.extensions

    @property
    def by_extensions(self) -> Iterator[tuple[bytes, retro_subsystem_rom_info]]:
        for info in self:
            for ext in info.extensions:
                yield ext, info

    def by_extension(self, ext: str | bytes) -> retro_subsystem_rom_info:
        ext = as_bytes(ext).removeprefix(b".")
        for info in self:
            if ext in info.extensions:
                return info

        raise KeyError(f"Subsystem ROM with extension {ext!r} not found")


class Subsystems(Sequence[retro_subsystem_info]):
    def __init__(self, subsystems: Sequence[retro_subsystem_info]):
        if not isinstance(subsystems, Sequence):
            raise TypeError(
                f"Expected a sequence of retro_subsystem_info objects, got {type(subsystems).__name__}"
            )

        if not all(isinstance(subsystem, retro_subsystem_info) for subsystem in subsystems):
            raise TypeError("All elements in the sequence must be retro_subsystem_info objects")

        self._subsystems = tuple(subsystems)
        self._subsystems_by_ident = {bytes(subsystem.ident): subsystem for subsystem in subsystems}

    def __getitem__(self, item: int | str | bytes) -> retro_subsystem_info:
        length = len(self._subsystems)
        match item:
            case int() if -length <= item < length:
                return self._subsystems[item]
            case int():
                raise IndexError(f"Expected {-length} <= index < {length}, got {item}")
            case str() | bytes():
                ident = as_bytes(item)
                if ident in self._subsystems_by_ident:
                    return self._subsystems_by_ident[ident]

                raise KeyError(f"Subsystem with identifier {item!r} not found")
            case _:
                raise TypeError(f"Expected an int, str, or bytes; got {type(item).__name__}")

    def __contains__(self, item: str | bytes | retro_subsystem_info):
        match item:
            case str(ident) | bytes(ident):
                return as_bytes(ident) in self._subsystems_by_ident
            case retro_subsystem_info():
                return item in self._subsystems
            case _:
                raise TypeError(
                    f"Expected a str, bytes, or retro_subsystem_info object; got {type(item).__name__}"
                )

    def __iter__(self):
        return iter(self._subsystems)

    def __len__(self):
        return len(self._subsystems)


@dataclass(init=False)
class retro_system_content_info_override(Structure, metaclass=FieldsFromTypeHints):
    extensions: c_char_p
    need_fullpath: c_bool
    persistent_data: c_bool

    def __deepcopy__(self, _):
        return retro_system_content_info_override(
            extensions=self.extensions,
            need_fullpath=self.need_fullpath,
            persistent_data=self.persistent_data,
        )

    def get_extensions(self) -> Iterator[bytes]:
        if self.extensions:
            yield from self.extensions.split(b"|")


class ContentInfoOverrides(Sequence[retro_system_content_info_override]):
    def __init__(self, overrides: Sequence[retro_system_content_info_override]):
        if not isinstance(overrides, Sequence):
            raise TypeError(
                f"Expected a sequence of retro_system_content_info_override objects, got {type(overrides).__name__}"
            )

        if not all(
            isinstance(override, retro_system_content_info_override) for override in overrides
        ):
            raise TypeError(
                "All elements in the sequence must be retro_system_content_info_override objects"
            )

        self._overrides = tuple(overrides)
        overrides_by_ext: dict[bytes, retro_system_content_info_override] = {}
        for o in self._overrides:
            for e in o.get_extensions():
                if e not in overrides_by_ext:
                    # If this isn't a duplicate override...
                    overrides_by_ext[e] = o
                    # If an extension is listed more than once in a RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE call,
                    # only the first occurrence is used.

        self._overrides_by_ext = MappingProxyType(overrides_by_ext)

    def __getitem__(self, item: int | slice | str | bytes) -> retro_system_content_info_override:
        match item:
            case int() if -len(self) <= item < len(self):
                return self._overrides[item]
            case int():
                raise IndexError(f"Expected {-len(self)} <= index < {len(self)}, got {item}")
            case slice() as s:
                return self._overrides[s]
            case str() | bytes():
                ext = as_bytes(item).removeprefix(b".")
                if ext in self._overrides_by_ext:
                    return self._overrides_by_ext[ext]

                raise KeyError(f"Override for extension {item!r} not found")
            case _:
                raise TypeError(f"Expected an int, str, or bytes; got {type(item).__name__}")

    def __contains__(self, item: str | bytes | retro_system_content_info_override) -> bool:
        """
        Tests if the given item is in the overrides list.

        :param item: The item to test.
            If a ``retro_system_content_info_override`` object, looks for an exact match.
            If a ``str`` or ``bytes`` object,
            looks for a ``retro_system_content_info_override`` with a matching extension.
        """
        match item:
            case str(ext) | bytes(ext):
                return as_bytes(ext).removeprefix(b".") in self._overrides_by_ext
            case retro_system_content_info_override():
                return item in self._overrides
            case _:
                raise TypeError(
                    f"Expected a str, bytes, or retro_system_content_info_override object; got {type(item).__name__}"
                )

    def __iter__(self):
        return iter(self._overrides)

    def __len__(self):
        return len(self._overrides)

    @property
    def by_extension(self) -> Mapping[bytes, retro_system_content_info_override]:
        return self._overrides_by_ext


@dataclass(init=False)
class retro_game_info_ext(Structure, metaclass=FieldsFromTypeHints):
    full_path: c_char_p
    archive_path: c_char_p
    archive_file: c_char_p
    dir: c_char_p
    name: c_char_p
    ext: c_char_p
    meta: c_char_p
    data: c_void_p
    size: c_size_t
    file_in_archive: c_bool
    persistent_data: c_bool

    def __deepcopy__(self, _):
        return retro_game_info_ext(
            full_path=self.full_path,
            archive_path=self.archive_path,
            archive_file=self.archive_file,
            dir=self.dir,
            name=self.name,
            ext=self.ext,
            meta=self.meta,
            data=deepcopy_buffer(self.data, self.size),
            size=self.size,
            file_in_archive=self.file_in_archive,
            persistent_data=self.persistent_data,
        )


@contextmanager
def map_content(
    content: Content | None,
) -> Generator[retro_game_info | None, Any, None]:
    match content:
        case None:
            yield None
        case retro_game_info() as info:
            yield info
        case retro_game_info_ext() as info_ext:
            yield retro_game_info(
                path=info_ext.full_path,
                data=info_ext.data,
                size=info_ext.size,
                meta=info_ext.meta,
            )
        case str(path) | PathLike(path):
            with mmap_file(path) as contentview:
                # noinspection PyTypeChecker
                # You can't directly get an address from a memoryview,
                # so you need to resort to C-like casting
                array_type: type[Array] = c_ubyte * len(contentview)
                buffer_array = array_type.from_buffer(contentview)

                info = retro_game_info(
                    path.encode(), addressof(buffer_array), len(contentview), None
                )
                yield info
                del info
                del buffer_array
                del array_type
                # Need to clear all outstanding pointers, or else mmap will raise a BufferError
        case bytes(data) | bytearray(data) | memoryview(data):
            # noinspection PyTypeChecker
            array_type: type[Array] = c_ubyte * len(data)
            buffer_array = array_type.from_buffer(data)
            yield retro_game_info(data=addressof(buffer_array), size=len(data))
        case _:
            raise TypeError(
                f"Expected a content path, data, or retro_game_info object, got {type(content).__name__}"
            )


def get_extension(content: Content | retro_game_info_ext) -> bytes | None:
    match content:
        case ZipPath() as zippath:
            zippath: ZipPath
            return zippath.suffix.encode().removeprefix(b".")
        case str() | PathLike() as path:
            _, e = os.path.splitext(os.fsencode(path))
            return e.removeprefix(b".")
        case bytes() | bytearray() | memoryview() | retro_game_info(path=None):
            return None
        case retro_game_info(path=path):
            _, ext = os.path.splitext(path)
            return ext.removeprefix(b".")
        case retro_game_info_ext():
            return content.ext
        case _:
            raise TypeError(
                f"Expected a str, path-like, buffer, retro_game_info, or retro_game_info_ext object; got {type(content).__name__}"
            )


__all__ = [
    "retro_system_info",
    "Content",
    "ContentData",
    "ContentPath",
    "SubsystemContent",
    "retro_game_info",
    "retro_subsystem_memory_info",
    "retro_subsystem_rom_info",
    "retro_subsystem_info",
    "retro_system_content_info_override",
    "retro_game_info_ext",
    "map_content",
    "get_extension",
    "Subsystems",
    "ContentInfoOverrides",
]
