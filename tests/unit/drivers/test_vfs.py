"""
Tests for the ``ctypes`` bridge between a core and a :class:`.FileSystemDriver`.

These drive :class:`.CompositeEnvironmentDriver`'s VFS interface
through its C function pointers,
exactly the way a core would after ``RETRO_ENVIRONMENT_GET_VFS_INTERFACE``.
No core is loaded.
"""

from __future__ import annotations

import warnings
from ctypes import CFUNCTYPE, byref, c_void_p, cast
from pathlib import Path

import pytest

from libretro import (
    ArrayAudioDriver,
    ArrayVideoDriver,
    CompositeEnvironmentDriver,
    DefaultFileSystemDriver,
    EnvironmentCall,
    IterableInputDriver,
)
from libretro.api import (
    VfsFileAccess,
    VfsFileAccessHint,
    retro_vfs_dir_handle,
    retro_vfs_file_handle,
    retro_vfs_interface,
    retro_vfs_interface_info,
)
from libretro.ctypes import TypedPointer


@pytest.fixture
def vfs_driver() -> DefaultFileSystemDriver:
    return DefaultFileSystemDriver()


@pytest.fixture
def env(vfs_driver: DefaultFileSystemDriver) -> CompositeEnvironmentDriver:
    return CompositeEnvironmentDriver(
        audio=ArrayAudioDriver(),
        input=IterableInputDriver(),
        video=ArrayVideoDriver(),
        vfs=vfs_driver,
    )


def _get_vfs(env: CompositeEnvironmentDriver) -> retro_vfs_interface:
    info = retro_vfs_interface_info(3, None)
    assert env.environment(EnvironmentCall.GET_VFS_INTERFACE, cast(byref(info), c_void_p))
    assert info.iface
    return info.iface[0]


def test_dir_handle_outlives_opendir(env: CompositeEnvironmentDriver, tmp_path: Path) -> None:
    """
    The handle returned by ``opendir`` must stay valid until ``closedir``.

    The address handed to the core points at a ``retro_vfs_dir_handle``
    that Python constructed inside the ``opendir`` callback.
    If nothing on the frontend side keeps that object alive,
    the core is left holding a pointer into freed memory,
    and directory enumeration silently truncates
    whenever the allocator happens to reuse the block --
    the cause of nondeterministic, platform-dependent lost entries.
    """
    names = {f"file{i}.bin".encode() for i in range(8)}
    for name in names:
        (tmp_path / name.decode()).write_bytes(b"\x00" * 16)

    vfs = _get_vfs(env)
    opendir = vfs.opendir
    readdir = vfs.readdir
    dirent_get_name = vfs.dirent_get_name
    closedir = vfs.closedir
    assert opendir is not None
    assert readdir is not None
    assert dirent_get_name is not None
    assert closedir is not None

    handle = cast(opendir(bytes(tmp_path), True), TypedPointer[retro_vfs_dir_handle])
    assert handle

    # Recycle the allocator block that held the handle, if it was freed:
    # allocations of the same size class make reuse all but certain.
    garbage = [retro_vfs_dir_handle(i, None, False) for i in range(10_000)]

    seen: list[bytes] = []
    while readdir(handle):
        name = dirent_get_name(handle)
        assert name is not None
        seen.append(name)

    assert closedir(handle)
    assert sorted(seen) == sorted(names)

    del garbage


def test_dir_handles_dont_accumulate(
    env: CompositeEnvironmentDriver, vfs_driver: DefaultFileSystemDriver, tmp_path: Path
) -> None:
    """``closedir`` must release whatever ``opendir`` registered."""
    (tmp_path / "file.bin").write_bytes(b"\x00")
    vfs = _get_vfs(env)

    assert vfs

    opendir = vfs.opendir
    assert opendir

    closedir = vfs.closedir
    assert closedir

    for _ in range(3):
        handle = cast(opendir(bytes(tmp_path), True), TypedPointer[retro_vfs_dir_handle])
        # TODO: Make TypedFunctionPointers add errcheck handlers to work around ctypes limits
        assert handle
        assert closedir(handle)

    assert not vfs_driver._dir_handles  # pyright: ignore[reportPrivateUsage]


def test_get_path_doesnt_leak(env: CompositeEnvironmentDriver, tmp_path: Path) -> None:
    """
    ``get_path`` must not leak a fresh ``bytes`` object on every call.

    A ``ctypes`` callback whose return type is ``c_char_p``
    has no way of knowing when the core is done with the returned pointer,
    so if the Python callback returns a ``bytes`` object,
    ``ctypes`` keeps it alive forever
    and emits ``RuntimeWarning: memory leak in callback function``.
    The callback must instead hand back a pointer into a buffer
    that the frontend keeps alive itself,
    and that pointer must stay stable for the lifetime of the handle.
    """
    path = tmp_path / "file.bin"
    path.write_bytes(b"\x00" * 16)

    vfs = _get_vfs(env)
    open = vfs.open
    get_path = vfs.get_path
    close = vfs.close
    assert open is not None
    assert get_path is not None
    assert close is not None

    # Call the same function pointer without ctypes' c_char_p conversion,
    # so we can inspect the raw address the core would see.
    raw_get_path = cast(get_path, CFUNCTYPE(c_void_p, c_void_p))

    handle = cast(
        open(bytes(path), VfsFileAccess.READ, VfsFileAccessHint.NONE),
        TypedPointer[retro_vfs_file_handle],
    )
    assert handle
    address = cast(handle, c_void_p).value

    # The warning is raised inside the ctypes callback,
    # where "error" would only make it an unraisable exception;
    # recording is the reliable way to observe it.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        results = [get_path(handle) for _ in range(5)]
        addresses = {raw_get_path(address) for _ in range(5)}

    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
    assert results == [bytes(path)] * 5
    assert len(addresses) == 1
    assert None not in addresses

    assert close(handle) == 0
    assert not env._vfs_strings  # pyright: ignore[reportPrivateUsage]


def test_dirent_get_name_doesnt_leak(env: CompositeEnvironmentDriver, tmp_path: Path) -> None:
    """``dirent_get_name`` must not leak a fresh ``bytes`` object on every call."""
    names = {f"file{i}.bin".encode() for i in range(8)}
    for name in names:
        (tmp_path / name.decode()).write_bytes(b"\x00" * 16)

    vfs = _get_vfs(env)
    opendir = vfs.opendir
    readdir = vfs.readdir
    dirent_get_name = vfs.dirent_get_name
    closedir = vfs.closedir
    assert opendir is not None
    assert readdir is not None
    assert dirent_get_name is not None
    assert closedir is not None

    handle = cast(opendir(bytes(tmp_path), True), TypedPointer[retro_vfs_dir_handle])
    assert handle

    seen: list[bytes] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        while readdir(handle):
            name = dirent_get_name(handle)
            assert name is not None
            # Repeated calls for the same entry must agree
            assert dirent_get_name(handle) == name
            seen.append(name)

    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
    assert sorted(seen) == sorted(names)
    assert closedir(handle)
    assert not env._vfs_strings  # pyright: ignore[reportPrivateUsage]
