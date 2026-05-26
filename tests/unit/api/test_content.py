"""Unit tests for :mod:`libretro.api.content`."""

from __future__ import annotations

import copy
from ctypes import addressof

import pytest

from libretro.api import (
    retro_game_info,
    retro_game_info_ext,
    retro_subsystem_info,
    retro_subsystem_memory_info,
    retro_subsystem_rom_info,
    retro_system_content_info_override,
    retro_system_info,
)
from libretro.api._utils import address
from libretro.api.content import (
    ContentInfoOverrides,
    Subsystems,
)


def test_retro_system_info_kwarg_init() -> None:
    info = retro_system_info(
        library_name=b"TestCore",
        library_version=b"1.2.3",
        valid_extensions=b"bin|rom",
        need_fullpath=True,
        block_extract=False,
    )
    assert info.library_name == b"TestCore"
    assert info.library_version == b"1.2.3"
    assert info.valid_extensions == b"bin|rom"
    assert info.need_fullpath is True
    assert info.block_extract is False


def test_retro_system_info_defaults() -> None:
    info = retro_system_info()
    assert info.library_name is None
    assert info.library_version is None
    assert info.valid_extensions is None
    assert info.need_fullpath is False
    assert info.block_extract is False


def test_retro_system_info_extensions_yields_each_ext() -> None:
    info = retro_system_info(valid_extensions=b"a|b|c")
    assert list(info.extensions) == [b"a", b"b", b"c"]


def test_retro_system_info_extensions_empty_when_none() -> None:
    info = retro_system_info()
    assert list(info.extensions) == []


def test_retro_system_info_deepcopy_preserves_values() -> None:
    info = retro_system_info(library_name=b"TestCore", library_version=b"1.0")
    dup = copy.deepcopy(info)
    assert dup is not info
    assert addressof(dup) != addressof(info)
    assert dup.library_name == info.library_name
    assert dup.library_version == info.library_version


def test_retro_system_info_deepcopy_copies_strings() -> None:
    info = retro_system_info(library_name=b"TestCore", library_version=b"1.0")
    dup = copy.deepcopy(info)
    info_library_name = info.library_name
    dup_library_name = dup.library_name

    assert info_library_name is not dup_library_name
    assert address(info_library_name) != address(dup_library_name)


def test_retro_game_info_kwarg_init() -> None:
    info = retro_game_info(path=b"/games/test.bin", size=1024, meta=b"checksum=deadbeef")
    assert info.path == b"/games/test.bin"
    assert info.size == 1024
    assert info.meta == b"checksum=deadbeef"


def test_retro_game_info_ext_extracts_extension() -> None:
    assert retro_game_info(path=b"/games/test.bin").ext == b"bin"
    assert retro_game_info(path=b"/games/test").ext == b""
    assert retro_game_info(path=None).ext is None


def test_retro_game_info_deepcopy_copies_strings() -> None:
    info = retro_game_info(path=b"/x.bin", size=0, meta=None)
    dup = copy.deepcopy(info)
    assert dup is not info
    assert dup.path == info.path
    assert dup.size == info.size


def test_retro_subsystem_memory_info_kwarg_init() -> None:
    mem = retro_subsystem_memory_info(extension=b"srm", type=0x100)
    assert mem.extension == b"srm"
    assert mem.type == 0x100


def test_retro_subsystem_memory_info_deepcopy() -> None:
    mem = retro_subsystem_memory_info(extension=b"srm", type=0x101)
    dup = copy.deepcopy(mem)
    assert dup is not mem
    assert dup.extension == mem.extension
    assert dup.type == mem.type


def test_retro_subsystem_rom_info_kwarg_init() -> None:
    rom = retro_subsystem_rom_info(
        desc=b"BIOS",
        valid_extensions=b"bin",
        need_fullpath=True,
        block_extract=False,
        required=True,
    )
    assert rom.desc == b"BIOS"
    assert rom.valid_extensions == b"bin"
    assert rom.need_fullpath is True
    assert rom.required is True


def test_retro_subsystem_rom_info_extensions_yields_each_ext() -> None:
    rom = retro_subsystem_rom_info(valid_extensions=b"bin|rom")
    assert list(rom.extensions) == [b"bin", b"rom"]


def test_retro_subsystem_rom_info_indexing_raises_when_empty() -> None:
    rom = retro_subsystem_rom_info(num_memory=0)
    with pytest.raises(ValueError):
        rom[0]


def test_retro_subsystem_rom_info_len_returns_num_memory() -> None:
    rom = retro_subsystem_rom_info(num_memory=0)
    assert len(rom) == 0


def test_retro_subsystem_info_sequence_protocol() -> None:
    roms = (retro_subsystem_rom_info * 2)(
        retro_subsystem_rom_info(desc=b"BIOS"),
        retro_subsystem_rom_info(desc=b"Cartridge"),
    )
    info = retro_subsystem_info(b"Super Game Boy", b"sgb", roms, 2, 1)
    assert len(info) == 2
    assert info[0].desc == b"BIOS"
    assert info[1].desc == b"Cartridge"
    assert [r.desc for r in info] == [b"BIOS", b"Cartridge"]


def test_retro_subsystem_info_index_out_of_range() -> None:
    roms = (retro_subsystem_rom_info * 1)(retro_subsystem_rom_info(desc=b"BIOS"))
    info = retro_subsystem_info(b"x", b"x", roms, 1, 0)
    with pytest.raises(IndexError):
        info[5]


def test_retro_subsystem_info_by_extension_missing_raises_key_error() -> None:
    roms = (retro_subsystem_rom_info * 1)(
        retro_subsystem_rom_info(desc=b"BIOS", valid_extensions=b"bin"),
    )
    info = retro_subsystem_info(b"x", b"x", roms, 1, 0)
    with pytest.raises(KeyError):
        info.by_extension("xyz")


def test_retro_subsystem_info_by_extension_finds_match() -> None:
    roms = (retro_subsystem_rom_info * 1)(
        retro_subsystem_rom_info(desc=b"BIOS", valid_extensions=b"bin|rom"),
    )
    info = retro_subsystem_info(b"x", b"x", roms, 1, 0)
    found = info.by_extension(b".rom")
    assert found.desc == b"BIOS"


def test_retro_subsystem_info_deepcopy() -> None:
    info = retro_subsystem_info(desc=b"sgb", ident=b"sgb", id=1)
    dup = copy.deepcopy(info)
    assert dup is not info
    assert dup.desc == info.desc
    assert dup.ident == info.ident


def test_retro_system_content_info_override_kwarg_init() -> None:
    ov = retro_system_content_info_override(
        extensions=b"bin|rom", need_fullpath=True, persistent_data=False
    )
    assert ov.extensions == b"bin|rom"
    assert ov.need_fullpath is True
    assert ov.persistent_data is False


def test_retro_system_content_info_override_get_extensions() -> None:
    ov = retro_system_content_info_override(extensions=b"bin|rom|iso")
    assert list(ov.get_extensions()) == [b"bin", b"rom", b"iso"]


def test_retro_system_content_info_override_deepcopy() -> None:
    ov = retro_system_content_info_override(extensions=b"bin", need_fullpath=True)
    dup = copy.deepcopy(ov)
    assert dup is not ov
    assert dup.extensions == ov.extensions
    assert dup.need_fullpath == ov.need_fullpath


def test_retro_game_info_ext_kwarg_init() -> None:
    info = retro_game_info_ext(
        full_path=b"/games/test.bin",
        ext=b"bin",
        name=b"test",
        dir=b"/games",
        size=512,
        file_in_archive=False,
        persistent_data=True,
    )
    assert info.full_path == b"/games/test.bin"
    assert info.ext == b"bin"
    assert info.name == b"test"
    assert info.dir == b"/games"
    assert info.size == 512
    assert info.file_in_archive is False
    assert info.persistent_data is True


def test_retro_game_info_ext_deepcopy() -> None:
    info = retro_game_info_ext(full_path=b"/x.bin", ext=b"bin")
    dup = copy.deepcopy(info)
    assert dup is not info
    assert dup.full_path == info.full_path
    assert dup.ext == info.ext


def test_subsystems_indexed_by_int_str_bytes() -> None:
    subs = Subsystems(
        [
            retro_subsystem_info(desc=b"SGB", ident=b"sgb", id=1),
            retro_subsystem_info(desc=b"GBC", ident=b"gbc", id=2),
        ]
    )
    assert len(subs) == 2
    assert subs[0].ident == b"sgb"
    assert subs[b"gbc"].id == 2
    assert subs["sgb"].id == 1


def test_subsystems_membership_by_ident() -> None:
    subs = Subsystems([retro_subsystem_info(ident=b"sgb")])
    assert b"sgb" in subs
    assert "gbc" not in subs


def test_subsystems_rejects_non_sequence() -> None:
    with pytest.raises(TypeError):
        Subsystems(42)  # pyright: ignore[reportArgumentType]


def test_subsystems_rejects_wrong_element_type() -> None:
    with pytest.raises(TypeError):
        Subsystems(["not a subsystem"])  # pyright: ignore[reportArgumentType]


def test_subsystems_missing_ident_raises_key_error() -> None:
    subs = Subsystems([])
    with pytest.raises(KeyError):
        subs[b"missing"]


def test_subsystems_out_of_range_raises_index_error() -> None:
    subs = Subsystems([])
    with pytest.raises(IndexError):
        subs[5]


def test_content_info_overrides_by_extension() -> None:
    overrides = ContentInfoOverrides(
        [
            retro_system_content_info_override(extensions=b"bin"),
            retro_system_content_info_override(extensions=b"rom|iso"),
        ]
    )
    assert len(overrides) == 2
    assert overrides[0].extensions == b"bin"
    assert overrides[b"rom"].extensions == b"rom|iso"
    assert overrides[b".iso"].extensions == b"rom|iso"


def test_content_info_overrides_membership() -> None:
    overrides = ContentInfoOverrides([retro_system_content_info_override(extensions=b"bin")])
    assert b"bin" in overrides
    assert b"rom" not in overrides


def test_content_info_overrides_first_match_wins() -> None:
    overrides = ContentInfoOverrides(
        [
            retro_system_content_info_override(extensions=b"bin", need_fullpath=False),
            retro_system_content_info_override(extensions=b"bin", need_fullpath=True),
        ]
    )
    assert overrides[b"bin"].need_fullpath is False
