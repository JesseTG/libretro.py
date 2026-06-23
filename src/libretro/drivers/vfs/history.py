"""
:class:`.FileSystemDriver` decorator that records the operations performed against another driver.

.. seealso::

    :class:`.FileSystemDriver`
        The protocol this driver implements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsSeekPosition,
    VfsStat,
    retro_vfs_dir_handle,
    retro_vfs_file_handle,
)

from .driver import FileSystemDriver


@dataclass(frozen=True, slots=True, kw_only=True)
class GetPath:
    """Recorded :meth:`.FileSystemDriver.get_path` call."""

    stream: retro_vfs_file_handle
    result: bytes | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Open:
    """Recorded :meth:`.FileSystemDriver.open` call."""

    path: bytes
    mode: VfsFileAccess
    hints: VfsFileAccessHint
    result: retro_vfs_file_handle | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Close:
    """Recorded :meth:`.FileSystemDriver.close` call."""

    stream: retro_vfs_file_handle
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Size:
    """Recorded :meth:`.FileSystemDriver.size` call."""

    stream: retro_vfs_file_handle
    result: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Truncate:
    """Recorded :meth:`.FileSystemDriver.truncate` call."""

    stream: retro_vfs_file_handle
    length: int
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Tell:
    """Recorded :meth:`.FileSystemDriver.tell` call."""

    stream: retro_vfs_file_handle
    result: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Seek:
    """Recorded :meth:`.FileSystemDriver.seek` call."""

    stream: retro_vfs_file_handle
    offset: int
    whence: VfsSeekPosition
    result: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Read:
    """Recorded :meth:`.FileSystemDriver.read` call."""

    stream: retro_vfs_file_handle
    buffer: bytes
    result: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Write:
    """Recorded :meth:`.FileSystemDriver.write` call."""

    stream: retro_vfs_file_handle
    buffer: bytes
    result: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Flush:
    """Recorded :meth:`.FileSystemDriver.flush` call."""

    stream: retro_vfs_file_handle
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Remove:
    """Recorded :meth:`.FileSystemDriver.remove` call."""

    path: bytes
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Rename:
    """Recorded :meth:`.FileSystemDriver.rename` call."""

    old_path: bytes
    new_path: bytes
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Stat:
    """Recorded :meth:`.FileSystemDriver.stat` call."""

    path: bytes
    result: tuple[VfsStat, int] | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Mkdir:
    """Recorded :meth:`.FileSystemDriver.mkdir` call."""

    path: bytes
    result: VfsMkdirResult


@dataclass(frozen=True, slots=True, kw_only=True)
class OpenDir:
    """Recorded :meth:`.FileSystemDriver.opendir` call."""

    path: bytes
    include_hidden: bool
    result: retro_vfs_dir_handle | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDir:
    """Recorded :meth:`.FileSystemDriver.readdir` call."""

    dir: retro_vfs_dir_handle
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class DirentGetName:
    """Recorded :meth:`.FileSystemDriver.dirent_get_name` call."""

    dir: retro_vfs_dir_handle
    result: bytes | None


@dataclass(frozen=True, slots=True, kw_only=True)
class DirentIsDir:
    """Recorded :meth:`.FileSystemDriver.dirent_is_dir` call."""

    dir: retro_vfs_dir_handle
    result: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CloseDir:
    """Recorded :meth:`.FileSystemDriver.closedir` call."""

    dir: retro_vfs_dir_handle
    result: int


type VfsOperation = (
    GetPath
    | Open
    | Close
    | Size
    | Truncate
    | Tell
    | Seek
    | Read
    | Write
    | Flush
    | Remove
    | Rename
    | Stat
    | Mkdir
    | OpenDir
    | ReadDir
    | DirentGetName
    | DirentIsDir
    | CloseDir
)


class HistoryFileSystemDriver(FileSystemDriver):
    """
    :class:`.FileSystemDriver` that wraps another and records every call made through it.

    Each recorded call is appended to :attr:`history` as a :type:`.VfsOperation` instance,
    making it easy to assert against the exact sequence of VFS operations a core performed.
    """

    def __init__(self, interface: FileSystemDriver):
        """
        Wrap ``interface`` and start with an empty history.

        :param interface: The underlying :class:`.FileSystemDriver` to delegate to.
        :raises TypeError: If ``interface`` is not a :class:`.FileSystemDriver`.
        """
        if not isinstance(interface, FileSystemDriver):
            raise TypeError(f"Expected a FileSystemDriver, got {type(interface).__name__}")

        self._interface = interface
        self._history: list[VfsOperation] = []

    @property
    @override
    def version(self) -> int:
        return self._interface.version

    @override
    def get_path(self, stream: retro_vfs_file_handle) -> bytes | None:
        try:
            path = self._interface.get_path(stream)
            self._history.append(GetPath(stream=stream, result=path))
            return path
        except:
            self._history.append(GetPath(stream=stream, result=None))
            raise

    @override
    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> retro_vfs_file_handle | None:
        try:
            handle = self._interface.open(path, mode, hints)
            self._history.append(Open(path=path, mode=mode, hints=hints, result=handle))
            return handle
        except:
            self._history.append(Open(path=path, mode=mode, hints=hints, result=None))
            raise

    @override
    def close(self, stream: retro_vfs_file_handle) -> bool:
        try:
            result = self._interface.close(stream)
            self._history.append(Close(stream=stream, result=result))
            return result
        except:
            self._history.append(Close(stream=stream, result=False))
            raise

    @override
    def size(self, stream: retro_vfs_file_handle) -> int:
        try:
            result = self._interface.size(stream)
            self._history.append(Size(stream=stream, result=result))
            return result
        except:
            self._history.append(Size(stream=stream, result=-1))
            raise

    @override
    def truncate(self, stream: retro_vfs_file_handle, length: int) -> bool:
        try:
            result = self._interface.truncate(stream, length)
            self._history.append(Truncate(stream=stream, length=length, result=result))
            return result
        except:
            self._history.append(Truncate(stream=stream, length=length, result=False))
            raise

    @override
    def tell(self, stream: retro_vfs_file_handle) -> int:
        try:
            result = self._interface.tell(stream)
            self._history.append(Tell(stream=stream, result=result))
            return result
        except:
            self._history.append(Tell(stream=stream, result=-1))
            raise

    @override
    def seek(self, stream: retro_vfs_file_handle, offset: int, whence: VfsSeekPosition) -> int:
        try:
            result = self._interface.seek(stream, offset, whence)
            self._history.append(Seek(stream=stream, offset=offset, whence=whence, result=result))
            return result
        except:
            self._history.append(Seek(stream=stream, offset=offset, whence=whence, result=-1))
            raise

    @override
    def read(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        try:
            result = self._interface.read(stream, buffer)
            self._history.append(Read(stream=stream, buffer=bytes(buffer), result=result))
            return result
        except:
            self._history.append(Read(stream=stream, buffer=bytes(buffer), result=-1))
            raise

    @override
    def write(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        try:
            result = self._interface.write(stream, buffer)
            self._history.append(Write(stream=stream, buffer=bytes(buffer), result=result))
            return result
        except:
            self._history.append(Write(stream=stream, buffer=bytes(buffer), result=-1))
            raise

    @override
    def flush(self, stream: retro_vfs_file_handle) -> bool:
        try:
            result = self._interface.flush(stream)
            self._history.append(Flush(stream=stream, result=result))
            return result
        except:
            self._history.append(Flush(stream=stream, result=False))
            raise

    @override
    def remove(self, path: bytes) -> bool:
        try:
            result = self._interface.remove(path)
            self._history.append(Remove(path=path, result=result))
            return result
        except:
            self._history.append(Remove(path=path, result=False))
            raise

    @override
    def rename(self, old_path: bytes, new_path: bytes) -> bool:
        try:
            result = self._interface.rename(old_path, new_path)
            self._history.append(Rename(old_path=old_path, new_path=new_path, result=result))
            return result
        except:
            self._history.append(Rename(old_path=old_path, new_path=new_path, result=False))
            raise

    @override
    def stat(self, path: bytes) -> tuple[VfsStat, int] | None:
        try:
            result = self._interface.stat(path)
            self._history.append(Stat(path=path, result=result))
            return result
        except:
            self._history.append(Stat(path=path, result=None))
            raise

    @override
    def mkdir(self, path: bytes) -> VfsMkdirResult:
        try:
            result = self._interface.mkdir(path)
            self._history.append(Mkdir(path=path, result=result))
            return result
        except:
            self._history.append(Mkdir(path=path, result=VfsMkdirResult.ERROR))
            raise

    @override
    def opendir(self, path: bytes, include_hidden: bool) -> retro_vfs_dir_handle | None:
        try:
            handle = self._interface.opendir(path, include_hidden)
            self._history.append(OpenDir(path=path, include_hidden=include_hidden, result=handle))
            return handle
        except:
            self._history.append(OpenDir(path=path, include_hidden=include_hidden, result=None))
            raise

    @override
    def readdir(self, dir: retro_vfs_dir_handle) -> bool:
        try:
            result = self._interface.readdir(dir)
            self._history.append(ReadDir(dir=dir, result=result))
            return result
        except:
            self._history.append(ReadDir(dir=dir, result=False))
            raise

    @override
    def dirent_get_name(self, dir: retro_vfs_dir_handle) -> bytes | None:
        try:
            result = self._interface.dirent_get_name(dir)
            self._history.append(DirentGetName(dir=dir, result=result))
            return result
        except:
            self._history.append(DirentGetName(dir=dir, result=None))
            raise

    @override
    def dirent_is_dir(self, dir: retro_vfs_dir_handle) -> bool:
        try:
            result = self._interface.dirent_is_dir(dir)
            self._history.append(DirentIsDir(dir=dir, result=result))
            return result
        except:
            self._history.append(DirentIsDir(dir=dir, result=False))
            raise

    @override
    def closedir(self, dir: retro_vfs_dir_handle) -> bool:
        try:
            result = self._interface.closedir(dir)
            self._history.append(CloseDir(dir=dir, result=result))
            return result
        except:
            self._history.append(CloseDir(dir=dir, result=False))
            raise

    @property
    def history(self) -> tuple[VfsOperation, ...]:
        """The recorded operations in the order they were performed."""
        return tuple(self._history)


__all__ = [
    "HistoryFileSystemDriver",
    "VfsOperation",
    "GetPath",
    "Open",
    "Close",
    "Size",
    "Truncate",
    "Tell",
    "Seek",
    "Read",
    "Write",
    "Flush",
    "Remove",
    "Rename",
    "Stat",
    "Mkdir",
    "OpenDir",
    "ReadDir",
    "DirentGetName",
    "DirentIsDir",
    "CloseDir",
]
