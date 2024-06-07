from abc import abstractmethod
from ctypes import POINTER, c_int32, c_void_p, cast
from logging import Logger
from typing import NamedTuple, Protocol, runtime_checkable

from libretro.api._utils import memoryview_at
from libretro.api.vfs import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsMkdirResult,
    VfsPath,
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

_VFS_SEEK_POSITION_MEMBERS = VfsSeekPosition.__members__.values()
_VFS_MKDIR_RESULT_MEMBERS = VfsMkdirResult.__members__.values()


@runtime_checkable
class FileHandle(Protocol):
    @abstractmethod
    def __init__(self, path: VfsPath, mode: VfsFileAccess, hints: VfsFileAccessHint):
        self._as_parameter_ = id(self)

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
    def read(self, buffer: bytearray | memoryview) -> int: ...

    @abstractmethod
    def write(self, buffer: bytes | bytearray | memoryview) -> int: ...

    @abstractmethod
    def flush(self) -> bool: ...

    @abstractmethod
    def truncate(self, length: int) -> int: ...


class DirEntry(NamedTuple):
    name: bytes
    is_dir: bool


@runtime_checkable
class DirectoryHandle(Protocol):
    @abstractmethod
    def __init__(self, dir: bytes, include_hidden: bool):
        self._as_parameter_ = id(self)
        self._current_dirent: DirEntry | None = None

    @abstractmethod
    def close(self) -> bool: ...  # Corresponds to closedir

    def __iter__(self):
        return self

    def __next__(self) -> DirEntry:
        self._current_dirent = self.readdir()
        if self._current_dirent is None:
            raise StopIteration

        return self._current_dirent

    @abstractmethod
    def readdir(self) -> DirEntry | None: ...

    def dirent_name(self) -> bytes | None:
        """
        Returns the most recent directory entry returned by readdir
        """
        return self._current_dirent and self._current_dirent.name

    def dirent_is_dir(self) -> bool:
        """
        Returns whether the most recent directory entry returned by readdir is a directory
        """
        return bool(self._current_dirent and self._current_dirent.is_dir)


@runtime_checkable
class FileSystemInterface(Protocol):
    @abstractmethod
    def __init__(self, logger: Logger | None = None):
        self.__file_handles: dict[int, FileHandle] = dict()
        self.__dir_handles: dict[int, DirectoryHandle] = dict()
        if not isinstance(logger, (Logger, type(None))):
            raise TypeError(
                f"Expected logger to be a Logger or None, got: {type(logger).__name__}"
            )

        self._logger = logger
        self.__interface: retro_vfs_interface | None = None

    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def open(
        self, path: bytes, mode: VfsFileAccess, hints: VfsFileAccessHint
    ) -> FileHandle | None: ...

    @abstractmethod
    def remove(self, path: bytes) -> bool: ...

    @abstractmethod
    def rename(self, old_path: bytes, new_path: bytes) -> bool: ...

    @abstractmethod
    def stat(self, path: bytes) -> tuple[VfsStat, int] | None: ...

    @abstractmethod
    def mkdir(self, path: bytes) -> VfsMkdirResult: ...

    @abstractmethod
    def opendir(self, path: bytes, include_hidden: bool) -> DirectoryHandle | None: ...

    @property
    def _as_parameter_(self) -> retro_vfs_interface:
        if not self.__interface:
            self.__interface: retro_vfs_interface = retro_vfs_interface()
            if self.version >= 1:
                self.__interface.get_path = retro_vfs_get_path_t(self.__get_path)
                self.__interface.open = retro_vfs_open_t(self.__open)
                self.__interface.close = retro_vfs_close_t(self.__close)
                self.__interface.size = retro_vfs_size_t(self.__size)
                self.__interface.tell = retro_vfs_tell_t(self.__tell)
                self.__interface.seek = retro_vfs_seek_t(self.__seek)
                self.__interface.read = retro_vfs_read_t(self.__read)
                self.__interface.write = retro_vfs_write_t(self.__write)
                self.__interface.flush = retro_vfs_flush_t(self.__flush)
                self.__interface.remove = retro_vfs_remove_t(self.__remove)
                self.__interface.rename = retro_vfs_rename_t(self.__rename)

            if self.version >= 2:
                self.__interface.truncate = retro_vfs_truncate_t(self.__truncate)

            if self.version >= 3:
                self.__interface.stat = retro_vfs_stat_t(self.__stat)
                self.__interface.mkdir = retro_vfs_mkdir_t(self.__mkdir)
                self.__interface.opendir = retro_vfs_opendir_t(self.__opendir)
                self.__interface.readdir = retro_vfs_readdir_t(self.__readdir)
                self.__interface.dirent_get_name = retro_vfs_dirent_get_name_t(
                    self.__dirent_get_name
                )
                self.__interface.dirent_is_dir = retro_vfs_dirent_is_dir_t(self.__dirent_is_dir)
                self.__interface.closedir = retro_vfs_closedir_t(self.__closedir)

        return self.__interface

    # These private methods are passed to the core as C function pointers in the _as_parameter_ property;
    # we can't propagate exceptions out of here, so we need to catch them and return error codes as appropriate.
    def __get_path(self, stream: POINTER(retro_vfs_file_handle)) -> bytes | None:
        if not stream:
            return None

        address: int = cast(stream, c_void_p).value
        handle = self.__file_handles.get(address, None)
        if not handle:
            return None

        assert isinstance(handle, FileHandle)

        match handle.path:
            case bytes(path):
                return path
            case _ as result:
                raise TypeError(f"Expected path to return a bytes, got: {type(result).__name__}")

    def __open(self, path: bytes, mode: int, hints: int) -> c_void_p | None:
        if not path:
            return None

        assert isinstance(path, bytes)
        assert isinstance(mode, int)
        assert isinstance(hints, int)

        file = self.open(path, VfsFileAccess(mode), VfsFileAccessHint(hints))
        if not file:
            return None

        if not isinstance(file, FileHandle):
            raise TypeError(f"Expected open to return a FileHandle, got: {type(file).__name__}")

        address = id(file)
        self.__file_handles[address] = file

        return address

    def __close(self, stream: POINTER(retro_vfs_file_handle)) -> int:
        if not stream:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.pop(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            ok = handle.close()
            del handle

            return 0 if ok else -1
        except:
            # TODO: Log the exception
            return -1

    def __size(self, stream: POINTER(retro_vfs_file_handle)) -> int:
        if not stream:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            size = handle.size
            if not isinstance(size, int):
                raise TypeError(f"Expected size to return an int, got: {type(size).__name__}")

            return size
        except:
            # TODO: Log the exception
            return -1

    def __tell(self, stream: POINTER(retro_vfs_file_handle)) -> int:
        if not stream:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            pos = handle.tell()
            if not isinstance(pos, int):
                raise TypeError(f"Expected tell to return an int, got: {type(pos).__name__}")

            return pos
        except:
            # TODO: Log the exception
            return -1

    def __seek(self, stream: POINTER(retro_vfs_file_handle), offset: int, whence: int) -> int:
        if not stream:
            return -1

        assert isinstance(offset, int)
        assert isinstance(whence, int)

        if whence not in _VFS_SEEK_POSITION_MEMBERS:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            pos = handle.seek(offset, VfsSeekPosition(whence))
            if not isinstance(pos, int):
                raise TypeError(f"Expected seek to return an int, got: {type(pos).__name__}")

            return pos
        except:
            # TODO: Log the exception
            return -1

    def __read(self, stream: POINTER(retro_vfs_file_handle), buffer: c_void_p, length: int) -> int:
        if not stream:
            return -1

        if not buffer:
            return -1

        # assert isinstance(buffer, c_void_p), f"Expected a c_void_p, got: {type(buffer).__name__}"
        assert isinstance(length, int), f"Expected an int, got: {type(length).__name__}"
        assert length >= 0, f"Expected length to be non-negative, got: {length}"

        if length == 0:
            return 0

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(
                handle, FileHandle
            ), f"Expected a FileHandle, got: {type(handle).__name__}"

            memview = memoryview_at(buffer, length)
            bytes_read = handle.read(memview)
            if not isinstance(bytes_read, int):
                raise TypeError(
                    f"Expected read to return an int, got: {type(bytes_read).__name__}"
                )

            return bytes_read
        except:
            # TODO: Log the exception
            return -1

    def __write(self, stream: POINTER(retro_vfs_file_handle), buffer: int, length: int) -> int:
        if not stream:
            return -1

        if not buffer:
            return -1

        assert isinstance(buffer, int)
        assert isinstance(length, int)
        assert length >= 0

        if length == 0:
            return 0

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            memview = memoryview_at(buffer, length, readonly=True)
            bytes_written = handle.write(memview)
            if not isinstance(bytes_written, int):
                raise TypeError(
                    f"Expected write to return an int, got: {type(bytes_written).__name__}"
                )

            return bytes_written
        except:
            # TODO: Log the exception
            return -1

    def __flush(self, stream: POINTER(retro_vfs_file_handle)) -> int:
        if not stream:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            return 0 if handle.flush() else -1
        except:
            # TODO: Log the exception
            return -1

    def __remove(self, path: bytes) -> int:
        if not path:
            return -1

        assert isinstance(path, bytes)

        try:
            return 0 if self.remove(path) else -1
        except:
            # TODO: Log the exception
            return -1

    def __rename(self, old_path: bytes, new_path: bytes) -> int:
        if not old_path or not new_path:
            return -1

        assert isinstance(old_path, bytes)
        assert isinstance(new_path, bytes)

        try:
            return 0 if self.rename(old_path, new_path) else -1
        except:
            # TODO: Log the exception
            return -1

    def __truncate(self, stream: POINTER(retro_vfs_file_handle), length: int) -> int:
        if not stream:
            return -1

        assert isinstance(length, int)
        if length < 0:
            return -1

        try:
            address: int = cast(stream, c_void_p).value
            handle = self.__file_handles.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, FileHandle)

            return 0 if handle.truncate(length) else -1
        except:
            # TODO: Log the exception
            return -1

    def __stat(self, path: bytes, size: POINTER(c_int32)) -> int:
        if not path:
            return 0

        assert isinstance(path, bytes)

        match self.stat(path):
            case (VfsStat() | int() as flags), int(filesize):
                if size and flags:
                    # size is allowed to be null!
                    size[0] = filesize

                return flags
            case None:
                return 0
            case _:
                # TODO: Log details of the error here
                return 0

    def __mkdir(self, path: bytes) -> int:
        if not path:
            return VfsMkdirResult.ERROR

        assert isinstance(path, bytes)

        try:
            ok = self.mkdir(path)

            if ok not in _VFS_MKDIR_RESULT_MEMBERS:
                raise TypeError(
                    f"Expected mkdir to return a VfsMkdirResult, got: {type(ok).__name__}"
                )

            return ok
        except FileExistsError:
            return VfsMkdirResult.ALREADY_EXISTS
        except:
            # TODO: Log an error here
            return VfsMkdirResult.ERROR

    def __opendir(self, path: bytes, include_hidden: bool) -> c_void_p | None:
        if not path:
            return None

        assert isinstance(path, bytes)
        assert isinstance(include_hidden, bool)

        try:
            dir = self.opendir(path, include_hidden)
            if not dir:
                return None

            if not isinstance(dir, DirectoryHandle):
                raise TypeError(
                    f"Expected opendir to return a DirectoryHandle, got: {type(dir).__name__}"
                )
        except:
            # TODO: Log the exception
            return None

        address = id(dir)
        self.__dir_handles[address] = dir

        return address

    def __readdir(self, dir: POINTER(retro_vfs_dir_handle)) -> bool:
        if not dir:
            return False

        try:
            address: int = cast(dir, c_void_p).value
            handle = self.__dir_handles.get(address, None)
            if not handle:
                return False

            assert isinstance(handle, DirectoryHandle)

            match next(handle, None):
                case None | StopIteration() | False:
                    return False
                case DirEntry():
                    return True  # It's okay, this can be accessed via handle.dirent
                case e:
                    raise TypeError(
                        f"Expected readdir to return a DirEntry or None, got: {type(e).__name__}"
                    )
        except StopIteration:
            # Not an error, just the end of the directory
            return False
        except:
            # TODO: Log the exception
            return False

    def __dirent_get_name(self, dir: POINTER(retro_vfs_dir_handle)) -> bytes | None:
        if not dir:
            return None

        try:
            address: int = cast(dir, c_void_p).value
            handle = self.__dir_handles.get(address, None)
            if not handle:
                return None

            assert isinstance(handle, DirectoryHandle)

            match handle.dirent_name():
                case (bytes() | None) as name:
                    return name
                case _ as name:
                    raise TypeError(
                        f"Expected dirent_name to return a bytes or None, got: {type(name).__name__}"
                    )
        except:
            # TODO: Log the exception
            return None

    def __dirent_is_dir(self, dir: POINTER(retro_vfs_dir_handle)) -> bool:
        if not dir:
            return False

        try:
            address: int = cast(dir, c_void_p).value
            handle = self.__dir_handles.get(address, None)
            if not handle:
                return False

            assert isinstance(handle, DirectoryHandle)

            return handle.dirent_is_dir()
        except:
            # TODO: Log the exception
            return False

    def __closedir(self, dir: POINTER(retro_vfs_dir_handle)) -> int:
        if not dir:
            return -1

        try:
            address: int = cast(dir, c_void_p).value
            handle = self.__dir_handles.pop(address, None)
            if not handle:
                return -1

            assert isinstance(handle, DirectoryHandle)

            del handle
            return 0
        except:
            # TODO: Log the exception
            return -1


__all__ = ["FileHandle", "DirectoryHandle", "FileSystemInterface", "DirEntry"]
