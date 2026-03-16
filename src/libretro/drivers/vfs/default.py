import os
import stat
from io import FileIO
from os import DirEntry
from typing import Literal, override

from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsSeekPosition,
    VfsStat,
    retro_vfs_dir_handle,
    retro_vfs_file_handle,
)

from .interface import DirectoryHandle, FileHandle, FileSystemInterface


class StandardFileHandle(FileHandle):
    @override
    def __init__(self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint):
        if not path:
            raise ValueError("Expected a non-empty path")

        self._path = path
        self._file = FileIO(path, mode.open_flag)

    def __del__(self):
        self.close()

    @override
    def close(self) -> bool:
        if self._file is not None:
            self._file.close()
            del self._file
            self._file = None

        return True

    @property
    @override
    def path(self) -> bytes:
        if not self._file:
            raise IOError("File is closed")

        return self._path

    @property
    @override
    def size(self) -> int:
        if not self._file:
            raise IOError("File is closed")

        stat = os.stat(self._file.fileno())
        return stat.st_size

    @override
    def tell(self) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.tell()

    @override
    def seek(self, offset: int, whence: VfsSeekPosition) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.seek(offset, whence)

    @override
    def read(self, buffer: bytearray | memoryview) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.readinto(buffer)

    @override
    def write(self, buffer: bytes | bytearray | memoryview) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.write(buffer)

    @override
    def flush(self) -> bool:
        if not self._file:
            raise IOError("File is closed")

        self._file.flush()
        os.fsync(self._file.fileno())
        return True

    @override
    def truncate(self, length: int) -> int:
        if not self._file:
            raise IOError("File is closed")

        return self._file.truncate(length)

    @property
    def _as_parameter_(self):
        if not self._file:
            raise IOError("File is closed")

        return self._file.fileno()


class StandardDirectoryHandle(DirectoryHandle):
    @override
    def __init__(self, path: bytes, include_hidden: bool):
        self._scandir = os.scandir(path)
        self._dirent: DirEntry[bytes] | None = None
        self._include_hidden = include_hidden

    def __del__(self):
        self.closedir()

    @override
    def readdir(self) -> bool:
        if not self._scandir:
            raise IOError("Directory is closed")

        # TODO: If include_hidden is False,
        # keep iterating until we find a non-hidden entry or reach the end of the directory
        self._dirent = next(self._scandir, None)
        return self._dirent is not None

    @property
    @override
    def dirent_name(self) -> bytes | None:
        if not self._scandir:
            raise IOError("Directory is closed")

        if not self._dirent:
            return None

        return self._dirent.name

    @property
    @override
    def dirent_is_dir(self) -> bool:
        if not self._scandir:
            raise IOError("Directory is closed")

        if not self._dirent:
            raise ValueError("No directory entry available")

        return self._dirent.is_dir()

    @override
    def closedir(self) -> bool:
        if self._scandir:
            self._scandir.close()
            del self._scandir
            self._scandir = None

        return True

    @property
    def _as_parameter_(self):
        if not self._scandir:
            raise IOError("Directory is closed")

        return id(self._scandir)


class StandardFileSystemInterface(FileSystemInterface):
    _file_handles: dict[int, StandardFileHandle]
    _dir_handles: dict[int, StandardDirectoryHandle]

    def __init__(self, version: Literal[1, 2, 3] = 3):
        self._version = version
        self._file_handles = {}
        self._dir_handles = {}

    @override
    def get_path(self, stream: retro_vfs_file_handle) -> bytes | None:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return None

        return file.path

    @override
    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> retro_vfs_file_handle | None:
        file = StandardFileHandle(path, mode, hints)
        handle = id(file)
        self._file_handles[handle] = file
        return retro_vfs_file_handle(handle)

    @override
    def close(self, stream: retro_vfs_file_handle) -> int:
        handle = stream.id
        file = self._file_handles.pop(handle, None)
        if not file:
            return -1

        file.close()
        return 0

    @override
    def size(self, stream: retro_vfs_file_handle) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.size

    @override
    def truncate(self, stream: retro_vfs_file_handle, length: int) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.truncate(length)

    @override
    def tell(self, stream: retro_vfs_file_handle) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.tell()

    @override
    def seek(self, stream: retro_vfs_file_handle, offset: int, whence: VfsSeekPosition) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.seek(offset, whence)

    @override
    def read(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.read(buffer)

    @override
    def write(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return -1

        return file.write(buffer)

    @override
    def flush(self, stream: retro_vfs_file_handle) -> bool:
        handle = stream.id
        file = self._file_handles.get(handle)
        if not file:
            return False

        return file.flush()

    @override
    def remove(self, path: bytes) -> bool:
        os.remove(path)
        return True

    @override
    def rename(self, old_path: bytes, new_path: bytes) -> bool:
        os.rename(old_path, new_path)
        return True

    @override
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

    @override
    def mkdir(self, path: bytes) -> VfsMkdirResult:
        try:
            os.mkdir(path)
            return VfsMkdirResult.SUCCESS
        except FileExistsError:
            return VfsMkdirResult.ALREADY_EXISTS
        except OSError:
            return VfsMkdirResult.ERROR

    @override
    def opendir(self, path: bytes, include_hidden: bool) -> retro_vfs_dir_handle | None:
        dir_handle = StandardDirectoryHandle(path, include_hidden)
        handle = id(dir_handle)
        self._dir_handles[handle] = dir_handle
        return retro_vfs_dir_handle(handle)

    @override
    def readdir(self, dir: retro_vfs_dir_handle) -> bool:
        handle = dir.id
        dir_handle = self._dir_handles.get(handle)
        if not dir_handle:
            return False

        return dir_handle.readdir()

    @override
    def dirent_get_name(self, dir: retro_vfs_dir_handle) -> bytes | None:
        handle = dir.id
        dir_handle = self._dir_handles.get(handle)
        if not dir_handle:
            return None

        return dir_handle.dirent_name

    @override
    def dirent_is_dir(self, dir: retro_vfs_dir_handle) -> bool:
        handle = dir.id
        dir_handle = self._dir_handles.get(handle)
        if not dir_handle:
            return False

        return dir_handle.dirent_is_dir

    @override
    def closedir(self, dir: retro_vfs_dir_handle) -> bool:
        handle = dir.id
        dir_handle = self._dir_handles.pop(handle, None)
        if not dir_handle:
            return False

        return dir_handle.closedir()

    @property
    @override
    def version(self) -> int:
        return self._version


__all__ = [
    "StandardFileHandle",
    "StandardDirectoryHandle",
    "StandardFileSystemInterface",
]
