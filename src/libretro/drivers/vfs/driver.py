"""
:class:`~typing.Protocol` definition for the virtual filesystem interface.

.. seealso::

    :mod:`libretro.api.vfs`
        The matching :mod:`ctypes` types and callback definitions.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsSeekPosition,
    VfsStat,
    retro_vfs_dir_handle,
    retro_vfs_file_handle,
)


@runtime_checkable
class FileHandle(Protocol):
    """
    Represents an open file in the virtual file system.

    This is a higher-level abstraction than the raw file handle provided by the VFS interface.
    Optional.
    """

    @abstractmethod
    def __init__(self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint):
        """
        Open the file at ``path`` with the given access ``mode`` and ``hints``.

        :param path: Path of the file to open, encoded as :class:`bytes`.
        :param mode: Access mode flags controlling read/write behavior.
        :param hints: Hints describing the intended access pattern.
        :raises OSError: If the file cannot be opened.
        """
        ...

    @abstractmethod
    def close(self) -> bool:
        """
        Close the underlying file and release any associated resources.

        :return: ``True`` if the file was closed successfully, ``False`` otherwise.
        """
        ...

    @property
    @abstractmethod
    def path(self) -> bytes:
        """
        Return the path that was used to open this file.

        :return: The original path as :class:`bytes`.
        :raises IOError: If the file is closed.
        """
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        """
        Return the size of the open file in bytes.

        :return: The current file size in bytes.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def tell(self) -> int:
        """
        Return the current read/write offset within the file.

        :return: The current byte offset from the start of the file.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def seek(self, offset: int, whence: VfsSeekPosition) -> int:
        """
        Move the file's read/write offset to ``offset`` relative to ``whence``.

        :param offset: The new offset, in bytes, relative to ``whence``.
        :param whence: The reference position used to interpret ``offset``.
        :return: The resulting absolute offset from the start of the file.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def read(self, buffer: memoryview[int]) -> int:
        """
        Read bytes from the file into ``buffer``.

        :param buffer: A writable buffer to receive the bytes that were read.
        :return: The number of bytes that were actually read.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def write(self, buffer: memoryview[int]) -> int:
        """
        Write the contents of ``buffer`` to the file at the current offset.

        :param buffer: A readable buffer holding the bytes to write.
        :return: The number of bytes that were actually written.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def flush(self) -> bool:
        """
        Flush any buffered data to the underlying storage.

        :return: ``True`` if the flush succeeded, ``False`` otherwise.
        :raises IOError: If the file is closed.
        """
        ...

    @abstractmethod
    def truncate(self, length: int) -> bool:
        """
        Truncate (or extend) the file to ``length`` bytes.

        :param length: The new size of the file, in bytes.
        :return: ``True`` if the operation succeeded, ``False`` otherwise.
        :raises IOError: If the file is closed.
        """
        ...


@runtime_checkable
class DirectoryHandle(Protocol):
    """
    Represents an open directory in the virtual file system.

    This is a higher-level abstraction than the raw directory handle provided by the VFS interface.
    Optional.
    """

    @abstractmethod
    def __init__(self, dir: bytes, include_hidden: bool):
        """
        Open the directory at ``dir`` for iteration.

        :param dir: Path of the directory to open, encoded as :class:`bytes`.
        :param include_hidden: Whether hidden entries should be returned during iteration.
        :raises OSError: If the directory cannot be opened.
        """
        ...

    @abstractmethod
    def readdir(self) -> bool:
        """
        Advance to the next entry in the directory.

        :return: ``True`` if a new entry is now available, ``False`` if the end was reached.
        :raises IOError: If the directory is closed.
        """
        ...

    @property
    @abstractmethod
    def dirent_name(self) -> bytes | None:
        """
        Return the name of the current directory entry, if any.

        :return: The entry name as :class:`bytes`, or ``None`` if no entry is available.
        :raises IOError: If the directory is closed.
        """
        ...

    @property
    @abstractmethod
    def dirent_is_dir(self) -> bool:
        """
        Return whether the current directory entry refers to a subdirectory.

        :return: ``True`` if the current entry is a directory, ``False`` otherwise.
        :raises IOError: If the directory is closed.
        :raises ValueError: If no current entry is available.
        """
        ...

    @abstractmethod
    def closedir(self) -> bool:
        """
        Close the directory and release any associated resources.

        :return: ``True`` if the directory was closed successfully, ``False`` otherwise.
        """
        ...


@runtime_checkable
class FileSystemDriver(Protocol):
    """
    Protocol for backends that implement the libretro virtual filesystem interface.

    Implementations expose file and directory operations to cores using
    the same semantics as the C ``retro_vfs_*`` callbacks.

    .. seealso::

        :mod:`libretro.api.vfs`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def version(self) -> int:
        """
        Return the VFS interface version implemented by this driver.

        :return: The supported VFS interface version (1, 2, or 3).
        """
        ...

    @abstractmethod
    def get_path(self, stream: retro_vfs_file_handle) -> bytes | None:
        """
        Return the path that was used to open ``stream``.

        :param stream: An open file handle previously returned by :meth:`open`.
        :return: The original path as :class:`bytes`, or ``None`` if ``stream`` is unknown.

        .. seealso:: :c:func:`retro_vfs_get_path_t`
        """
        ...

    @abstractmethod
    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> retro_vfs_file_handle | None:
        """
        Open the file at ``path`` and return a handle to it.

        :param path: Path of the file to open, encoded as :class:`bytes`.
        :param mode: Access mode flags controlling read/write behavior.
        :param hints: Hints describing the intended access pattern.
        :return: A new :class:`.retro_vfs_file_handle`, or ``None`` if the file could not be opened.

        .. seealso:: :c:func:`retro_vfs_open_t`
        """
        ...

    @abstractmethod
    def close(self, stream: retro_vfs_file_handle) -> bool:
        """
        Close the file referenced by ``stream``.

        :param stream: A file handle previously returned by :meth:`open`.
        :return: ``True`` if the file was closed successfully, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_close_t`
        """
        ...

    @abstractmethod
    def size(self, stream: retro_vfs_file_handle) -> int:
        """
        Return the size of the file referenced by ``stream``.

        :param stream: An open file handle previously returned by :meth:`open`.
        :return: The size of the file in bytes, or a negative value on failure.

        .. seealso:: :c:func:`retro_vfs_size_t`
        """
        ...

    @abstractmethod
    def truncate(self, stream: retro_vfs_file_handle, length: int) -> bool:
        """
        Truncate (or extend) the file referenced by ``stream`` to ``length`` bytes.

        :param stream: An open file handle previously returned by :meth:`open`.
        :param length: The new size of the file, in bytes.
        :return: ``True`` if the operation succeeded, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_truncate_t`
        """
        ...

    @abstractmethod
    def tell(self, stream: retro_vfs_file_handle) -> int:
        """
        Return the current read/write offset within ``stream``.

        :param stream: An open file handle previously returned by :meth:`open`.
        :return: The current byte offset from the start of the file, or a negative value on failure.

        .. seealso:: :c:func:`retro_vfs_tell_t`
        """
        ...

    @abstractmethod
    def seek(self, stream: retro_vfs_file_handle, offset: int, whence: VfsSeekPosition) -> int:
        """
        Move ``stream``'s read/write offset to ``offset`` relative to ``whence``.

        :param stream: An open file handle previously returned by :meth:`open`.
        :param offset: The new offset, in bytes, relative to ``whence``.
        :param whence: The reference position used to interpret ``offset``.
        :return: The resulting absolute offset, or a negative value on failure.

        .. seealso:: :c:func:`retro_vfs_seek_t`
        """
        ...

    @abstractmethod
    def read(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        """
        Read bytes from ``stream`` into ``buffer``.

        :param stream: An open file handle previously returned by :meth:`open`.
        :param buffer: A writable buffer to receive the bytes that were read.
        :return: The number of bytes actually read, or a negative value on failure.

        .. seealso:: :c:func:`retro_vfs_read_t`
        """
        ...

    @abstractmethod
    def write(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        """
        Write the contents of ``buffer`` to ``stream`` at its current offset.

        :param stream: An open file handle previously returned by :meth:`open`.
        :param buffer: A readable buffer holding the bytes to write.
        :return: The number of bytes actually written, or a negative value on failure.

        .. seealso:: :c:func:`retro_vfs_write_t`
        """
        ...

    @abstractmethod
    def flush(self, stream: retro_vfs_file_handle) -> bool:
        """
        Flush any buffered data for ``stream`` to the underlying storage.

        :param stream: An open file handle previously returned by :meth:`open`.
        :return: ``True`` if the flush succeeded, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_flush_t`
        """
        ...

    @abstractmethod
    def remove(self, path: bytes) -> bool:
        """
        Delete the file at ``path``.

        :param path: Path of the file to remove, encoded as :class:`bytes`.
        :return: ``True`` if the file was removed successfully, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_remove_t`
        """
        ...

    @abstractmethod
    def rename(self, old_path: bytes, new_path: bytes) -> bool:
        """
        Rename or move the file at ``old_path`` to ``new_path``.

        :param old_path: Existing path of the file, encoded as :class:`bytes`.
        :param new_path: New path for the file, encoded as :class:`bytes`.
        :return: ``True`` if the rename succeeded, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_rename_t`
        """
        ...

    @abstractmethod
    def stat(self, path: bytes) -> tuple[VfsStat, int] | None:
        """
        Return file metadata for ``path``.

        :param path: Path of the entry to inspect, encoded as :class:`bytes`.
        :return: A pair of :class:`.VfsStat` flags and the entry size in bytes,
            or ``None`` if ``path`` does not exist.

        .. seealso:: :c:func:`retro_vfs_stat_t`
        """
        ...

    @abstractmethod
    def mkdir(self, path: bytes) -> VfsMkdirResult:
        """
        Create a directory at ``path``.

        :param path: Path of the directory to create, encoded as :class:`bytes`.
        :return: A :class:`.VfsMkdirResult` describing the outcome of the operation.

        .. seealso:: :c:func:`retro_vfs_mkdir_t`
        """
        ...

    @abstractmethod
    def opendir(self, path: bytes, include_hidden: bool) -> retro_vfs_dir_handle | None:
        """
        Open the directory at ``path`` for iteration.

        :param path: Path of the directory to open, encoded as :class:`bytes`.
        :param include_hidden: Whether hidden entries should be returned during iteration.
        :return: A new :class:`.retro_vfs_dir_handle`,
            or ``None`` if the directory could not be opened.

        .. seealso:: :c:func:`retro_vfs_opendir_t`
        """
        ...

    @abstractmethod
    def readdir(self, dir: retro_vfs_dir_handle) -> bool:
        """
        Advance ``dir`` to its next entry.

        :param dir: An open directory handle previously returned by :meth:`opendir`.
        :return: ``True`` if a new entry is now available, ``False`` if the end was reached.

        .. seealso:: :c:func:`retro_vfs_readdir_t`
        """
        ...

    @abstractmethod
    def dirent_get_name(self, dir: retro_vfs_dir_handle) -> bytes | None:
        """
        Return the name of the current entry in ``dir``.

        :param dir: An open directory handle previously returned by :meth:`opendir`.
        :return: The entry name as :class:`bytes`, or ``None`` if no entry is available.

        .. seealso:: :c:func:`retro_vfs_dirent_get_name_t`
        """
        ...

    @abstractmethod
    def dirent_is_dir(self, dir: retro_vfs_dir_handle) -> bool:
        """
        Return whether the current entry in ``dir`` refers to a subdirectory.

        :param dir: An open directory handle previously returned by :meth:`opendir`.
        :return: ``True`` if the current entry is a directory, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_dirent_is_dir_t`
        """
        ...

    @abstractmethod
    def closedir(self, dir: retro_vfs_dir_handle) -> bool:
        """
        Close ``dir`` and release any associated resources.

        :param dir: A directory handle previously returned by :meth:`opendir`.
        :return: ``True`` if the directory was closed successfully, ``False`` otherwise.

        .. seealso:: :c:func:`retro_vfs_closedir_t`
        """
        ...


__all__ = ["FileSystemDriver", "FileHandle", "DirectoryHandle"]
