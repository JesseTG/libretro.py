from collections.abc import MutableSequence, Sequence
from enum import Enum, auto
from typing import Any, NamedTuple

from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsSeekPosition,
    VfsStat,
)

from .interface import DirectoryHandle, DirEntry, FileHandle, FileSystemInterface


class VfsOperationType(Enum):
    GET_PATH = (auto(),)
    OPEN = (auto(),)
    CLOSE = (auto(),)
    SIZE = (auto(),)
    TELL = (auto(),)
    SEEK = (auto(),)
    READ = (auto(),)
    WRITE = (auto(),)
    FLUSH = (auto(),)
    REMOVE = (auto(),)
    RENAME = (auto(),)
    TRUNCATE = (auto(),)
    STAT = (auto(),)
    MKDIR = (auto(),)
    OPENDIR = (auto(),)
    READDIR = (auto(),)
    DIRENT_GET_NAME = (auto(),)
    DIRENT_IS_DIR = (auto(),)
    CLOSEDIR = (auto(),)


class VfsOperation(NamedTuple):
    operation: VfsOperationType
    args: tuple
    result: Any


class HistoryFileHandle(FileHandle):
    def __init__(self, handle: FileHandle, history: MutableSequence[VfsOperation]):
        if not isinstance(handle, FileHandle):
            raise TypeError(f"Expected a FileHandle, got {type(handle).__name__}")

        if not isinstance(history, MutableSequence):
            raise TypeError(f"Expected a MutableSequence, got {type(history).__name__}")

        self._handle = handle
        self._history = history

    def close(self) -> bool:
        try:
            result = self._handle.close()
            self._history.append(VfsOperation(VfsOperationType.CLOSE, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.CLOSE, (), False))
            raise

    @property
    def path(self) -> bytes:
        try:
            result = self._handle.path
            self._history.append(VfsOperation(VfsOperationType.GET_PATH, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.GET_PATH, (), None))
            raise

    @property
    def size(self) -> int:
        try:
            result = self._handle.size
            self._history.append(VfsOperation(VfsOperationType.SIZE, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.SIZE, (), -1))
            raise

    def tell(self) -> int:
        try:
            result = self._handle.tell()
            self._history.append(VfsOperation(VfsOperationType.TELL, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.TELL, (), -1))
            raise

    def seek(self, offset: int, whence: VfsSeekPosition) -> int:
        try:
            result = self._handle.seek(offset, whence)
            self._history.append(VfsOperation(VfsOperationType.SEEK, (offset, whence), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.SEEK, (offset, whence), -1))
            raise

    def read(self, buffer: bytearray | memoryview) -> int:
        try:
            result = self._handle.read(buffer)
            self._history.append(VfsOperation(VfsOperationType.READ, (bytes(buffer),), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.READ, (bytes(buffer),), -1))
            raise

    def write(self, buffer: bytes | bytearray | memoryview) -> int:
        try:
            result = self._handle.write(buffer)
            self._history.append(VfsOperation(VfsOperationType.WRITE, (bytes(buffer),), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.WRITE, (bytes(buffer),), -1))
            raise

    def flush(self) -> bool:
        try:
            result = self._handle.flush()
            self._history.append(VfsOperation(VfsOperationType.FLUSH, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.FLUSH, (), False))
            raise

    def truncate(self, length: int) -> int:
        try:
            result = self._handle.truncate(length)
            self._history.append(VfsOperation(VfsOperationType.TRUNCATE, (length,), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.TRUNCATE, (length,), -1))
            raise


class HistoryDirectoryHandle(DirectoryHandle):
    def __init__(self, handle: DirectoryHandle, history: MutableSequence[VfsOperation]):
        if not isinstance(handle, DirectoryHandle):
            raise TypeError(f"Expected a DirectoryHandle, got {type(handle).__name__}")

        if not isinstance(history, MutableSequence):
            raise TypeError(f"Expected a MutableSequence, got {type(history).__name__}")

        self._handle = handle
        self._history = history

    def close(self) -> bool:
        try:
            result = self._handle.close()
            self._history.append(VfsOperation(VfsOperationType.CLOSEDIR, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.CLOSEDIR, (), False))
            raise

    def readdir(self) -> DirEntry | None:
        try:
            result = self._handle.readdir()
            self._history.append(VfsOperation(VfsOperationType.READDIR, (), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.READDIR, (), None))
            raise


class HistoryFileSystemInterface(FileSystemInterface):
    def __init__(self, interface: FileSystemInterface):
        super().__init__(None)
        if not isinstance(interface, FileSystemInterface):
            raise TypeError(f"Expected a FileSystemInterface, got {type(interface).__name__}")

        self._interface = interface
        self._history: list[VfsOperation] = []

    @property
    def version(self) -> int:
        return self._interface.version

    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> FileHandle | None:
        try:
            wrapped_handle = self._interface.open(path, mode, hints)
            if not wrapped_handle:
                self._history.append(
                    VfsOperation(VfsOperationType.OPEN, (path, mode, hints), None)
                )
                return None

            handle = HistoryFileHandle(wrapped_handle, self._history)
            self._history.append(
                VfsOperation(VfsOperationType.OPEN, (path, mode, hints), wrapped_handle)
            )
            return handle
        except:
            self._history.append(VfsOperation(VfsOperationType.OPEN, (path, mode, hints), None))
            raise

    def remove(self, path: bytes) -> bool:
        try:
            result = self._interface.remove(path)
            self._history.append(VfsOperation(VfsOperationType.REMOVE, (path,), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.REMOVE, (path,), False))
            raise

    def rename(self, old_path: bytes, new_path: bytes) -> bool:
        try:
            result = self._interface.rename(old_path, new_path)
            self._history.append(
                VfsOperation(VfsOperationType.RENAME, (old_path, new_path), result)
            )
            return result
        except:
            self._history.append(
                VfsOperation(VfsOperationType.RENAME, (old_path, new_path), False)
            )
            raise

    def stat(self, path: bytes) -> tuple[VfsStat, int] | None:
        try:
            result = self._interface.stat(path)
            self._history.append(VfsOperation(VfsOperationType.STAT, (path,), result))
            return result
        except:
            self._history.append(VfsOperation(VfsOperationType.STAT, (path,), None))
            raise

    def mkdir(self, path: bytes) -> VfsMkdirResult:
        try:
            result = self._interface.mkdir(path)
            self._history.append(VfsOperation(VfsOperationType.MKDIR, (path,), result))
            return result
        except:
            self._history.append(
                VfsOperation(VfsOperationType.MKDIR, (path,), VfsMkdirResult.ERROR)
            )
            raise

    def opendir(self, path: bytes, include_hidden: bool) -> DirectoryHandle | None:
        try:
            handle = self._interface.opendir(path, include_hidden)
            self._history.append(
                VfsOperation(VfsOperationType.OPENDIR, (path, include_hidden), handle)
            )
            return handle
        except:
            self._history.append(
                VfsOperation(VfsOperationType.OPENDIR, (path, include_hidden), None)
            )
            raise

    @property
    def history(self) -> Sequence[VfsOperation]:
        return tuple(self._history)


__all__ = [
    "HistoryFileHandle",
    "HistoryDirectoryHandle",
    "HistoryFileSystemInterface",
    "VfsOperationType",
    "VfsOperation",
]
