from abc import abstractmethod
from typing import Protocol, runtime_checkable
from warnings import deprecated

from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsSeekPosition,
    VfsStat,
    retro_vfs_close_t,
    retro_vfs_closedir_t,
    retro_vfs_dir_handle,
    retro_vfs_dirent_get_name_t,
    retro_vfs_dirent_is_dir_t,
    retro_vfs_file_handle,
    retro_vfs_flush_t,
    retro_vfs_get_path_t,
    retro_vfs_interface,
    retro_vfs_mkdir_t,
    retro_vfs_open_t,
    retro_vfs_opendir_t,
    retro_vfs_read_t,
    retro_vfs_readdir_t,
    retro_vfs_remove_t,
    retro_vfs_rename_t,
    retro_vfs_seek_t,
    retro_vfs_size_t,
    retro_vfs_stat_t,
    retro_vfs_tell_t,
    retro_vfs_truncate_t,
    retro_vfs_write_t,
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

    @property
    @deprecated("Create the retro_vfs_interface in EnvironmentDriver instead of here")
    def _as_parameter_(self) -> retro_vfs_interface:
        interface = retro_vfs_interface()

        if self.version >= 1:
            interface.get_path = retro_vfs_get_path_t(self.get_path)
            interface.open = retro_vfs_open_t(self.open)
            interface.close = retro_vfs_close_t(self.close)
            interface.size = retro_vfs_size_t(self.size)
            interface.tell = retro_vfs_tell_t(self.tell)
            interface.seek = retro_vfs_seek_t(self.seek)
            interface.read = retro_vfs_read_t(self.read)
            interface.write = retro_vfs_write_t(self.write)
            interface.flush = retro_vfs_flush_t(self.flush)
            interface.remove = retro_vfs_remove_t(self.remove)
            interface.rename = retro_vfs_rename_t(self.rename)

        if self.version >= 2:
            interface.truncate = retro_vfs_truncate_t(self.truncate)

        if self.version >= 3:
            interface.stat = retro_vfs_stat_t(self.stat)
            interface.mkdir = retro_vfs_mkdir_t(self.mkdir)
            interface.opendir = retro_vfs_opendir_t(self.opendir)
            interface.readdir = retro_vfs_readdir_t(self.readdir)
            interface.dirent_get_name = retro_vfs_dirent_get_name_t(self.dirent_get_name)
            interface.dirent_is_dir = retro_vfs_dirent_is_dir_t(self.dirent_is_dir)
            interface.closedir = retro_vfs_closedir_t(self.closedir)

        return interface


__all__ = ["FileSystemInterface", "FileHandle", "DirectoryHandle"]
