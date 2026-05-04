"""
Types that describe the address space of the :class:`.Core`'s emulated memory.
"""

from __future__ import annotations

from ctypes import POINTER, Structure, c_char_p, c_size_t, c_uint, c_uint64
from dataclasses import dataclass
from enum import IntFlag
from typing import overload

from libretro.ctypes import TypedPointer, c_void_ptr

from ._utils import MemoDict, deepcopy_array

RETRO_MEMORY_MASK = 0xFF
"""Mask for extracting the memory type from a memory ID."""

RETRO_MEMORY_SAVE_RAM = 0
"""Identifier for save RAM (battery-backed SRAM)."""

RETRO_MEMORY_RTC = 1
"""Identifier for real-time clock memory."""

RETRO_MEMORY_SYSTEM_RAM = 2
"""Identifier for main system RAM."""

RETRO_MEMORY_VIDEO_RAM = 3
"""Identifier for video RAM."""


RETRO_MEMDESC_CONST = 1 << 0
RETRO_MEMDESC_BIGENDIAN = 1 << 1
RETRO_MEMDESC_SYSTEM_RAM = 1 << 2
RETRO_MEMDESC_SAVE_RAM = 1 << 3
RETRO_MEMDESC_VIDEO_RAM = 1 << 4
RETRO_MEMDESC_ALIGN_2 = 1 << 16
RETRO_MEMDESC_ALIGN_4 = 2 << 16
RETRO_MEMDESC_ALIGN_8 = 3 << 16
RETRO_MEMDESC_MINSIZE_2 = 1 << 24
RETRO_MEMDESC_MINSIZE_4 = 2 << 24
RETRO_MEMDESC_MINSIZE_8 = 3 << 24


class MemoryDescriptorFlag(IntFlag):
    """Flags that describe properties of a :class:`retro_memory_descriptor`.

    Corresponds to the ``RETRO_MEMDESC_*`` constants in ``libretro.h``.

    >>> from libretro.api import MemoryDescriptorFlag
    >>> MemoryDescriptorFlag.CONST
    <MemoryDescriptorFlag.CONST: 1>
    >>> MemoryDescriptorFlag.BIGENDIAN | MemoryDescriptorFlag.SAVE_RAM
    <MemoryDescriptorFlag.SAVE_RAM|BIGENDIAN: 10>
    """

    CONST = RETRO_MEMDESC_CONST
    BIGENDIAN = RETRO_MEMDESC_BIGENDIAN
    SYSTEM_RAM = RETRO_MEMDESC_SYSTEM_RAM
    SAVE_RAM = RETRO_MEMDESC_SAVE_RAM
    VIDEO_RAM = RETRO_MEMDESC_VIDEO_RAM
    ALIGN_2 = RETRO_MEMDESC_ALIGN_2
    ALIGN_4 = RETRO_MEMDESC_ALIGN_4
    ALIGN_8 = RETRO_MEMDESC_ALIGN_8
    MINSIZE_2 = RETRO_MEMDESC_MINSIZE_2
    MINSIZE_4 = RETRO_MEMDESC_MINSIZE_4
    MINSIZE_8 = RETRO_MEMDESC_MINSIZE_8


@dataclass(init=False, slots=True)
class retro_memory_descriptor(Structure):
    """
    Describes a region of emulated memory.

    Corresponds to :c:type:`retro_memory_descriptor` in ``libretro.h``.

    >>> from libretro.api import retro_memory_descriptor
    >>> desc = retro_memory_descriptor()
    >>> desc.start
    0
    >>> desc.ptr is None
    True
    """

    flags: MemoryDescriptorFlag
    """Bitwise OR of :class:`MemoryDescriptorFlag` values describing this region."""
    ptr: c_void_ptr | None
    """Pointer to the start of this memory region in the host's address space."""
    offset: int
    """Offset relative to :attr:`ptr`."""
    start: int
    """
    Starting address within the emulated hardware's address space.

    .. note::
        This is not represented as a pointer because
        it's not necessarily valid in the host's address space.
    """

    select: int
    """Bitmask of address bits that must match :attr:`start`."""
    disconnect: int
    """Bitmask of address bits not used for addressing."""
    len: int
    """Length of this memory region in bytes."""
    addrspace: bytes | None
    """Short name for this address space."""

    _fields_ = (
        ("flags", c_uint64),
        ("ptr", c_void_ptr),
        ("offset", c_size_t),
        ("start", c_size_t),
        ("select", c_size_t),
        ("disconnect", c_size_t),
        ("len", c_size_t),
        ("addrspace", c_char_p),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object,
        including all subobjects and strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_memory_descriptor
        >>> copy.deepcopy(retro_memory_descriptor()).start
        0
        """
        return retro_memory_descriptor(
            flags=self.flags,
            ptr=self.ptr,
            offset=self.offset,
            start=self.start,
            select=self.select,
            disconnect=self.disconnect,
            len=self.len,
            addrspace=self.addrspace,
        )

    # TODO: Implement __getitem__, __setitem__
    # TODO: Implement a buffer property (not __buffer__ because Structure provides that)


@dataclass(init=False, slots=True)
class retro_memory_map(Structure):
    """
    A collection of :class:`retro_memory_descriptor`\\s
    that define the address space of the :class:`.Core`'s emulated memory.

    Corresponds to :c:type:`retro_memory_map` in ``libretro.h``.

    >>> from libretro.api import retro_memory_map
    >>> m = retro_memory_map()
    >>> len(m)
    0
    """

    descriptors: TypedPointer[retro_memory_descriptor] | None
    """Array of memory descriptors."""
    num_descriptors: int
    """Number of entries in :attr:`descriptors`."""

    _fields_ = (
        ("descriptors", POINTER(retro_memory_descriptor)),
        ("num_descriptors", c_uint),
    )

    def __len__(self):
        """Returns the number of memory descriptors.

        >>> from libretro.api import retro_memory_map
        >>> len(retro_memory_map())
        0
        """
        return self.num_descriptors

    @overload
    def __getitem__(self, item: int) -> retro_memory_descriptor: ...
    @overload
    def __getitem__(
        self, item: slice[retro_memory_descriptor]
    ) -> list[retro_memory_descriptor]: ...
    def __getitem__(
        self, item: int | slice[retro_memory_descriptor]
    ) -> retro_memory_descriptor | list[retro_memory_descriptor]:
        """Returns a descriptor by index or a list of descriptors by slice.

        :param item: An integer index or slice.
        :returns: A single :class:`retro_memory_descriptor` or a list of them.
        :raises IndexError: If the index is out of range.
        :raises RuntimeError: If no descriptors are available.
        """
        if isinstance(item, int):
            if item < 0 or item >= self.num_descriptors:
                raise IndexError(f"Expected 0 <= index < {self.num_descriptors}, got {item}")
        # TODO: Validate the slice (not just the start and stop, but also the step)

        if not self.descriptors:
            raise RuntimeError("Memory map has no descriptors")

        return self.descriptors[item]

    def __deepcopy__(self, memodict: MemoDict = None):
        """
        Returns a deep copy of this object,
        including all subobjects and strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_memory_map
        >>> copy.deepcopy(retro_memory_map()).num_descriptors
        0
        """
        return retro_memory_map(
            descriptors=deepcopy_array(self.descriptors, self.num_descriptors, memodict),
            num_descriptors=self.num_descriptors,
        )


__all__ = [
    "retro_memory_descriptor",
    "retro_memory_map",
    "MemoryDescriptorFlag",
    "RETRO_MEMORY_MASK",
    "RETRO_MEMORY_SAVE_RAM",
    "RETRO_MEMORY_RTC",
    "RETRO_MEMORY_SYSTEM_RAM",
    "RETRO_MEMORY_VIDEO_RAM",
]
