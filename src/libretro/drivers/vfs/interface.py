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
    def __init__(self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint): ...

    @abstractmethod
    def close(self) -> bool: ...

    @property
    @abstractmethod
    def path(self) -> bytes: ...

    @property
    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def tell(self) -> int: ...

    @abstractmethod
    def seek(self, offset: int, whence: VfsSeekPosition) -> int: ...

    @abstractmethod
    def read(self, buffer: memoryview[int]) -> int: ...

    @abstractmethod
    def write(self, buffer: memoryview[int]) -> int: ...

    @abstractmethod
    def flush(self) -> bool: ...

    @abstractmethod
    def truncate(self, length: int) -> bool: ...


@runtime_checkable
class DirectoryHandle(Protocol):
    @abstractmethod
    def __init__(self, dir: bytes, include_hidden: bool): ...

    @abstractmethod
    def readdir(self) -> bool: ...

    @property
    @abstractmethod
    def dirent_name(self) -> bytes | None: ...

    @property
    @abstractmethod
    def dirent_is_dir(self) -> bool: ...

    @abstractmethod
    def closedir(self) -> bool: ...


@runtime_checkable
class FileSystemInterface(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def get_path(self, stream: retro_vfs_file_handle) -> bytes | None: ...

    @abstractmethod
    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> retro_vfs_file_handle | None: ...

    @abstractmethod
    def close(self, stream: retro_vfs_file_handle) -> bool: ...

    @abstractmethod
    def size(self, stream: retro_vfs_file_handle) -> int: ...

    @abstractmethod
    def truncate(self, stream: retro_vfs_file_handle, length: int) -> bool: ...

    @abstractmethod
    def tell(self, stream: retro_vfs_file_handle) -> int: ...

    @abstractmethod
    def seek(self, stream: retro_vfs_file_handle, offset: int, whence: VfsSeekPosition) -> int: ...

    @abstractmethod
    def read(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int: ...

    @abstractmethod
    def write(self, stream: retro_vfs_file_handle, buffer: memoryview[int]) -> int: ...

    @abstractmethod
    def flush(self, stream: retro_vfs_file_handle) -> bool: ...

    @abstractmethod
    def remove(self, path: bytes) -> bool: ...

    @abstractmethod
    def rename(self, old_path: bytes, new_path: bytes) -> bool: ...

    @abstractmethod
    def stat(self, path: bytes) -> tuple[VfsStat, int] | None: ...

    @abstractmethod
    def mkdir(self, path: bytes) -> VfsMkdirResult: ...

    @abstractmethod
    def opendir(self, path: bytes, include_hidden: bool) -> retro_vfs_dir_handle | None: ...

    @abstractmethod
    def readdir(self, dir: retro_vfs_dir_handle) -> bool: ...

    @abstractmethod
    def dirent_get_name(self, dir: retro_vfs_dir_handle) -> bytes | None: ...

    @abstractmethod
    def dirent_is_dir(self, dir: retro_vfs_dir_handle) -> bool: ...

    @abstractmethod
    def closedir(self, dir: retro_vfs_dir_handle) -> bool: ...


__all__ = ["FileSystemInterface", "FileHandle", "DirectoryHandle"]
