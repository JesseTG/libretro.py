import os

from abc import abstractmethod
from ctypes import *
from enum import IntFlag, IntEnum
from io import FileIO
from typing import Protocol, Literal, runtime_checkable

from .._utils import UNCHECKED, String, FieldsFromTypeHints
from ..h import *


class retro_vfs_file_handle(Structure):
    pass


class retro_vfs_dir_handle(Structure):
    pass


retro_vfs_get_path_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_file_handle))
retro_vfs_open_t = CFUNCTYPE(UNCHECKED(POINTER(retro_vfs_file_handle)), String, c_uint, c_uint)
retro_vfs_close_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_size_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_truncate_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64)
retro_vfs_tell_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_seek_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64, c_int)
retro_vfs_read_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_write_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_flush_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_remove_t = CFUNCTYPE(c_int, String)
retro_vfs_rename_t = CFUNCTYPE(c_int, String, String)
retro_vfs_stat_t = CFUNCTYPE(c_int, String, POINTER(c_int32))
retro_vfs_mkdir_t = CFUNCTYPE(c_int, String)
retro_vfs_opendir_t = CFUNCTYPE(UNCHECKED(POINTER(retro_vfs_dir_handle)), String, c_bool)
retro_vfs_readdir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_get_name_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_is_dir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_closedir_t = CFUNCTYPE(c_int, POINTER(retro_vfs_dir_handle))


class retro_vfs_interface(Structure, metaclass=FieldsFromTypeHints):
    get_path: retro_vfs_get_path_t
    open: retro_vfs_open_t
    close: retro_vfs_close_t
    size: retro_vfs_size_t
    tell: retro_vfs_tell_t
    seek: retro_vfs_seek_t
    read: retro_vfs_read_t
    write: retro_vfs_write_t
    flush: retro_vfs_flush_t
    remove: retro_vfs_remove_t
    rename: retro_vfs_rename_t
    truncate: retro_vfs_truncate_t
    stat: retro_vfs_stat_t
    mkdir: retro_vfs_mkdir_t
    opendir: retro_vfs_opendir_t
    readdir: retro_vfs_readdir_t
    dirent_get_name: retro_vfs_dirent_get_name_t
    dirent_is_dir: retro_vfs_dirent_is_dir_t
    closedir: retro_vfs_closedir_t


class retro_vfs_interface_info(Structure, metaclass=FieldsFromTypeHints):
    required_interface_version: c_uint32
    iface: POINTER(retro_vfs_interface)


class VfsFileAccess(IntFlag):
    READ = RETRO_VFS_FILE_ACCESS_READ
    WRITE = RETRO_VFS_FILE_ACCESS_WRITE
    READ_WRITE = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UPDATE_EXISTING = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING

    def __init__(self, value: int):
        self._type_ = 'I'


class VfsFileAccessHint(IntFlag):
    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS

    def __init__(self, value: int):
        self._type_ = 'I'


class VfsSeekPosition(IntEnum):
    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END

    def __init__(self, value: int):
        self._type_ = 'I'


class VfsStat(IntFlag):
    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL

    def __init__(self, value: int):
        self._type_ = 'I'


class FileHandle:
    def __init__(self, file: FileIO):
        self.file = file
        self._as_parameter_ = c_void_p(id(self))


class DirectoryHandle:
    pass


@runtime_checkable
class FileSystemInterface(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def get_path(self, stream: FileHandle) -> bytes: ...

    @abstractmethod
    def open(self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint) -> FileHandle: ...

    @abstractmethod
    def close(self, stream: FileHandle) -> int: ...

    @abstractmethod
    def size(self, stream: FileHandle) -> int: ...

    @abstractmethod
    def tell(self, stream: FileHandle) -> int: ...

    @abstractmethod
    def seek(self, stream: FileHandle, offset: int, whence: VfsSeekPosition) -> int: ...

    @abstractmethod
    def read(self, stream: FileHandle, buffer: c_void_p, length: int) -> int: ...

    @abstractmethod
    def write(self, stream: FileHandle, buffer: c_void_p, length: int) -> int: ...

    @abstractmethod
    def flush(self, stream: FileHandle) -> int: ...

    @abstractmethod
    def remove(self, path: bytes) -> int: ...

    @abstractmethod
    def rename(self, old_path: bytes, new_path: bytes) -> int: ...

    @abstractmethod
    def truncate(self, stream: FileHandle, length: int) -> int: ...

    @abstractmethod
    def stat(self, path: bytes, size: c_int32) -> VfsStat: ...

    @abstractmethod
    def mkdir(self, path: bytes) -> int: ...

    @abstractmethod
    def opendir(self, path: bytes, include_hidden: bool) -> DirectoryHandle: ...

    @abstractmethod
    def readdir(self, dir: DirectoryHandle) -> bytes: ...

    @abstractmethod
    def dirent_get_name(self, dir: DirectoryHandle) -> bytes: ...

    @abstractmethod
    def dirent_is_dir(self, dir: DirectoryHandle) -> bool: ...

    @abstractmethod
    def closedir(self, dir: DirectoryHandle) -> int: ...


class PythonFileSystemInterface(FileSystemInterface):
    def __init__(self, version: Literal[1, 2, 3] = 3):
        self._version = version
        self._file_handles: set[FileHandle] = set()
        self._dir_handles: set[DirectoryHandle] = set()

        self._as_parameter_ = retro_vfs_interface()
        if version >= 1:
            self._as_parameter_.get_path = retro_vfs_get_path_t(self.get_path)
            self._as_parameter_.open = retro_vfs_open_t(self.open)
            self._as_parameter_.close = retro_vfs_close_t(self.close)
            self._as_parameter_.size = retro_vfs_size_t(self.size)
            self._as_parameter_.tell = retro_vfs_tell_t(self.tell)
            self._as_parameter_.seek = retro_vfs_seek_t(self.seek)
            self._as_parameter_.read = retro_vfs_read_t(self.read)
            self._as_parameter_.write = retro_vfs_write_t(self.write)
            self._as_parameter_.flush = retro_vfs_flush_t(self.flush)
            self._as_parameter_.remove = retro_vfs_remove_t(self.remove)
            self._as_parameter_.rename = retro_vfs_rename_t(self.rename)

        if version >= 2:
            self._as_parameter_.truncate = retro_vfs_truncate_t(self.truncate)

        if version >= 3:
            self._as_parameter_.stat = retro_vfs_stat_t(self.stat)
            self._as_parameter_.mkdir = retro_vfs_mkdir_t(self.mkdir)
            self._as_parameter_.opendir = retro_vfs_opendir_t(self.opendir)
            self._as_parameter_.readdir = retro_vfs_readdir_t(self.readdir)
            self._as_parameter_.dirent_get_name = retro_vfs_dirent_get_name_t(self.dirent_get_name)
            self._as_parameter_.dirent_is_dir = retro_vfs_dirent_is_dir_t(self.dirent_is_dir)
            self._as_parameter_.closedir = retro_vfs_closedir_t(self.closedir)

    @property
    def version(self) -> int:
        return self._version

    def get_path(self, stream: FileHandle) -> bytes | None:
        if not stream or stream not in self._file_handles:
            return None

        return stream.file.name

    def open(self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint) -> FileHandle | None:
        if path is None:
            return None

        try:
            file = FileIO(path, mode.to_str())
            handle = FileHandle(file)
            self._file_handles.add(handle)
            return handle
        except OSError as e:
            print(e)
            return None

    def close(self, stream: FileHandle) -> int:
        if not stream or stream not in self._file_handles:
            return -1

        self._file_handles.remove(stream)
        stream.file.close()
        del stream
        return 0

    def size(self, stream: FileHandle) -> int:
        if not stream or stream not in self._file_handles or not stream.file.seekable():
            return -1

        pos = stream.file.tell()
        size = stream.file.seek(0, os.SEEK_END)
        stream.file.seek(pos, os.SEEK_SET)

        return size

    def truncate(self, stream: FileHandle, length: int) -> int:
        if not stream or stream not in self._file_handles:
            return -1

        if not stream.file.seekable() or not stream.file.writable():
            return -1

        if length < 0:
            return -1

        stream.file.truncate(length)
        return 0

    def tell(self, stream: FileHandle) -> int:
        if not stream or stream not in self._file_handles or not stream.file.seekable():
            return -1

        return stream.file.tell()

    def seek(self, stream: FileHandle, offset: int, whence: VfsSeekPosition) -> int:
        if not stream or stream not in self._file_handles or not stream.file.seekable():
            return -1

        try:
            return stream.file.seek(offset, whence)
        except OSError as e:
            return -1

    def read(self, stream: FileHandle, buffer: c_void_p, length: int) -> int:
        if not stream or stream not in self._file_handles or not stream.file.readable():
            return -1

        if not buffer:
            return -1

        try:
            data = stream.file.read(length)
            memmove(buffer, data, len(data))
            return len(data)
        except OSError as e:
            return -1

    def write(self, stream: FileHandle, buffer: c_void_p, length: int) -> int:
        if not stream or stream not in self._file_handles or not stream.file.writable():
            return -1

        if not buffer:
            return -1

        # TODO: Implement write

    def flush(self, stream: FileHandle) -> int:
        if not stream or stream not in self._file_handles:
            return -1

        try:
            stream.file.flush()
            return 0
        except OSError as e:
            return -1

    def remove(self, path: bytes) -> int:
        if not path:
            return -1

        try:
            os.remove(path)
            return 0
        except OSError as e:
            return -1

    def rename(self, old_path: bytes, new_path: bytes) -> int:
        if not old_path or not new_path:
            return -1

        try:
            os.rename(old_path, new_path)
            return 0
        except OSError as e:
            return -1

    def stat(self, path: bytes, size: c_int32) -> VfsStat:
        if not path:
            return -1

        stat = os.stat(path)
        if size:
            size.value = stat.st_size

        # TODO: Implement stat

    def mkdir(self, path: bytes) -> int:
        if not path:
            return -1

        try:
            os.mkdir(path)
            return 0
        except FileExistsError:
            return -2
        except OSError as e:
            return -1