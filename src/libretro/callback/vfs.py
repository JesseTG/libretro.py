from abc import abstractmethod
from io import FileIO
import os
from typing import Protocol, Literal
from ..retro import *
from ..defs import *


class FileHandle:
    def __init__(self, file: FileIO):
        self.file = file
        self._as_parameter_ = c_void_p(id(self))

class DirectoryHandle:
    pass

class FileSystemInterfaceV1(Protocol):
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


class FileSystemInterfaceV2(FileSystemInterfaceV1, Protocol):
    @abstractmethod
    def truncate(self, stream: FileHandle, length: int) -> int: ...


class FileSystemInterfaceV3(FileSystemInterfaceV2, Protocol):
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


class PythonFileSystemInterface(FileSystemInterfaceV3):
    def __init__(self, version: Literal[1, 2, 3] = 3):
        self._version = version
        self._file_handles: set[FileHandle] = set()
        self._dir_handles: set[DirectoryHandle] = set()

        self._as_parameter_ = retro_vfs_interface()
        if version >= 1:
            self._as_parameter_.get_path = self.get_path
            self._as_parameter_.open = self.open
            self._as_parameter_.close = self.close
            self._as_parameter_.size = self.size
            self._as_parameter_.tell = self.tell
            self._as_parameter_.seek = self.seek
            self._as_parameter_.read = self.read
            self._as_parameter_.write = self.write
            self._as_parameter_.flush = self.flush
            self._as_parameter_.remove = self.remove
            self._as_parameter_.rename = self.rename

        if version >= 2:
            self._as_parameter_.truncate = self.truncate

        if version >= 3:
            self._as_parameter_.stat = self.stat
            self._as_parameter_.mkdir = self.mkdir
            self._as_parameter_.opendir = self.opendir
            self._as_parameter_.readdir = self.readdir
            self._as_parameter_.dirent_get_name = self.dirent_get_name
            self._as_parameter_.dirent_is_dir = self.dirent_is_dir
            self._as_parameter_.closedir = self.closedir

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