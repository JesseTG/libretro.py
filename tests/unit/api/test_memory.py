"""Unit tests for :mod:`libretro.api.memory`."""

from __future__ import annotations

import copy
from collections.abc import Sequence
from ctypes import Array, addressof, c_uint8

import pytest

from libretro.api import (
    MemoryDescriptorFlag,
    retro_memory_descriptor,
    retro_memory_map,
)


def test_retro_memory_descriptor_kwarg_init() -> None:
    desc = retro_memory_descriptor(
        flags=MemoryDescriptorFlag.SAVE_RAM | MemoryDescriptorFlag.ALIGN_4,
        offset=0x1000,
        start=0x2000,
        select=0xFF,
        disconnect=0x00,
        len=0x10000,
        addrspace=b"WRAM",
    )
    assert desc.flags == MemoryDescriptorFlag.SAVE_RAM | MemoryDescriptorFlag.ALIGN_4
    assert desc.offset == 0x1000
    assert desc.start == 0x2000
    assert desc.select == 0xFF
    assert desc.disconnect == 0x00
    assert desc.len == 0x10000
    assert desc.addrspace == b"WRAM"


def test_retro_memory_descriptor_defaults() -> None:
    desc = retro_memory_descriptor()
    assert desc.start == 0
    assert desc.len == 0
    assert desc.addrspace is None
    assert not desc.ptr


def test_retro_memory_descriptor_deepcopy() -> None:
    desc = retro_memory_descriptor(start=0x1000, len=0x100, addrspace=b"WRAM")
    dup = copy.deepcopy(desc)
    assert dup is not desc
    assert dup.start == desc.start
    assert dup.len == desc.len
    assert dup.addrspace == desc.addrspace


def test_retro_memory_map_empty_length() -> None:
    m = retro_memory_map()
    assert len(m) == 0


def test_retro_memory_map_sequence_protocol() -> None:
    m = retro_memory_map()
    assert isinstance(m, Sequence)


def test_retro_memory_map_indexing_sequence_protocol() -> None:
    descs = (retro_memory_descriptor * 2)(
        retro_memory_descriptor(start=0x0000, len=0x1000),
        retro_memory_descriptor(start=0x1000, len=0x2000),
    )
    m = retro_memory_map(descs, 2)
    assert len(m) == 2
    assert m[0].len == 0x1000
    assert m[1].len == 0x2000
    assert [d.len for d in m] == [0x1000, 0x2000]


def test_retro_memory_map_index_out_of_range() -> None:
    descs = (retro_memory_descriptor * 1)(retro_memory_descriptor(start=0, len=0x100))
    m = retro_memory_map(descs, 1)
    with pytest.raises(IndexError):
        m[5]


def test_retro_memory_map_deepcopy() -> None:
    m = retro_memory_map()
    dup = copy.deepcopy(m)
    assert dup is not m
    assert len(dup) == 0


def test_memory_descriptor_flag_combination() -> None:
    flag = MemoryDescriptorFlag.SAVE_RAM | MemoryDescriptorFlag.BIGENDIAN
    assert MemoryDescriptorFlag.SAVE_RAM in flag
    assert MemoryDescriptorFlag.BIGENDIAN in flag
    assert MemoryDescriptorFlag.CONST not in flag


def test_memory_descriptor_flag_align_values_match_libretro() -> None:
    assert MemoryDescriptorFlag.ALIGN_2.value == 1 << 16
    assert MemoryDescriptorFlag.ALIGN_4.value == 2 << 16
    assert MemoryDescriptorFlag.ALIGN_8.value == 3 << 16


def viewof(desc: retro_memory_descriptor) -> memoryview:
    view = desc.view
    assert view is not None
    return view


def resolve(m: retro_memory_map, address: int) -> tuple[retro_memory_descriptor, int]:
    found = m.find(address)
    assert found is not None, f"{address:#010x} is unmapped"
    return found


# --------------------------------------------------------------------------- #
# retro_memory_descriptor.view
# --------------------------------------------------------------------------- #


def test_view_spans_the_declared_length() -> None:
    buffer = (c_uint8 * 0x100)()
    desc = retro_memory_descriptor(ptr=addressof(buffer), len=0x80)
    assert len(viewof(desc)) == 0x80


def test_view_reads_through_to_the_backing_buffer() -> None:
    buffer = (c_uint8 * 4)(0x11, 0x22, 0x33, 0x44)
    desc = retro_memory_descriptor(ptr=addressof(buffer), len=4)
    assert bytes(viewof(desc)) == b"\x11\x22\x33\x44"


def test_view_writes_through_to_the_backing_buffer() -> None:
    buffer = (c_uint8 * 4)()
    desc = retro_memory_descriptor(ptr=addressof(buffer), len=4)
    viewof(desc)[1] = 0xAB
    assert buffer[1] == 0xAB


def test_view_honors_offset() -> None:
    buffer = (c_uint8 * 8)(0, 1, 2, 3, 4, 5, 6, 7)
    desc = retro_memory_descriptor(ptr=addressof(buffer), offset=4, len=4)
    assert bytes(viewof(desc)) == b"\x04\x05\x06\x07"


def test_view_is_readonly_when_const() -> None:
    buffer = (c_uint8 * 4)()
    desc = retro_memory_descriptor(ptr=addressof(buffer), len=4, flags=MemoryDescriptorFlag.CONST)
    view = viewof(desc)
    assert view.readonly

    with pytest.raises(TypeError):
        view[0] = 1


def test_view_is_writable_without_const() -> None:
    buffer = (c_uint8 * 4)()
    desc = retro_memory_descriptor(
        ptr=addressof(buffer), len=4, flags=MemoryDescriptorFlag.SYSTEM_RAM
    )
    assert not viewof(desc).readonly


def test_view_is_none_without_a_pointer() -> None:
    assert retro_memory_descriptor(len=0x100).view is None


def test_view_rejects_an_unknown_length() -> None:
    buffer = (c_uint8 * 4)()
    desc = retro_memory_descriptor(ptr=addressof(buffer), len=0)

    with pytest.raises(ValueError):
        desc.view


# --------------------------------------------------------------------------- #
# retro_memory_map.find
# --------------------------------------------------------------------------- #


def test_find_on_an_empty_map() -> None:
    assert retro_memory_map().find(0x1000) is None


def test_find_explicit_range_hit() -> None:
    buffer = (c_uint8 * 0x1000)()
    m = retro_memory_map(
        [retro_memory_descriptor(ptr=addressof(buffer), start=0x2000, len=0x1000)]
    )

    desc, offset = resolve(m, 0x2123)
    assert desc.start == 0x2000
    assert offset == 0x123


def test_find_explicit_range_misses_below_and_above() -> None:
    buffer = (c_uint8 * 0x1000)()
    m = retro_memory_map(
        [retro_memory_descriptor(ptr=addressof(buffer), start=0x2000, len=0x1000)]
    )

    assert m.find(0x1FFF) is None
    assert m.find(0x2FFF) is not None
    assert m.find(0x3000) is None


def test_find_returns_the_descriptor_the_core_sent() -> None:
    buffer = (c_uint8 * 0x1000)()
    m = retro_memory_map(
        [retro_memory_descriptor(ptr=addressof(buffer), start=0x2000, len=0x1000)]
    )

    desc, _ = resolve(m, 0x2000)
    assert desc.ptr is not None
    assert desc.ptr.value == addressof(buffer)


def test_find_resolves_a_view_that_aliases_the_core() -> None:
    buffer = (c_uint8 * 0x1000)()
    m = retro_memory_map(
        [retro_memory_descriptor(ptr=addressof(buffer), start=0x2000, len=0x1000)]
    )

    desc, offset = resolve(m, 0x2010)
    viewof(desc)[offset] = 0x5A
    assert buffer[0x10] == 0x5A


def test_find_follows_declared_mirrors() -> None:
    # The DS's 4 MiB of main RAM repeats four times across a 16 MiB window
    buffer = (c_uint8 * 0x400000)()
    m = retro_memory_map(
        [
            retro_memory_descriptor(
                ptr=addressof(buffer),
                start=0x02000000,
                select=0xFF000000,
                disconnect=0x00C00000,
                len=0x400000,
            )
        ]
    )

    mirrors = (0x02000010, 0x02400010, 0x02800010, 0x02C00010)
    assert [resolve(m, address)[1] for address in mirrors] == [0x10] * 4


def test_find_infers_mirrors_that_the_map_left_out() -> None:
    # A descriptor that selects more address space than it fills mirrors across the rest,
    # even though it declared no disconnect mask of its own
    buffer = (c_uint8 * 0x400000)()
    m = retro_memory_map(
        [
            retro_memory_descriptor(
                ptr=addressof(buffer),
                start=0x02000000,
                select=0xFF000000,
                len=0x400000,
            )
        ]
    )

    mirrors = (0x02000010, 0x02400010, 0x02800010, 0x02C00010)
    assert [resolve(m, address)[1] for address in mirrors] == [0x10] * 4


def test_find_stops_at_the_first_matching_descriptor() -> None:
    first = (c_uint8 * 0x1000)()
    second = (c_uint8 * 0x1000)()
    m = retro_memory_map(
        [
            retro_memory_descriptor(ptr=addressof(first), start=0x2000, len=0x1000),
            retro_memory_descriptor(ptr=addressof(second), start=0x2000, len=0x1000),
        ]
    )

    desc, _ = resolve(m, 0x2000)
    assert desc.ptr is not None
    assert desc.ptr.value == addressof(first)


def test_find_rejects_a_length_that_is_not_a_power_of_two() -> None:
    m = retro_memory_map([retro_memory_descriptor(start=0, len=0x3000)])

    with pytest.raises(ValueError, match="power of two"):
        m.find(0)


def test_find_rejects_a_start_that_its_select_cannot_match() -> None:
    m = retro_memory_map([retro_memory_descriptor(start=0x1234, select=0xFF000000, len=0x1000)])

    with pytest.raises(ValueError, match="cannot match"):
        m.find(0)


def test_find_rejects_a_descriptor_with_neither_select_nor_length() -> None:
    m = retro_memory_map([retro_memory_descriptor(start=0x1000)])

    with pytest.raises(ValueError, match="neither"):
        m.find(0x1000)


@pytest.mark.parametrize("address", [-1, 0x1_0000_0000])
def test_find_rejects_addresses_outside_32_bits(address: int) -> None:
    m = retro_memory_map([retro_memory_descriptor(start=0, len=0x1000)])

    with pytest.raises(ValueError, match="32 bits"):
        m.find(address)


# --------------------------------------------------------------------------- #
# The map that melonDS DS sends, as a worked example
# --------------------------------------------------------------------------- #

# Kept alive for the module's lifetime, because NINTENDO_DS_MAP only holds their addresses
DS_MAIN_RAM = (c_uint8 * 0x400000)()
DS_ITCM = (c_uint8 * 0x8000)()
DS_DTCM = (c_uint8 * 0x4000)()

#: The memory map of a Nintendo DS, as the melonDS DS core describes it.
NINTENDO_DS_MAP = retro_memory_map(
    [
        retro_memory_descriptor(
            flags=MemoryDescriptorFlag.SYSTEM_RAM,
            ptr=addressof(DS_MAIN_RAM),
            start=0x02000000,
            select=0xFF000000,
            disconnect=0x00C00000,
            len=0x400000,
        ),
        retro_memory_descriptor(
            flags=MemoryDescriptorFlag.SYSTEM_RAM,
            ptr=addressof(DS_ITCM),
            start=0x00000000,
            select=0xFE000000,
            disconnect=0x01FF8000,
            len=0x8000,
        ),
        retro_memory_descriptor(
            flags=MemoryDescriptorFlag.SYSTEM_RAM,
            ptr=addressof(DS_DTCM),
            start=0x0E000000,
            select=0,
            disconnect=0,
            len=0x4000,
        ),
    ]
)


@pytest.mark.parametrize(
    ("address", "buffer", "offset"),
    [
        pytest.param(0x02000010, DS_MAIN_RAM, 0x10, id="main-ram"),
        pytest.param(0x02400010, DS_MAIN_RAM, 0x10, id="main-ram-mirror"),
        pytest.param(0x027E0000, DS_MAIN_RAM, 0x3E0000, id="retail-dtcm-address-hits-main-ram"),
        pytest.param(0x02FF4000, DS_MAIN_RAM, 0x3F4000, id="blocksds-dtcm-address-hits-main-ram"),
        pytest.param(0x00000ABC, DS_ITCM, 0xABC, id="itcm"),
        pytest.param(0x01000ABC, DS_ITCM, 0xABC, id="itcm-mirror"),
        pytest.param(0x01FFFFFF, DS_ITCM, 0x7FFF, id="itcm-last-mirror"),
        pytest.param(0x0E000100, DS_DTCM, 0x100, id="dtcm"),
        pytest.param(0x0E003FFF, DS_DTCM, 0x3FFF, id="dtcm-last-byte"),
    ],
)
def test_nintendo_ds_map_resolves(address: int, buffer: Array[c_uint8], offset: int) -> None:
    desc, found = resolve(NINTENDO_DS_MAP, address)
    assert desc.ptr is not None
    assert desc.ptr.value == addressof(buffer)
    assert found == offset


@pytest.mark.parametrize(
    "address",
    [
        pytest.param(0x0DFFFFFF, id="below-dtcm"),
        pytest.param(0x0E004000, id="past-dtcm"),
        pytest.param(0x03000000, id="shared-wram"),
        pytest.param(0x04000000, id="io-registers"),
    ],
)
def test_nintendo_ds_map_leaves_unmapped_addresses_alone(address: int) -> None:
    assert NINTENDO_DS_MAP.find(address) is None
