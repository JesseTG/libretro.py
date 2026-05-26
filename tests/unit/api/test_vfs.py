"""Unit tests for :mod:`libretro.api.vfs`."""

from __future__ import annotations

import copy

import pytest

from libretro.api import (
    VfsFileAccess,
    VfsFileAccessHint,
    VfsSeekPosition,
    retro_vfs_dir_handle,
    retro_vfs_file_handle,
    retro_vfs_interface,
    retro_vfs_interface_info,
)


def test_retro_vfs_file_handle_init() -> None:
    handle = retro_vfs_file_handle(
        id=42, path=b"/tmp/x.bin", mode=VfsFileAccess.READ_WRITE, hints=0
    )
    assert handle.id == 42
    assert handle.path == b"/tmp/x.bin"
    assert handle.mode == VfsFileAccess.READ_WRITE
    assert handle.hints == 0


def test_retro_vfs_dir_handle_kwarg_init() -> None:
    handle = retro_vfs_dir_handle(id=1, dir=b"/tmp", include_hidden=True)
    assert handle.id == 1
    assert handle.dir == b"/tmp"
    assert handle.include_hidden is True


def test_retro_vfs_interface_defaults_all_null() -> None:
    iface = retro_vfs_interface()
    assert not iface.open
    assert not iface.close
    assert not iface.read
    assert not iface.write
    assert not iface.opendir
    assert not iface.closedir


def test_retro_vfs_interface_deepcopy() -> None:
    iface = retro_vfs_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.open


def test_retro_vfs_interface_info_defaults() -> None:
    info = retro_vfs_interface_info()
    assert info.required_interface_version == 0
    assert not info.iface


def test_retro_vfs_interface_info_kwarg_init() -> None:
    info = retro_vfs_interface_info(required_interface_version=3)
    assert info.required_interface_version == 3


@pytest.mark.parametrize(
    ("access", "open_flag"),
    [
        (VfsFileAccess.READ, "rb"),
        (VfsFileAccess.WRITE, "wb"),
        (VfsFileAccess.READ_WRITE, "w+b"),
        (VfsFileAccess.READ_WRITE_EXISTING, "r+b"),
    ],
)
def test_vfs_file_access_open_flag(access: VfsFileAccess, open_flag: str) -> None:
    assert access.open_flag == open_flag


def test_vfs_file_access_hint_values() -> None:
    assert VfsFileAccessHint.NONE.value == 0
    assert VfsFileAccessHint.FREQUENT_ACCESS.value == 1


def test_vfs_seek_position_enum_values() -> None:
    assert VfsSeekPosition.START.value == 0
    assert VfsSeekPosition.CURRENT.value == 1
    assert VfsSeekPosition.END.value == 2
