"""Unit tests for :mod:`libretro.api.memory`."""

from __future__ import annotations

import copy
from collections.abc import Sequence

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
