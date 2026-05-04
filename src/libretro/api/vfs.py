"""
Virtual filesystem (VFS) interface types and callbacks.

.. seealso::

    :class:`.FileSystemDriver`
        The :class:`~typing.Protocol` that uses these types to implement VFS support in libretro.py.

    :mod:`libretro.drivers.vfs`
        libretro.py's included :class:`.FileSystemDriver` implementations.
"""

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
from typing import Literal

from libretro.ctypes import (
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


@dataclass(slots=True)
class retro_vfs_file_handle(Structure):
    """
    Opaque handle for an open VFS file.

    Corresponds to :c:type:`retro_vfs_file_handle` in ``libretro.h``.

    .. note::

        Unlike most other :mod:`ctypes`-wrapped ``struct``s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.FileSystemDriver` implementations.

        :class:`.Core`\\s should treat instances of this class as opaque handles
        and _not_ access or modify its fields directly.


    .. seealso::
        :meth:`.FileSystemDriver.open`
            The suggested method for creating instances of this class.
    """

    id: int
    """
    Opaque identifier for this file handle.
    The :class:`.FileSystemDriver` that creates this handle can assign any value,
    but it should be unique among opened files.
    """

    path: bytes | None
    """Path that was used to open this file."""

    mode: int
    """
    File access mode flags.

    .. seealso::
        :class:`.VfsFileAccess`
            The flags that can be set in this field.
    """

    hints: int
    """
    File access hint flags.

    .. seealso::
        :class:`.VfsFileAccessHint`
            The flags that can be set in this field.
    """

    _fields_ = (
        ("id", c_uint64),
        ("path", c_char_p),
        ("mode", c_uint),
        ("hints", c_uint),
    )

    def __init__(self, id: int, path: bytes | None, mode: int, hints: int):
        self.id = id
        self.path = path
        self.mode = mode
        self.hints = hints


@dataclass(init=False, slots=True)
class retro_vfs_dir_handle(Structure):
    """
    Opaque handle for an open VFS directory.

    Corresponds to :c:type:`retro_vfs_dir_handle` in ``libretro.h``.

    .. note::
        Unlike most other :mod:`ctypes`-wrapped ``struct``s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.FileSystemDriver` implementations.

        :class:`.Core`\\s should treat instances of this class as opaque handles
        and _not_ access or modify its fields directly.

    .. seealso::
        :meth:`.FileSystemDriver.opendir`
            The method that creates instances of this class.
    """

    id: int
    """
    Opaque identifier for this directory handle.
    The :class:`.FileSystemDriver` that creates this handle can assign any value,
    but it should be unique among opened directories.
    """

    dir: bytes | None
    """Path to the open directory."""

    include_hidden: bool
    """
    Whether hidden entries are included when enumerating the directory's contents.
    """

    _fields_ = (
        ("id", c_uint64),
        ("dir", c_char_p),
        ("include_hidden", c_bool),
    )


class VfsFileAccess(IntFlag):
    """
    File access mode flags for VFS operations.

    Corresponds to the ``RETRO_VFS_FILE_ACCESS_*`` constants in ``libretro.h``.

    >>> from libretro.api import VfsFileAccess
    >>> VfsFileAccess.READ
    <VfsFileAccess.READ: 1>
    """

    READ = RETRO_VFS_FILE_ACCESS_READ
    WRITE = RETRO_VFS_FILE_ACCESS_WRITE
    READ_WRITE = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UPDATE_EXISTING = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING

    READ_WRITE_EXISTING = READ_WRITE | UPDATE_EXISTING

    @property
    def open_flag(self) -> Literal["rb", "wb", "w+b", "r+b"]:
        """Returns the Python :func:`open` mode string for this access mode.

        >>> from libretro.api import VfsFileAccess
        >>> VfsFileAccess.READ.open_flag
        'rb'
        """
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
"""Returns the path of an open file handle."""

retro_vfs_open_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_file_handle], [CStringArg, CIntArg[c_uint], CIntArg[c_uint]]
]
"""Opens a file with the given path, mode, and hints."""

retro_vfs_close_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
"""Closes an open file handle."""

retro_vfs_size_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
"""Returns the size of an open file."""

retro_vfs_truncate_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64]]
]
"""Truncates an open file to the given length."""

retro_vfs_tell_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
"""Returns the current position in an open file."""

retro_vfs_seek_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64], CIntArg[c_int]]
]
"""Seeks to a position in an open file."""

retro_vfs_read_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
"""Reads data from an open file."""

retro_vfs_write_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
"""Writes data to an open file."""

retro_vfs_flush_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
"""Flushes pending writes to an open file."""

retro_vfs_remove_t = TypedFunctionPointer[c_int, [CStringArg]]
"""Removes a file at the given path."""

retro_vfs_rename_t = TypedFunctionPointer[c_int, [CStringArg, CStringArg]]
"""Renames a file from one path to another."""

retro_vfs_stat_t = TypedFunctionPointer[c_int, [CStringArg, TypedPointer[c_int32]]]
"""Stats a path and returns flags and optionally the file size."""

retro_vfs_mkdir_t = TypedFunctionPointer[c_int, [CStringArg]]
"""Creates a directory at the given path."""

retro_vfs_opendir_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_dir_handle], [CStringArg, CBoolArg]
]
"""Opens a directory for iteration."""

retro_vfs_readdir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
"""Advances the directory iterator to the next entry."""

retro_vfs_dirent_get_name_t = TypedFunctionPointer[c_char_p, [TypedPointer[retro_vfs_dir_handle]]]
"""Returns the name of the current directory entry."""

retro_vfs_dirent_is_dir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
"""Returns whether the current directory entry is a subdirectory."""

retro_vfs_closedir_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_dir_handle]]]
"""Closes an open directory handle."""


@dataclass(init=False, slots=True)
class retro_vfs_interface(Structure):
    """Corresponds to :c:type:`retro_vfs_interface` in ``libretro.h``.

    A complete set of callbacks for virtual filesystem operations.

    >>> from libretro.api import retro_vfs_interface
    >>> vfs = retro_vfs_interface()
    >>> vfs.open is None
    True
    """

    get_path: retro_vfs_get_path_t | None
    """Returns the path of an open file handle."""
    open: retro_vfs_open_t | None
    """Opens a file with the given path, mode, and hints."""
    close: retro_vfs_close_t | None
    """Closes an open file handle."""
    size: retro_vfs_size_t | None
    """Returns the size of an open file in bytes."""
    tell: retro_vfs_tell_t | None
    """Returns the current read/write position."""
    seek: retro_vfs_seek_t | None
    """Sets the current read/write position."""
    read: retro_vfs_read_t | None
    """Reads data from an open file."""
    write: retro_vfs_write_t | None
    """Writes data to an open file."""
    flush: retro_vfs_flush_t | None
    """Flushes pending writes to an open file."""
    remove: retro_vfs_remove_t | None
    """Deletes a file at the given path."""
    rename: retro_vfs_rename_t | None
    """Renames a file from one path to another."""
    truncate: retro_vfs_truncate_t | None
    """Sets an open file's length."""
    stat: retro_vfs_stat_t | None
    """Gets status flags and size of a file."""
    mkdir: retro_vfs_mkdir_t | None
    """Creates a directory at the given path."""
    opendir: retro_vfs_opendir_t | None
    """Opens a directory for iteration."""
    readdir: retro_vfs_readdir_t | None
    """Advances to the next directory entry."""
    dirent_get_name: retro_vfs_dirent_get_name_t | None
    """Returns the name of the current directory entry."""
    dirent_is_dir: retro_vfs_dirent_is_dir_t | None
    """Returns whether the current directory entry is a subdirectory."""
    closedir: retro_vfs_closedir_t | None
    """Closes an open directory handle."""

    _fields_ = (
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
    )

    def __deepcopy__(self, _):
        """Returns a shallow copy."""
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


@dataclass(init=False, slots=True)
class retro_vfs_interface_info(Structure):
    """Corresponds to :c:type:`retro_vfs_interface_info` in ``libretro.h``.

    Wraps a :class:`retro_vfs_interface` pointer with a version number.

    >>> from libretro.api import retro_vfs_interface_info
    >>> info = retro_vfs_interface_info()
    >>> info.required_interface_version
    0
    """

    required_interface_version: int
    """Minimum VFS API version required by the core."""
    iface: TypedPointer[retro_vfs_interface] | Pointer[retro_vfs_interface] | None
    """VFS interface provided by the frontend."""

    _fields_ = (
        ("required_interface_version", c_uint32),
        ("iface", POINTER(retro_vfs_interface)),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """
        Returns a deep copy of this object, including all subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_vfs_interface_info(
            self.required_interface_version,
            pointer(deepcopy(self.iface[0], memo)) if self.iface else None,
        )


class VfsFileAccessHint(IntFlag):
    """Hints for file access patterns.

    >>> from libretro.api import VfsFileAccessHint
    >>> VfsFileAccessHint.FREQUENT_ACCESS
    <VfsFileAccessHint.FREQUENT_ACCESS: 1>
    """

    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS


class VfsSeekPosition(IntEnum):
    """Seek origin for VFS seek operations.

    >>> from libretro.api import VfsSeekPosition
    >>> VfsSeekPosition.START
    <VfsSeekPosition.START: 0>
    """

    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END


class VfsStat(IntFlag):
    """Flags returned by VFS stat operations.

    >>> from libretro.api import VfsStat
    >>> VfsStat.IS_DIRECTORY
    <VfsStat.IS_DIRECTORY: 2>
    """

    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL


class VfsMkdirResult(IntEnum):
    """Return codes for VFS mkdir operations.

    >>> from libretro.api import VfsMkdirResult
    >>> VfsMkdirResult.SUCCESS
    <VfsMkdirResult.SUCCESS: 0>
    """

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
