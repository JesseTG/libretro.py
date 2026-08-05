# These tests exercise the composite driver's VFS interface exactly the way
# a core does, through the ctypes function pointers; those calls are untyped
# at the ABI boundary, so the unknown-type family of checks is relaxed here.
# pyright: reportPrivateUsage=false, reportArgumentType=false
# pyright: reportUnknownMemberType=false, reportUnknownParameterType=false
# pyright: reportMissingParameterType=false, reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false, reportOptionalSubscript=false

from ctypes import POINTER, c_ubyte, cast, pointer

import pytest

from libretro.api.vfs import (
    VfsFileAccess,
    retro_vfs_file_handle,
    retro_vfs_interface_info,
)
from libretro.drivers.audio import ArrayAudioDriver
from libretro.drivers.environment.composite import CompositeEnvironmentDriver
from libretro.drivers.input import IterableInputDriver
from libretro.drivers.vfs.default import DefaultFileSystemDriver
from libretro.drivers.video import ArrayVideoDriver


@pytest.fixture
def vfs_iface():
    env = CompositeEnvironmentDriver(
        audio=ArrayAudioDriver(),
        input=IterableInputDriver(),
        video=ArrayVideoDriver(),
        vfs=DefaultFileSystemDriver(),
    )
    info = retro_vfs_interface_info(required_interface_version=2, iface=None)
    assert env._get_vfs_interface(cast(pointer(info), POINTER(retro_vfs_interface_info)))
    yield info.iface[0]
    del env  # Keep the env (and its callbacks) alive for the duration of the test


def test_seek_returns_zero_on_success(vfs_iface, tmp_path):
    """
    libretro.h says seek returns the new position,
    but cores are written against RetroArch,
    which returns 0 on success for ordinary files;
    PPSSPP treats any non-zero return as an error.
    """
    path = tmp_path / "data.bin"
    path.write_bytes(bytes(range(200)))

    handle = cast(
        vfs_iface.open(str(path).encode(), VfsFileAccess.READ, 0), POINTER(retro_vfs_file_handle)
    )
    assert handle

    assert vfs_iface.seek(handle, 100, 0) == 0  # SEEK_SET to a non-zero position
    assert vfs_iface.tell(handle) == 100
    assert vfs_iface.seek(handle, 0, 2) == 0  # SEEK_END
    assert vfs_iface.tell(handle) == 200
    assert vfs_iface.close(handle) == 0


def test_read_after_seek(vfs_iface, tmp_path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"MComprHD-like header and then some")

    handle = cast(
        vfs_iface.open(str(path).encode(), VfsFileAccess.READ, 0), POINTER(retro_vfs_file_handle)
    )
    buf = (c_ubyte * 8)()
    assert vfs_iface.read(handle, buf, 8) == 8
    assert bytes(buf) == b"MComprHD"
    assert vfs_iface.seek(handle, 5, 0) == 0
    assert vfs_iface.read(handle, buf, 4) == 4
    assert bytes(buf[:4]) == b"rHD-"
    assert vfs_iface.size(handle) == path.stat().st_size
    assert vfs_iface.close(handle) == 0


def test_open_write_update_existing(vfs_iface, tmp_path):
    """WRITE | UPDATE_EXISTING opens for writing without truncation."""
    path = tmp_path / "save.bin"
    path.write_bytes(b"0123456789")

    handle = cast(
        vfs_iface.open(str(path).encode(), VfsFileAccess.WRITE | VfsFileAccess.UPDATE_EXISTING, 0),
        POINTER(retro_vfs_file_handle),
    )
    assert handle
    buf = (c_ubyte * 2)(*b"AB")
    assert vfs_iface.seek(handle, 4, 0) == 0
    assert vfs_iface.write(handle, buf, 2) == 2
    assert vfs_iface.close(handle) == 0
    assert path.read_bytes() == b"0123AB6789"  # Not truncated
