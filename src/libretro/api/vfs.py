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
from typing import TYPE_CHECKING

from _utils import MemoDict

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


if TYPE_CHECKING:
    from libretro.typing import FrontendFunctionPointer, Pointer

    retro_vfs_get_path_t = FrontendFunctionPointer[c_char_p, [Pointer[retro_vfs_file_handle]]]
    retro_vfs_open_t = FrontendFunctionPointer[
        Pointer[retro_vfs_file_handle], [c_char_p, c_uint, c_uint]
    ]
    retro_vfs_close_t = FrontendFunctionPointer[c_int, [Pointer[retro_vfs_file_handle]]]
    retro_vfs_size_t = FrontendFunctionPointer[c_int64, [Pointer[retro_vfs_file_handle]]]
    retro_vfs_truncate_t = FrontendFunctionPointer[
        c_int64, [Pointer[retro_vfs_file_handle], c_int64]
    ]
    retro_vfs_tell_t = FrontendFunctionPointer[c_int64, [Pointer[retro_vfs_file_handle]]]
    retro_vfs_seek_t = FrontendFunctionPointer[
        c_int64, [Pointer[retro_vfs_file_handle], c_int64, c_int]
    ]
    retro_vfs_read_t = FrontendFunctionPointer[
        c_int64, [Pointer[retro_vfs_file_handle], c_void_p, c_uint64]
    ]
    retro_vfs_write_t = FrontendFunctionPointer[
        c_int64, [Pointer[retro_vfs_file_handle], c_void_p, c_uint64]
    ]
    retro_vfs_flush_t = FrontendFunctionPointer[c_int, [Pointer[retro_vfs_file_handle]]]
    retro_vfs_remove_t = FrontendFunctionPointer[c_int, [c_char_p]]
    retro_vfs_rename_t = FrontendFunctionPointer[c_int, [c_char_p, c_char_p]]
    retro_vfs_stat_t = FrontendFunctionPointer[c_int, [c_char_p, Pointer[c_int32]]]
    retro_vfs_mkdir_t = FrontendFunctionPointer[c_int, [c_char_p]]
    retro_vfs_opendir_t = FrontendFunctionPointer[c_void_p, [c_char_p, c_bool]]
    retro_vfs_readdir_t = FrontendFunctionPointer[c_bool, [Pointer[retro_vfs_dir_handle]]]
    retro_vfs_dirent_get_name_t = FrontendFunctionPointer[
        c_char_p, [Pointer[retro_vfs_dir_handle]]
    ]
    retro_vfs_dirent_is_dir_t = FrontendFunctionPointer[c_bool, [Pointer[retro_vfs_dir_handle]]]
    retro_vfs_closedir_t = FrontendFunctionPointer[c_int, [Pointer[retro_vfs_dir_handle]]]
else:
    retro_vfs_get_path_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_file_handle))
    retro_vfs_open_t = CFUNCTYPE(POINTER(retro_vfs_file_handle), c_char_p, c_uint, c_uint)
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


@dataclass(init=False, slots=True)
class retro_vfs_interface(Structure):
    if TYPE_CHECKING:
        get_path: retro_vfs_get_path_t | None
        open: retro_vfs_open_t | None
        close: retro_vfs_close_t | None
        size: retro_vfs_size_t | None
        tell: retro_vfs_tell_t | None
        seek: retro_vfs_seek_t | None
        read: retro_vfs_read_t | None
        write: retro_vfs_write_t | None
        flush: retro_vfs_flush_t | None
        remove: retro_vfs_remove_t | None
        rename: retro_vfs_rename_t | None
        truncate: retro_vfs_truncate_t | None
        stat: retro_vfs_stat_t | None
        mkdir: retro_vfs_mkdir_t | None
        opendir: retro_vfs_opendir_t | None
        readdir: retro_vfs_readdir_t | None
        dirent_get_name: retro_vfs_dirent_get_name_t | None
        dirent_is_dir: retro_vfs_dirent_is_dir_t | None
        closedir: retro_vfs_closedir_t | None
    else:
        _fields_ = [
            ("get_path", retro_vfs_get_path_t),
            ("open", retro_vfs_open_t),
            ("close", retro_vfs_close_t),
            ("size", retro_vfs_size_t),
            ("tell", retro_vfs_tell_t),
            ("seek", retro_vfs_seek_t),
            ("read", retro_vfs_read_t),
            ("write", retro_vfs_write_t),
            ("flush", retro_vfs_flush_t),
            ("remove", retro_vfs_remove_t),
            ("rename", retro_vfs_rename_t),
            ("truncate", retro_vfs_truncate_t),
            ("stat", retro_vfs_stat_t),
            ("mkdir", retro_vfs_mkdir_t),
            ("opendir", retro_vfs_opendir_t),
            ("readdir", retro_vfs_readdir_t),
            ("dirent_get_name", retro_vfs_dirent_get_name_t),
            ("dirent_is_dir", retro_vfs_dirent_is_dir_t),
            ("closedir", retro_vfs_closedir_t),
        ]

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
class retro_vfs_interface_info(Structure):
    if TYPE_CHECKING:
        required_interface_version: int
        iface: Pointer[retro_vfs_interface] | None
    else:
        _fields_ = [
            ("required_interface_version", c_uint32),
            ("iface", POINTER(retro_vfs_interface)),
        ]

    def __deepcopy__(self, memo: MemoDict = None):
        return retro_vfs_interface_info(
            self.required_interface_version,
            pointer(deepcopy(self.iface[0], memo)) if self.iface else None,
        )


class VfsFileAccessHint(IntFlag):
    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS


class VfsSeekPosition(IntEnum):
    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END


class VfsStat(IntFlag):
    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL


class VfsMkdirResult(IntEnum):
    SUCCESS = 0
    ERROR = -1
    ALREADY_EXISTS = -2


VfsPath = bytes | str | PathLike[bytes] | PathLike[str]

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
