from collections.abc import Sequence
from ctypes import *
from dataclasses import dataclass
from os import PathLike
from typing import TypeAlias, NamedTuple, overload

from .._utils import FieldsFromTypeHints, deepcopy_array, deepcopy_buffer


@dataclass(init=False)
class retro_game_info(Structure, metaclass=FieldsFromTypeHints):
    path: c_char_p
    data: c_void_p
    size: c_size_t
    meta: c_char_p

    def __deepcopy__(self, _):
        return retro_game_info(
            path=bytes(self.path) if self.path else None,
            data=deepcopy_buffer(self.data, self.size),
            size=self.size,
            meta=bytes(self.meta) if self.meta else None
        )


Content: TypeAlias = str | bytes | PathLike | retro_game_info


class SubsystemContent(NamedTuple):
    game_type: int | str | bytes
    info: Sequence[Content]


@dataclass(init=False)
class retro_subsystem_memory_info(Structure, metaclass=FieldsFromTypeHints):
    extension: c_char_p
    type: c_uint

    def __deepcopy__(self, _):
        return retro_subsystem_memory_info(
            extension=bytes(self.extension) if self.extension else None,
            type=self.type
        )


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
        return int(self.num_types)

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
            desc=bytes(self.desc) if self.desc else None,
            valid_extensions=bytes(self.valid_extensions) if self.valid_extensions else None,
            need_fullpath=self.need_fullpath,
            block_extract=self.block_extract,
            required=self.required,
            memory=deepcopy_array(self.memory, self.num_memory, memo) if self.memory else None,
            num_memory=self.num_memory
        )


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
            desc=bytes(self.desc) if self.desc else None,
            ident=bytes(self.ident) if self.ident else None,
            roms=deepcopy_array(self.roms, self.num_roms, memo) if self.roms else None,
            num_roms=self.num_roms,
            id=self.id
        )


@dataclass(init=False)
class retro_system_content_info_override(Structure, metaclass=FieldsFromTypeHints):
    extensions: c_char_p
    need_fullpath: c_bool
    persistent_data: c_bool

    def __deepcopy__(self, _):
        return retro_system_content_info_override(
            extensions=bytes(self.extensions) if self.extensions else None,
            need_fullpath=self.need_fullpath,
            persistent_data=self.persistent_data
        )


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
            full_path=bytes(self.full_path) if self.full_path else None,
            archive_path=bytes(self.archive_path) if self.archive_path else None,
            archive_file=bytes(self.archive_file) if self.archive_file else None,
            dir=bytes(self.dir) if self.dir else None,
            name=bytes(self.name) if self.name else None,
            ext=bytes(self.ext) if self.ext else None,
            meta=bytes(self.meta) if self.meta else None,
            data=deepcopy_buffer(self.data, self.size),
            size=self.size,
            file_in_archive=self.file_in_archive,
            persistent_data=self.persistent_data
        )


__all__ = [
    'Content',
    'SubsystemContent',
    'retro_game_info',
    'retro_subsystem_memory_info',
    'retro_subsystem_rom_info',
    'retro_subsystem_info',
    'retro_system_content_info_override',
    'retro_game_info_ext'
]
