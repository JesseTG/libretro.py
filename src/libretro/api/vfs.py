"""
Virtual filesystem (VFS) interface types and callbacks.

.. seealso::

    :class:`.FileSystemDriver`
        The :class:`~typing.Protocol` that uses these types to implement VFS support in libretro.py.

    :mod:`libretro.drivers.vfs`
        libretro.py's included :class:`.FileSystemDriver` implementations.
"""

from collections.abc import Iterator, Sequence
from copy import deepcopy
from ctypes import (
    POINTER,
    Array,
    Structure,
    c_bool,
    c_char_p,
    c_int,
    c_int32,
    c_int64,
    c_size_t,
    c_uint,
    c_uint32,
    c_uint64,
    pointer,
)
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from os import PathLike
from typing import Literal, overload

from libretro.ctypes import (
    CBoolArg,
    CIntArg,
    CStringArg,
    Pointer,
    TypedArray,
    TypedFunctionPointer,
    TypedPointer,
    c_void_ptr,
)

from ._utils import MemoDict, NullPointerToNoneMixin, deepcopy_array

RETRO_VFS_FILE_ACCESS_READ = 1 << 0
RETRO_VFS_FILE_ACCESS_WRITE = 1 << 1
RETRO_VFS_FILE_ACCESS_READ_WRITE = RETRO_VFS_FILE_ACCESS_READ | RETRO_VFS_FILE_ACCESS_WRITE
RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING = 1 << 2

RETRO_VFS_FILE_ACCESS_HINT_NONE = 0
RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS = 1 << 0
RETRO_VFS_FILE_ACCESS_HINT_SEQUENTIAL_BULK = 1 << 1

RETRO_VFS_SEEK_POSITION_START = 0
RETRO_VFS_SEEK_POSITION_CURRENT = 1
RETRO_VFS_SEEK_POSITION_END = 2

RETRO_VFS_STAT_IS_VALID = 1 << 0
RETRO_VFS_STAT_IS_DIRECTORY = 1 << 1
RETRO_VFS_STAT_IS_CHARACTER_SPECIAL = 1 << 2


@dataclass(slots=True)
class retro_vfs_file_handle(Structure):
    r"""
    Opaque handle for an open VFS file.

    Corresponds to :c:type:`retro_vfs_file_handle` in ``libretro.h``.

    .. note::

        Unlike most other :mod:`ctypes`-wrapped ``struct``\s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.FileSystemDriver` implementations.

        :term:`Core <core>`\s should treat instances of this class as opaque handles
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
        """
        Initialize a new file handle with the given values.

        ..seealso::
            :class:`retro_vfs_open_t`
        """
        self.id = id
        self.path = path
        self.mode = mode
        self.hints = hints


@dataclass(init=False, slots=True)
class retro_vfs_dir_handle(Structure):
    r"""
    Opaque handle for an open VFS directory.

    Corresponds to :c:type:`retro_vfs_dir_handle` in ``libretro.h``.

    .. note::
        Unlike most other :mod:`ctypes`-wrapped ``struct``\s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.FileSystemDriver` implementations.

        :term:`Core <core>`\s should treat instances of this class as opaque handles
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
        """
        Returns the Python :func:`open` mode string for this access mode.

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
"""
Return the path that was used to open a VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to an open :class:`retro_vfs_file_handle`.
:return: The path that was used to open ``stream``, as a :obj:`bytes` string.
    The string is owned by the frontend and must not be modified.

Corresponds to :c:type:`retro_vfs_get_path_t` in ``libretro.h``.
"""

retro_vfs_open_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_file_handle], [CStringArg, CIntArg[c_uint], CIntArg[c_uint]]
]
"""
Open a file for reading, writing, or both.

Registered by the :term:`frontend` and called by the :term:`core`.

:param path: The path of the file to open.
:param mode: A bitmask of :class:`VfsFileAccess` flags;
    at least one of :attr:`.VfsFileAccess.READ` or :attr:`.VfsFileAccess.WRITE` must be set.

    When nothing exists at ``path``,
    the flags decide whether a file is created:
    :attr:`~.VfsFileAccess.WRITE` without :attr:`~.VfsFileAccess.UPDATE_EXISTING`
    creates an empty file there,
    while any other combination fails without creating anything.
:param hints: A bitmask of :class:`VfsFileAccessHint` flags.
:return: A :class:`~libretro.ctypes.c_void_ptr` to a new :class:`retro_vfs_file_handle` on success,
    or :obj:`None` on failure (including when ``path`` names a directory).

Corresponds to :c:type:`retro_vfs_open_t` in ``libretro.h``.
"""

retro_vfs_close_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
"""
Close an open VFS file and release its resources.

Registered by the :term:`frontend` and called by the :term:`core`.
After this returns the handle is no longer valid.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to close.
:return: ``0`` on success, ``-1`` on failure or if ``stream`` is :obj:`None`.

Corresponds to :c:type:`retro_vfs_close_t` in ``libretro.h``.
"""

retro_vfs_size_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
"""
Return the size of an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to query.
:return: The size of the file in bytes, or ``-1`` on error.

Corresponds to :c:type:`retro_vfs_size_t` in ``libretro.h``.
"""

retro_vfs_truncate_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64]]
]
"""
Set the length of an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.
Shorter ``length`` values discard the trailing bytes;
longer values pad with platform-defined contents.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to truncate.
:param length: New length of the file, in bytes.
:return: ``0`` on success, ``-1`` on failure.

Corresponds to :c:type:`retro_vfs_truncate_t` in ``libretro.h``.
"""

retro_vfs_tell_t = TypedFunctionPointer[c_int64, [TypedPointer[retro_vfs_file_handle]]]
"""
Return the current read/write position of an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to query.
:return: The current stream position in bytes, or ``-1`` on error.

Corresponds to :c:type:`retro_vfs_tell_t` in ``libretro.h``.
"""

retro_vfs_seek_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], CIntArg[c_int64], CIntArg[c_int]]
]
"""
Set the read/write position of an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to seek.
:param offset: New offset in bytes, relative to ``seek_position``.
:param seek_position: A :class:`VfsSeekPosition` indicating the seek origin.
:return: ``0`` on success, ``-1`` on failure.
    Use :data:`retro_vfs_tell_t` to read back the resulting position.

Corresponds to :c:type:`retro_vfs_seek_t` in ``libretro.h``.
"""

retro_vfs_read_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
"""
Read data from an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to read from.
:param s: A :class:`~libretro.ctypes.c_void_ptr` to the buffer that will receive the data.
:param len: Maximum number of bytes to read.
:return: The number of bytes actually read, or ``-1`` on error.

Corresponds to :c:type:`retro_vfs_read_t` in ``libretro.h``.
"""

retro_vfs_write_t = TypedFunctionPointer[
    c_int64, [TypedPointer[retro_vfs_file_handle], c_void_ptr, CIntArg[c_uint64]]
]
"""
Write data to an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to write to.
:param s: A :class:`~libretro.ctypes.c_void_ptr` to the buffer of bytes to write.
:param len: Number of bytes to write from ``s``.
:return: The number of bytes actually written, or ``-1`` on error.

Corresponds to :c:type:`retro_vfs_write_t` in ``libretro.h``.
"""

retro_vfs_flush_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_file_handle]]]
"""
Flush pending writes for an open VFS file.

Registered by the :term:`frontend` and called by the :term:`core`.

:param stream: Pointer to the :class:`retro_vfs_file_handle` to flush.
:return: ``0`` on success, ``-1`` on failure.

Corresponds to :c:type:`retro_vfs_flush_t` in ``libretro.h``.
"""

retro_vfs_remove_t = TypedFunctionPointer[c_int, [CStringArg]]
"""
Delete the file at the given path.

Registered by the :term:`frontend` and called by the :term:`core`.

:param path: Path of the file to delete.
:return: ``0`` on success, ``-1`` on failure.

Corresponds to :c:type:`retro_vfs_remove_t` in ``libretro.h``.
"""

retro_vfs_rename_t = TypedFunctionPointer[c_int, [CStringArg, CStringArg]]
"""
Rename a file from one path to another.

Registered by the :term:`frontend` and called by the :term:`core`.

:param old_path: Path to an existing file.
:param new_path: Destination path; must not refer to an existing file.
:return: ``0`` on success, ``-1`` on failure.

Corresponds to :c:type:`retro_vfs_rename_t` in ``libretro.h``.
"""

retro_vfs_stat_t = TypedFunctionPointer[c_int, [CStringArg, TypedPointer[c_int32]]]
"""
Get information about a file at the given path.

Registered by the :term:`frontend` and called by the :term:`core`.

:param path: Path of the file to query.
:param size: Pointer to an :class:`~ctypes.c_int32` that receives the file's size in bytes,
    or :obj:`None` to ignore the size.
:return: A bitmask of :class:`VfsStat` flags,
    or ``0`` if ``path`` does not refer to a valid file.

Corresponds to :c:type:`retro_vfs_stat_t` in ``libretro.h``.
"""

retro_vfs_stat_64_t = TypedFunctionPointer[c_int, [CStringArg, TypedPointer[c_int64]]]
"""
Get information about a file at the given path, with a 64-bit size.

Registered by the :term:`frontend` and called by the :term:`core`.

Added in VFS API version 4 because :data:`retro_vfs_stat_t` reports the size
through a signed 32-bit integer and so cannot describe files larger than 2 GiB.
Changing the older callback would have broken every core already using it,
so this one was appended instead.

:param path: Path of the file to query.
:param size: Pointer to an :class:`~ctypes.c_int64` that receives the file's size in bytes,
    or :obj:`None` to ignore the size.
:return: A bitmask of :class:`VfsStat` flags,
    or ``0`` if ``path`` does not refer to a valid file.

Corresponds to :c:type:`retro_vfs_stat_64_t` in ``libretro.h``.

.. seealso::

    :data:`retro_vfs_stat_t`
        The 32-bit equivalent, available since VFS API version 1.
"""

retro_vfs_mkdir_t = TypedFunctionPointer[c_int, [CStringArg]]
"""
Create a directory at the given path.

Registered by the :term:`frontend` and called by the :term:`core`.

:param dir: Path of the directory to create.
:return: A :class:`VfsMkdirResult` value;
    ``0`` if the directory was created,
    ``-2`` if it already exists,
    or ``-1`` for any other error.

Corresponds to :c:type:`retro_vfs_mkdir_t` in ``libretro.h``.
"""

retro_vfs_opendir_t = TypedFunctionPointer[
    TypedPointer[retro_vfs_dir_handle], [CStringArg, CBoolArg]
]
"""
Open a directory so its contents can be enumerated.

Registered by the :term:`frontend` and called by the :term:`core`.

:param dir: Path to an existing directory.
:param include_hidden: :obj:`True` to include hidden files in the listing.
    The exact semantics depend on the platform.
:return: A :class:`~libretro.ctypes.c_void_ptr` to a new :class:`retro_vfs_dir_handle` on success,
    or :obj:`None` on failure.

Corresponds to :c:type:`retro_vfs_opendir_t` in ``libretro.h``.
"""

retro_vfs_readdir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
"""
Advance to the next directory entry.

Registered by the :term:`frontend` and called by the :term:`core`.

:param dirstream: Pointer to the :class:`retro_vfs_dir_handle` to advance.
:return: :obj:`True` if a new entry is available,
    :obj:`False` if no more entries remain.

Corresponds to :c:type:`retro_vfs_readdir_t` in ``libretro.h``.
"""

retro_vfs_dirent_get_name_t = TypedFunctionPointer[c_char_p, [TypedPointer[retro_vfs_dir_handle]]]
"""
Return the filename of the current directory entry.

Registered by the :term:`frontend` and called by the :term:`core`.
The returned pointer is valid until the next call to :c:type:`retro_vfs_readdir_t`
or :c:type:`retro_vfs_closedir_t` on this handle.

:param dirstream: Pointer to the :class:`retro_vfs_dir_handle` to query.
:return: The current entry's filename as a :obj:`bytes` string,
    or :obj:`None` on error.

Corresponds to :c:type:`retro_vfs_dirent_get_name_t` in ``libretro.h``.
"""

retro_vfs_dirent_is_dir_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_vfs_dir_handle]]]
"""
Return whether the current directory entry is itself a directory.

Registered by the :term:`frontend` and called by the :term:`core`.

:param dirstream: Pointer to the :class:`retro_vfs_dir_handle` to query.
:return: :obj:`True` if the current entry names a subdirectory,
    :obj:`False` otherwise or on error.

Corresponds to :c:type:`retro_vfs_dirent_is_dir_t` in ``libretro.h``.
"""

retro_vfs_closedir_t = TypedFunctionPointer[c_int, [TypedPointer[retro_vfs_dir_handle]]]
"""
Close an open VFS directory handle.

Registered by the :term:`frontend` and called by the :term:`core`.
After this returns the handle is no longer valid.

:param dirstream: Pointer to the :class:`retro_vfs_dir_handle` to close.
:return: ``0`` on success, ``-1`` on failure.

Corresponds to :c:type:`retro_vfs_closedir_t` in ``libretro.h``.
"""


@dataclass(init=False, slots=True)
class retro_vfs_interface(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`retro_vfs_interface` in ``libretro.h``.

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
    stat_64: retro_vfs_stat_64_t | None
    """
    Gets status flags and 64-bit size of a file.
    Only set by frontends that implement VFS API version 4 or newer.
    """

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
        # VFS API v4; new fields must be appended so the struct stays ABI-compatible
        ("stat_64", retro_vfs_stat_64_t),
    )

    def __deepcopy__(self, _):
        """Return a shallow copy."""
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
            self.stat_64,
        )


@dataclass(init=False, slots=True)
class retro_vfs_interface_info(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`retro_vfs_interface_info` in ``libretro.h``.

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
        Return a deep copy of this object, including all subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_vfs_interface_info(
            self.required_interface_version,
            pointer(deepcopy(self.iface[0], memo)) if self.iface else None,
        )


@dataclass(init=False, slots=True)
class retro_vfs_authorized_location(Structure):
    """
    A single filesystem location that the frontend has granted permission to access.

    Corresponds to :c:type:`retro_vfs_authorized_location` in ``libretro.h``.

    Useful on platforms where an application may only touch directories
    the user has explicitly granted, such as Android's Storage Access Framework.

    .. note::
        The frontend owns both strings.
        Cores that need them after the environment call returns must copy them.
    """

    path: bytes | None
    """
    Path to the authorized location,
    in a form that can be passed directly to the callbacks in :class:`retro_vfs_interface`
    (for example ``saf://...`` on Android).
    """

    label: bytes | None
    """Human-readable name for this location, suitable for display to the user."""

    flags: int
    """
    Reserved for future use.

    ``libretro.h`` does not currently define any flags for this field.
    """

    _fields_ = (
        ("path", c_char_p),
        ("label", c_char_p),
        ("flags", c_uint),
    )

    def __deepcopy__(self, _):
        """
        Return a deep copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_vfs_authorized_location
        >>> loc = retro_vfs_authorized_location(path=b"saf://downloads", label=b"Downloads")
        >>> copy.deepcopy(loc).label
        b'Downloads'
        """
        return retro_vfs_authorized_location(
            path=self.path,
            label=self.label,
            flags=self.flags,
        )


@dataclass(init=False, slots=True)
class retro_vfs_authorized_locations(Structure, NullPointerToNoneMixin):
    r"""
    The set of :class:`retro_vfs_authorized_location`\s that the frontend exposes to a core.

    Corresponds to :c:type:`retro_vfs_authorized_locations` in ``libretro.h``.

    Empty sets have length ``0``;
    populating :attr:`locations` lets the set be iterated like a sequence:

    >>> from libretro.api import retro_vfs_authorized_location, retro_vfs_authorized_locations
    >>> locs = (retro_vfs_authorized_location * 2)(
    ...     retro_vfs_authorized_location(path=b"saf://roms", label=b"ROMs"),
    ...     retro_vfs_authorized_location(path=b"saf://saves", label=b"Saves"),
    ... )
    >>> group = retro_vfs_authorized_locations(locs, 2)
    >>> [loc.label for loc in group]
    [b'ROMs', b'Saves']

    .. note::
        ``libretro.h`` names the length field ``count``,
        but libretro.py calls it :attr:`num_locations`
        so that :meth:`count` complies with :class:`~collections.abc.Sequence`.
        Field names don't participate in the C ABI,
        so the rename is invisible to :term:`core`\s.

    .. seealso::

        :attr:`.EnvironmentCall.GET_VFS_AUTHORIZED_LOCATIONS`
            The environment call that fills in this struct.
    """

    locations: TypedPointer[retro_vfs_authorized_location] | None
    """Array of authorized locations."""
    num_locations: int
    """
    Number of entries in :attr:`locations`.

    Named ``count`` in ``libretro.h``;
    see the note in this class's summary for why libretro.py differs.
    """

    _fields_ = (
        ("locations", POINTER(retro_vfs_authorized_location)),
        ("num_locations", c_size_t),
    )

    def __init__(
        self,
        locations: TypedPointer[retro_vfs_authorized_location]
        | TypedArray[retro_vfs_authorized_location]
        | Array[retro_vfs_authorized_location]
        | Sequence[retro_vfs_authorized_location]
        | None = None,
        num_locations: CIntArg[c_size_t] | None = None,
    ):
        """
        Initialize a :class:`retro_vfs_authorized_locations`.

        When *locations* is a :class:`~collections.abc.Sequence` (but not a pointer or array),
        it is converted to a :class:`~ctypes.Array`
        and *num_locations* defaults to its length:

        >>> from libretro.api import retro_vfs_authorized_location, retro_vfs_authorized_locations
        >>> group = retro_vfs_authorized_locations(
        ...     [retro_vfs_authorized_location(path=b"saf://roms")]
        ... )
        >>> len(group)
        1

        :param locations: Array of authorized locations as a pointer, array, or iterable.
        :param num_locations: Number of locations;
            inferred from *locations* when it is an array or iterable,
            and ``0`` when it is a pointer.
        """
        if locations is not None and not isinstance(locations, (TypedPointer, Array)):
            items = list(locations)
            locations = (retro_vfs_authorized_location * len(items))(*items)
        if num_locations is None:
            num_locations = len(locations) if isinstance(locations, Array) else 0

        super(retro_vfs_authorized_locations, self).__init__(locations, num_locations)

    def __len__(self):
        """
        Return the number of authorized locations.

        >>> from libretro.api import retro_vfs_authorized_locations
        >>> len(retro_vfs_authorized_locations())
        0
        """
        return self.num_locations

    @overload
    def __getitem__(self, item: int) -> retro_vfs_authorized_location: ...
    @overload
    def __getitem__(
        self, item: "slice[retro_vfs_authorized_location]"
    ) -> list[retro_vfs_authorized_location]: ...
    def __getitem__(
        self, item: "int | slice[retro_vfs_authorized_location]"
    ) -> retro_vfs_authorized_location | list[retro_vfs_authorized_location]:
        """
        Return a location by index or a list of locations by slice.

        Supports negative indexes in the usual Python fashion:

        >>> from libretro.api import retro_vfs_authorized_location, retro_vfs_authorized_locations
        >>> locs = (retro_vfs_authorized_location * 2)(
        ...     retro_vfs_authorized_location(path=b"saf://roms"),
        ...     retro_vfs_authorized_location(path=b"saf://saves"),
        ... )
        >>> retro_vfs_authorized_locations(locs, 2)[-1].path
        b'saf://saves'

        :param item: An integer index or slice.
        :return: A single :class:`retro_vfs_authorized_location` or a list of them.
        :raises RuntimeError: If :attr:`locations` is :obj:`None`.
        :raises IndexError: If ``item`` is an integer outside ``[-len, len)``.
        :raises TypeError: If ``item`` is neither an :class:`int` nor a :class:`slice`.
        """
        if not self.locations:
            raise RuntimeError("No authorized locations")

        match item:
            case int(i):
                n = len(self)
                if not (-n <= i < n):
                    raise IndexError(f"Expected {-n} <= index < {n}, got {i}")
                if i < 0:
                    i += n
                return self.locations[i]
            case slice() as s:
                return self.locations[s]
            case _:
                raise TypeError(f"Expected an int or slice, got {type(item).__name__}")

    def __iter__(self) -> Iterator[retro_vfs_authorized_location]:
        """
        Iterate over the authorized locations.

        Returns no elements when :attr:`locations` is :obj:`None`:

        >>> from libretro.api import retro_vfs_authorized_locations
        >>> list(retro_vfs_authorized_locations())
        []
        """
        if not self.locations:
            return
        for i in range(self.num_locations):
            yield self.locations[i]

    def __contains__(self, item: object) -> bool:
        """
        Test whether ``item`` appears in this sequence.

        :param item: The element to search for.
        :return: :obj:`True` if found, :obj:`False` otherwise.
        """
        return any(v is item or v == item for v in self)

    def __reversed__(self) -> Iterator[retro_vfs_authorized_location]:
        """
        Iterate over the authorized locations in reverse order.

        Returns no elements when :attr:`locations` is :obj:`None`.

        :return: An iterator over the locations in reverse order.
        """
        if not self.locations:
            return
        for i in range(self.num_locations - 1, -1, -1):
            yield self.locations[i]

    def count(self, value: object) -> int:
        """
        Count occurrences of ``value`` in this sequence.

        :param value: The element to count.
        :return: The number of times ``value`` appears.
        """
        return sum(1 for v in self if v is value or v == value)

    def index(self, value: object, start: int = 0, stop: int | None = None) -> int:
        """
        Return the index of the first occurrence of ``value``.

        :param value: The element to search for.
        :param start: Optional start index (inclusive).
        :param stop: Optional stop index (exclusive).
        :return: The index of the first match within ``[start, stop)``.
        :raises ValueError: If ``value`` is not found within the given range.
        """
        n = len(self)
        if start < 0:
            start = max(n + start, 0)
        if stop is None:
            stop = n
        elif stop < 0:
            stop = max(n + stop, 0)
        for i in range(start, min(stop, n)):
            v = self[i]
            if v is value or v == value:
                return i
        raise ValueError(f"{value!r} is not in sequence")

    def __deepcopy__(self, memodict: MemoDict = None):
        """
        Return a deep copy of this object,
        including all subobjects and strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_vfs_authorized_locations
        >>> copy.deepcopy(retro_vfs_authorized_locations()).num_locations
        0
        """
        return retro_vfs_authorized_locations(
            locations=deepcopy_array(self.locations, self.num_locations, memodict),
            num_locations=self.num_locations,
        )


Sequence.register(retro_vfs_authorized_locations)  # type: ignore
# Sequence.register isn't part of the type stubs


class VfsFileAccessHint(IntFlag):
    """
    Hints for file access patterns.

    >>> from libretro.api import VfsFileAccessHint
    >>> VfsFileAccessHint.FREQUENT_ACCESS
    <VfsFileAccessHint.FREQUENT_ACCESS: 1>
    """

    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    """No hint; the frontend should use its default access strategy."""

    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS
    """The file will be accessed often, so the frontend may keep it cached or mapped."""

    SEQUENTIAL_BULK = RETRO_VFS_FILE_ACCESS_HINT_SEQUENTIAL_BULK
    """
    The file will be read once from start to finish and then closed.

    Only meaningful in combination with :attr:`.VfsFileAccess.READ`.
    The caller keeps whatever bytes it asks for,
    so anything the frontend retains past the call is wasted;
    a frontend that buffers its reads may skip doing so for such a stream.
    """


class VfsSeekPosition(IntEnum):
    """
    Seek origin for VFS seek operations.

    >>> from libretro.api import VfsSeekPosition
    >>> VfsSeekPosition.START
    <VfsSeekPosition.START: 0>
    """

    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END


class VfsStat(IntFlag):
    """
    Flags returned by VFS stat operations.

    >>> from libretro.api import VfsStat
    >>> VfsStat.IS_DIRECTORY
    <VfsStat.IS_DIRECTORY: 2>
    """

    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL


class VfsMkdirResult(IntEnum):
    """
    Return codes for VFS mkdir operations.

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
    "retro_vfs_stat_64_t",
    "retro_vfs_mkdir_t",
    "retro_vfs_opendir_t",
    "retro_vfs_readdir_t",
    "retro_vfs_dirent_get_name_t",
    "retro_vfs_dirent_is_dir_t",
    "retro_vfs_closedir_t",
    "retro_vfs_interface",
    "retro_vfs_interface_info",
    "retro_vfs_authorized_location",
    "retro_vfs_authorized_locations",
    "VfsFileAccessHint",
    "VfsSeekPosition",
    "VfsStat",
    "VfsMkdirResult",
    "VfsPath",
]
