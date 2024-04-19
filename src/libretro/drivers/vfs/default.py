import os
import stat
from io import FileIO
from logging import Logger
from typing import Literal

from libretro.api._utils import as_bytes
from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsPath,
    VfsSeekPosition,
    VfsStat,
)

from .interface import DirectoryHandle, DirEntry, FileHandle, FileSystemInterface


class StandardFileHandle(FileHandle):
    def __init__(self, path: VfsPath, mode: VfsFileAccess, hints: VfsFileAccessHint):
        super().__init__(path, mode, hints)
        self._file: FileIO | None = None
        if not path:
            raise ValueError("Expected a non-empty path")

        self._file = FileIO(as_bytes(path), mode.open_flag)

    def __del__(self):
        self.close()

    def close(self) -> bool:
        if self._file is not None:
            self._file.close()
            del self._file
            self._file = None

        return True

    @property
    def path(self) -> bytes:
        if not self._file:
            raise IOError("File is closed")

        return self._file.name

    @property
    def size(self) -> int:
        if not self._file:
            raise IOError("File is closed")

        position = self._file.tell()
        size = self._file.seek(0, os.SEEK_END)
        self._file.seek(position, os.SEEK_SET)

        return size

    def tell(self) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.tell()

    def seek(self, offset: int, whence: VfsSeekPosition) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.seek(offset, whence)

    def read(self, buffer: bytearray | memoryview) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.readinto(buffer)

    def write(self, buffer: bytes | bytearray | memoryview) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.write(buffer)

    def flush(self) -> bool:
        if not self._file:
            raise IOError("File is closed")

        self._file.flush()
        os.fsync(self._file.fileno())
        return True

    def truncate(self, length: int) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.truncate(length)


class StandardDirectoryHandle(DirectoryHandle):
    def __init__(self, path: VfsPath, include_hidden: bool):
        super().__init__(path, include_hidden)
        self._dirent = os.scandir(path)

    def __del__(self):
        self.close()

    def close(self) -> bool:
        if self._dirent:
            self._dirent.close()
            del self._dirent
            self._dirent = None

        return True

    def readdir(self) -> DirEntry | None:
        dirent: os.DirEntry | None = next(self._dirent, None)
        if not dirent:
            return None

        return DirEntry(dirent.name, dirent.is_dir())


class StandardFileSystemInterface(FileSystemInterface):
    def __init__(self, version: Literal[1, 2, 3] = 3, logger: Logger | None = None):
        super().__init__(logger)
        self._version = version

    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> FileHandle | None:
        try:
            handle = StandardFileHandle(path, mode, hints)
            return handle
        except OSError as e:
            return None

    def remove(self, path: bytes) -> bool:
        os.remove(path)
        return True

    def rename(self, old_path: bytes, new_path: bytes) -> bool:
        os.rename(old_path, new_path)
        return True

    def stat(self, path: bytes) -> tuple[VfsStat, int] | None:
        try:
            filestat = os.stat(path)
            flags = VfsStat(0)

            if stat.S_ISREG(filestat.st_mode):
                flags |= VfsStat.IS_VALID

            if stat.S_ISDIR(filestat.st_mode):
                flags |= VfsStat.IS_DIRECTORY

            if stat.S_ISCHR(filestat.st_mode):
                flags |= VfsStat.IS_CHARACTER_SPECIAL

            return flags, filestat.st_size
        except FileNotFoundError:
            return VfsStat(0), 0

    def mkdir(self, path: bytes) -> VfsMkdirResult:
        try:
            os.mkdir(path)
            return VfsMkdirResult.SUCCESS
        except FileExistsError:
            return VfsMkdirResult.ALREADY_EXISTS
        except OSError:
            return VfsMkdirResult.ERROR

    def opendir(self, path: bytes, include_hidden: bool) -> DirectoryHandle | None:
        return StandardDirectoryHandle(path, include_hidden)

    @property
    def version(self) -> int:
        return self._version


__all__ = [
    "StandardFileHandle",
    "StandardDirectoryHandle",
    "StandardFileSystemInterface",
]
