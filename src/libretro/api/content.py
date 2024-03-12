from ctypes import *

from ..retro import FieldsFromTypeHints


class retro_subsystem_memory_info(Structure, metaclass=FieldsFromTypeHints):
    extension: c_char_p
    type: c_uint


class retro_subsystem_rom_info(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    valid_extensions: c_char_p
    need_fullpath: c_bool
    block_extract: c_bool
    required: c_bool
    memory: POINTER(retro_subsystem_memory_info)
    num_memory: c_uint


class retro_subsystem_info(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    ident: c_char_p
    roms: POINTER(retro_subsystem_rom_info)
    num_roms: c_uint
    id: c_uint


class retro_system_content_info_override(Structure, metaclass=FieldsFromTypeHints):
    extensions: c_char_p
    need_fullpath: c_bool
    persistent_data: c_bool


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
