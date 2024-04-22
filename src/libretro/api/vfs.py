from copy import deepcopy
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    c_bool,
    c_char_p,
    c_int,
    c_int32,
    c_int64,
    c_uint,
    c_uint32,
    c_uint64,
    c_void_p,
    pointer,
)
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from os import PathLike

from libretro.api._utils import UNCHECKED, FieldsFromTypeHints

RETRO_VFS_FILE_ACCESS_READ = 1 << 0
RETRO_VFS_FILE_ACCESS_WRITE = 1 << 1
RETRO_VFS_FILE_ACCESS_READ_WRITE = RETRO_VFS_FILE_ACCESS_READ | RETRO_VFS_FILE_ACCESS_WRITE
RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING = 1 << 2

RETRO_VFS_FILE_ACCESS_HINT_NONE = 0
RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS = 1 << 0

RETRO_VFS_SEEK_POSITION_START = 0
RETRO_VFS_SEEK_POSITION_CURRENT = 1
RETRO_VFS_SEEK_POSITION_END = 2

RETRO_VFS_STAT_IS_VALID = 1 << 0
RETRO_VFS_STAT_IS_DIRECTORY = 1 << 1
RETRO_VFS_STAT_IS_CHARACTER_SPECIAL = 1 << 2


class retro_vfs_file_handle(Structure):
    pass


class retro_vfs_dir_handle(Structure):
    pass


class VfsFileAccess(IntFlag):
    READ = RETRO_VFS_FILE_ACCESS_READ
    WRITE = RETRO_VFS_FILE_ACCESS_WRITE
    READ_WRITE = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UPDATE_EXISTING = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING

    READ_WRITE_EXISTING = READ_WRITE | UPDATE_EXISTING

    def __init__(self, value: int):
        self._type_ = "I"

    @property
    def open_flag(self) -> str:
        match self:
            case VfsFileAccess.READ:
                return "rb"
            case VfsFileAccess.WRITE:
                return "wb"
            case VfsFileAccess.READ_WRITE:
                return "w+b"
            case VfsFileAccess.READ_WRITE_EXISTING:
                return "r+b"
            case _:
                raise ValueError(f"Invalid VfsFileAccess: {self}")


retro_vfs_get_path_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_file_handle))
retro_vfs_open_t = CFUNCTYPE(UNCHECKED(POINTER(retro_vfs_file_handle)), c_char_p, c_uint, c_uint)
retro_vfs_close_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_size_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_truncate_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64)
retro_vfs_tell_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_seek_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64, c_int)
retro_vfs_read_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_write_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_flush_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_remove_t = CFUNCTYPE(c_int, c_char_p)
retro_vfs_rename_t = CFUNCTYPE(c_int, c_char_p, c_char_p)
retro_vfs_stat_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_int32))
retro_vfs_mkdir_t = CFUNCTYPE(c_int, c_char_p)
retro_vfs_opendir_t = CFUNCTYPE(c_void_p, c_char_p, c_bool)
retro_vfs_readdir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_get_name_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_is_dir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_closedir_t = CFUNCTYPE(c_int, POINTER(retro_vfs_dir_handle))


@dataclass(init=False)
class retro_vfs_interface(Structure, metaclass=FieldsFromTypeHints):
    get_path: retro_vfs_get_path_t
    open: retro_vfs_open_t
    close: retro_vfs_close_t
    size: retro_vfs_size_t
    tell: retro_vfs_tell_t
    seek: retro_vfs_seek_t
    read: retro_vfs_read_t
    write: retro_vfs_write_t
    flush: retro_vfs_flush_t
    remove: retro_vfs_remove_t
    rename: retro_vfs_rename_t
    truncate: retro_vfs_truncate_t
    stat: retro_vfs_stat_t
    mkdir: retro_vfs_mkdir_t
    opendir: retro_vfs_opendir_t
    readdir: retro_vfs_readdir_t
    dirent_get_name: retro_vfs_dirent_get_name_t
    dirent_is_dir: retro_vfs_dirent_is_dir_t
    closedir: retro_vfs_closedir_t

    def __deepcopy__(self, _):
        return retro_vfs_interface(
            self.get_path,
            self.open,
            self.close,
            self.size,
            self.tell,
            self.seek,
            self.read,
            self.write,
            self.flush,
            self.remove,
            self.rename,
            self.truncate,
            self.stat,
            self.mkdir,
            self.opendir,
            self.readdir,
            self.dirent_get_name,
            self.dirent_is_dir,
            self.closedir,
        )


@dataclass(init=False)
class retro_vfs_interface_info(Structure, metaclass=FieldsFromTypeHints):
    required_interface_version: c_uint32
    iface: POINTER(retro_vfs_interface)

    def __deepcopy__(self, memo):
        return retro_vfs_interface_info(
            self.required_interface_version,
            pointer(deepcopy(self.iface[0], memo)) if self.iface else None,
        )


class VfsFileAccessHint(IntFlag):
    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS

    def __init__(self, value: int):
        self._type_ = "I"


class VfsSeekPosition(IntEnum):
    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END

    def __init__(self, value: int):
        self._type_ = "I"


class VfsStat(IntFlag):
    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL

    def __init__(self, value: int):
        self._type_ = "I"


class VfsMkdirResult(IntEnum):
    SUCCESS = 0
    ERROR = -1
    ALREADY_EXISTS = -2

    def __init__(self, value: int):
        self._type_ = "I"


VfsPath = bytes | str | PathLike

__all__ = [
    "retro_vfs_file_handle",
    "retro_vfs_dir_handle",
    "VfsFileAccess",
    "retro_vfs_get_path_t",
    "retro_vfs_open_t",
    "retro_vfs_close_t",
    "retro_vfs_size_t",
    "retro_vfs_truncate_t",
    "retro_vfs_tell_t",
    "retro_vfs_seek_t",
    "retro_vfs_read_t",
    "retro_vfs_write_t",
    "retro_vfs_flush_t",
    "retro_vfs_remove_t",
    "retro_vfs_rename_t",
    "retro_vfs_stat_t",
    "retro_vfs_mkdir_t",
    "retro_vfs_opendir_t",
    "retro_vfs_readdir_t",
    "retro_vfs_dirent_get_name_t",
    "retro_vfs_dirent_is_dir_t",
    "retro_vfs_closedir_t",
    "retro_vfs_interface",
    "retro_vfs_interface_info",
    "VfsFileAccessHint",
    "VfsSeekPosition",
    "VfsStat",
    "VfsMkdirResult",
    "VfsPath",
]
