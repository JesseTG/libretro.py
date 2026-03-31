from copy import deepcopy
from ctypes import (
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
    pointer,
)
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from os import PathLike
from typing import TYPE_CHECKING, Literal

from libretro.typing import (
    CBoolArg,
    CIntArg,
    CStringArg,
    Pointer,
    TypedFunctionPointer,
    TypedPointer,
    c_void_ptr,
)

from ._utils import MemoDict

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


@dataclass(init=False, slots=True)
class retro_vfs_file_handle(Structure):
    if TYPE_CHECKING:
        id: int
    else:
        _fields_ = [("id", c_uint64)]


@dataclass(init=False, slots=True)
class retro_vfs_dir_handle(Structure):
    if TYPE_CHECKING:
        id: int
    else:
        _fields_ = [("id", c_uint64)]


class VfsFileAccess(IntFlag):
    READ = RETRO_VFS_FILE_ACCESS_READ
    WRITE = RETRO_VFS_FILE_ACCESS_WRITE
    READ_WRITE = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UPDATE_EXISTING = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING

    READ_WRITE_EXISTING = READ_WRITE | UPDATE_EXISTING

    @property
    def open_flag(self) -> Literal["rb", "wb", "w+b", "r+b"]:
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


retro_vfs_get_path_t = TypedFunctionPointer[c_char_p, [TypedPointer[retro_vfs_file_handle]]]
retro_vfs_open_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_file_handle], [CStringArg, CIntArg[c_uint], CIntArg[c_uint]]
]
retro_vfs_close_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
retro_vfs_size_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
retro_vfs_truncate_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64]]
]
retro_vfs_tell_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
retro_vfs_seek_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64], CIntArg[c_int]]
]
retro_vfs_read_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
retro_vfs_write_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
retro_vfs_flush_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
retro_vfs_remove_t = TypedFunctionPointer[c_int, [CStringArg]]
retro_vfs_rename_t = TypedFunctionPointer[c_int, [CStringArg, CStringArg]]
retro_vfs_stat_t = TypedFunctionPointer[c_int, [CStringArg, TypedPointer[c_int32]]]
retro_vfs_mkdir_t = TypedFunctionPointer[c_int, [CStringArg]]
retro_vfs_opendir_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_dir_handle], [CStringArg, CBoolArg]
]
retro_vfs_readdir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
retro_vfs_dirent_get_name_t = TypedFunctionPointer[c_char_p, [TypedPointer[retro_vfs_dir_handle]]]
retro_vfs_dirent_is_dir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
retro_vfs_closedir_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_dir_handle]]]


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
        iface: TypedPointer[retro_vfs_interface] | Pointer[retro_vfs_interface] | None

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
