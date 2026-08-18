"""
Tests for the ``ctypes`` bridge between a core and a :class:`.FileSystemDriver`.

These drive :class:`.CompositeEnvironmentDriver`'s VFS interface
through its C function pointers,
exactly the way a core would after ``RETRO_ENVIRONMENT_GET_VFS_INTERFACE``.
No core is loaded.
"""

from __future__ import annotations

from ctypes import byref, c_void_p, cast
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
from libretro.api import retro_vfs_dir_handle, retro_vfs_interface, retro_vfs_interface_info
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
        handle = opendir(bytes(tmp_path), True)
        assert handle
        assert closedir(handle)

    assert not vfs_driver._dir_handles  # pyright: ignore[reportPrivateUsage]
