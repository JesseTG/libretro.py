"""Types that describe the address space of the :class:`.Core`'s emulated memory."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from ctypes import POINTER, Array, Structure, c_char_p, c_size_t, c_uint, c_uint64
from dataclasses import dataclass
from enum import IntFlag
from typing import overload

from libretro.ctypes import CIntArg, TypedArray, TypedPointer, c_void_ptr

from ._utils import MemoDict, NullPointerToNoneMixin, deepcopy_array

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
    """
    Flags that describe properties of a :class:`retro_memory_descriptor`.

    Corresponds to the ``RETRO_MEMDESC_*`` constants in ``libretro.h``.

    >>> from libretro.api import MemoryDescriptorFlag
    >>> MemoryDescriptorFlag.CONST
    <MemoryDescriptorFlag.CONST: 1>
    >>> MemoryDescriptorFlag.BIGENDIAN | MemoryDescriptorFlag.SAVE_RAM
    <MemoryDescriptorFlag.BIGENDIAN|SAVE_RAM: 10>
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
class retro_memory_descriptor(Structure, NullPointerToNoneMixin):
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
        Return a deep copy of this object,
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
class retro_memory_map(Structure, NullPointerToNoneMixin):
    r"""
    A collection of :class:`retro_memory_descriptor`\s
    that define the address space of the :class:`.Core`'s emulated memory.

    Corresponds to :c:type:`retro_memory_map` in ``libretro.h``.

    Empty maps have length ``0``;
    populating :attr:`descriptors` lets the map be iterated like a sequence:

    >>> from libretro.api import retro_memory_descriptor, retro_memory_map
    >>> len(retro_memory_map())
    0
    >>> descs = (retro_memory_descriptor * 2)(
    ...     retro_memory_descriptor(start=0,       len=0x10000),
    ...     retro_memory_descriptor(start=0x10000, len=0x20000),
    ... )
    >>> m = retro_memory_map(descs, 2)
    >>> len(m)
    2
    >>> [d.len for d in m]
    [65536, 131072]
    """

    descriptors: TypedPointer[retro_memory_descriptor] | None
    """Array of memory descriptors."""
    num_descriptors: int
    """Number of entries in :attr:`descriptors`."""

    _fields_ = (
        ("descriptors", POINTER(retro_memory_descriptor)),
        ("num_descriptors", c_uint),
    )

    def __init__(
        self,
        descriptors: TypedPointer[retro_memory_descriptor]
        | TypedArray[retro_memory_descriptor]
        | Array[retro_memory_descriptor]
        | Sequence[retro_memory_descriptor]
        | None = None,
        num_descriptors: CIntArg[c_uint] | None = None,
    ):
        """
        Initialize a :class:`retro_memory_map`.

        When *descriptors* is an :class:`~collections.abc.Sequence` (but not a pointer or array),
        it is converted to a :class:`~ctypes.Array`
        and *num_descriptors* defaults to its length:

        >>> from libretro.api import retro_memory_descriptor, retro_memory_map
        >>> descs = [retro_memory_descriptor(start=0, len=0x8000)]
        >>> m = retro_memory_map(descriptors=descs)
        >>> len(m)
        1

        :param descriptors: Array of memory descriptors as a pointer, array, or iterable.
        :param num_descriptors: Number of descriptors;
            inferred from *descriptors* when it is an array or iterable,
            and ``0`` when it is a pointer.
        """
        if descriptors is not None and not isinstance(descriptors, (TypedPointer, Array)):
            items = list(descriptors)
            descriptors = (retro_memory_descriptor * len(items))(*items)
        if num_descriptors is None:
            num_descriptors = len(descriptors) if isinstance(descriptors, Array) else 0

        super(retro_memory_map, self).__init__(descriptors, num_descriptors)

    def __len__(self):
        """
        Return the number of memory descriptors.

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
        """
        Return a descriptor by index or a list of descriptors by slice.

        Supports negative indexes in the usual Python fashion:

        >>> from libretro.api import retro_memory_descriptor, retro_memory_map
        >>> descs = (retro_memory_descriptor * 2)(
        ...     retro_memory_descriptor(start=0x0000, len=0x1000),
        ...     retro_memory_descriptor(start=0x1000, len=0x2000),
        ... )
        >>> m = retro_memory_map(descs, 2)
        >>> m[-1].start
        4096

        :param item: An integer index or slice.
        :return: A single :class:`retro_memory_descriptor` or a list of them.
        :raises RuntimeError: If :attr:`descriptors` is :obj:`None`.
        :raises IndexError: If ``item`` is an integer outside ``[-len, len)``.
        :raises TypeError: If ``item`` is neither an :class:`int` nor a :class:`slice`.
        """
        if not self.descriptors:
            raise RuntimeError("Memory map has no descriptors")

        match item:
            case int(i):
                n = len(self)
                if not (-n <= i < n):
                    raise IndexError(f"Expected {-n} <= index < {n}, got {i}")
                if i < 0:
                    i += n
                return self.descriptors[i]
            case slice() as s:
                return self.descriptors[s]
            case _:
                raise TypeError(f"Expected an int or slice, got {type(item).__name__}")

    def __iter__(self) -> Iterator[retro_memory_descriptor]:
        """
        Iterate over the memory descriptors in this map.

        Returns no elements when :attr:`descriptors` is :obj:`None`:

        >>> from libretro.api import retro_memory_map
        >>> list(retro_memory_map())
        []
        """
        if not self.descriptors:
            return
        for i in range(self.num_descriptors):
            yield self.descriptors[i]

    def __contains__(self, item: object) -> bool:
        """
        Test whether ``item`` appears in this sequence.

        :param item: The element to search for.
        :return: :obj:`True` if found, :obj:`False` otherwise.
        """
        return any(v is item or v == item for v in self)

    def __reversed__(self) -> Iterator[retro_memory_descriptor]:
        """
        Iterate over the memory descriptors in reverse order.

        Returns no elements when :attr:`descriptors` is :obj:`None`.

        :return: An iterator over the descriptors in reverse order.
        """
        if not self.descriptors:
            return
        for i in range(self.num_descriptors - 1, -1, -1):
            yield self.descriptors[i]

    def count(self, value: object) -> int:
        """
        Count occurrences of ``value`` in this sequence.

        :param value: The element to count.
        :return: The number of times ``value`` appears.
        """
        return sum(1 for v in self if v is value or v == value)

    def index(self, value: object, start: int = 0, stop: int | None = None) -> int:
        """
        Return the index of the first occurrence of ``value``.

        :param value: The element to search for.
        :param start: Optional start index (inclusive).
        :param stop: Optional stop index (exclusive).
        :return: The index of the first match within ``[start, stop)``.
        :raises ValueError: If ``value`` is not found within the given range.
        """
        n = len(self)
        if start < 0:
            start = max(n + start, 0)
        if stop is None:
            stop = n
        elif stop < 0:
            stop = max(n + stop, 0)
        for i in range(start, min(stop, n)):
            v = self[i]
            if v is value or v == value:
                return i
        raise ValueError(f"{value!r} is not in sequence")

    def __deepcopy__(self, memodict: MemoDict = None):
        """
        Return a deep copy of this object,
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


Sequence.register(retro_memory_map)  # type: ignore


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
