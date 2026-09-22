"""Types that describe the address space of the :class:`.Core`'s emulated memory."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from ctypes import POINTER, Array, Structure, c_char_p, c_size_t, c_uint, c_uint8, c_uint64
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

RETRO_MEMORY_ROM = 4
"""Identifier for the loaded game's ROM."""


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

    @property
    def view(self) -> memoryview[int] | None:
        """
        Return a live window into the host memory that this descriptor covers.

        The returned :class:`memoryview` aliases :attr:`len` bytes of a :class:`.Core`'s memory
        starting at :attr:`ptr` plus :attr:`offset`.
        Writing it changes what the core sees on its next frame
        unless :attr:`flags` includes :attr:`~MemoryDescriptorFlag.CONST`.

        >>> from ctypes import addressof, c_uint8
        >>> from libretro.api import retro_memory_descriptor
        >>> wram = (c_uint8 * 8)()
        >>> desc = retro_memory_descriptor(ptr=addressof(wram), len=8)
        >>> desc.view[0] = 0xFF
        >>> wram[0]
        255

        .. warning::
            The view is only valid for as long as the core keeps the region alive.
            Cores that rebuild their memory on reset or on loading new content
            should reregister the memory descriptors with the new addresses,
            otherwise the dangling pointer may cause a crash.

        .. note::
            This is a property named ``view`` rather than an implementation of
            :class:`~collections.abc.Buffer`,
            because :class:`ctypes.Structure` already exposes the descriptor's *own* bytes
            through the buffer protocol.

        :return: A :class:`memoryview` of this region's bytes,
            or :obj:`None` if :attr:`ptr` is :obj:`None`.
        :raises ValueError: If :attr:`len` is 0.
            A descriptor may legally omit its length
            and let the frontend derive it from the rest of the map;
            use :meth:`retro_memory_map.find` for that.

        .. seealso:: :meth:`retro_memory_map.find`
        """
        if (ptr := self.ptr) is None:
            return None

        if not self.len:
            raise ValueError("Cannot view a memory descriptor of unknown length")

        buffer = (c_uint8 * self.len).from_address((ptr.value or 0) + self.offset)
        view = memoryview(buffer).cast("B")
        return view.toreadonly() if self.flags & MemoryDescriptorFlag.CONST else view


_SIZE_MAX = 0xFFFF_FFFF_FFFF_FFFF
"""The largest value a 64-bit ``size_t`` can hold, used to emulate C's wraparound."""

_UINT_MAX = 0xFFFF_FFFF
"""The largest value a 32-bit ``unsigned`` can hold; frontends address memory with one."""


def _add_bits_down(n: int) -> int:
    """Set every bit below the highest set bit of ``n``."""
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n |= n >> 32
    return n


def _inflate(addr: int, mask: int) -> int:
    """Spread the bits of ``addr`` apart to make room for a zero at each bit set in ``mask``."""
    while mask:
        tmp = (mask - 1) & ~mask & _SIZE_MAX
        addr = (((addr & ~tmp & _SIZE_MAX) << 1) | (addr & tmp)) & _SIZE_MAX
        mask &= mask - 1

    return addr


def _reduce(addr: int, mask: int) -> int:
    """Remove each bit of ``addr`` that is set in ``mask``, closing the gaps left behind."""
    while mask:
        tmp = (mask - 1) & ~mask & _SIZE_MAX
        addr = (addr & tmp) | ((addr >> 1) & ~tmp & _SIZE_MAX)
        mask = (mask & (mask - 1)) >> 1

    return addr


def _highest_bit(n: int) -> int:
    """Return the highest set bit of ``n``, or 0 if it has none."""
    n = _add_bits_down(n)
    return n ^ (n >> 1)


@dataclass(slots=True)
class _Region:
    """The addressing fields of one descriptor, as a frontend's preprocessing pass leaves them."""

    start: int
    select: int
    disconnect: int
    len: int


def _preprocess(descriptors: Sequence[retro_memory_descriptor]) -> list[_Region]:
    """
    Fill in the addressing fields that each descriptor left for the frontend to derive.

    :param descriptors: The descriptors to preprocess; they are not modified.
    :return: One :class:`_Region` per descriptor, in the same order.
    :raises ValueError: If a descriptor is one that a frontend would reject.
    """
    top_addr = 1
    regions: list[_Region] = []

    for desc in descriptors:
        regions.append(_Region(desc.start, desc.select, desc.disconnect, desc.len))
        top_addr |= desc.select if desc.select else (desc.start + desc.len - 1) & _SIZE_MAX

    top_addr = _add_bits_down(top_addr)

    for i, region in enumerate(regions):
        if not region.select:
            if not region.len:
                raise ValueError(f"Descriptor {i} has neither a select mask nor a length")

            if region.len & (region.len - 1):
                raise ValueError(
                    f"Descriptor {i} has no select mask, "
                    f"so its length must be a power of two, but it is {region.len:#x}"
                )

            region.select = (
                top_addr & ~_inflate(_add_bits_down(region.len - 1), region.disconnect) & _SIZE_MAX
            )

        if not region.len:
            region.len = (
                _add_bits_down(_reduce(top_addr & ~region.select & _SIZE_MAX, region.disconnect))
                + 1
            )

        if region.start & ~region.select & _SIZE_MAX:
            raise ValueError(
                f"Descriptor {i} starts at {region.start:#x}, "
                f"which its select mask {region.select:#x} cannot match"
            )

        # Disconnect the unselected bits that are too high to ever index into the core's buffer,
        # so that addresses above the region's extent mirror it instead of falling off the end.
        highest_reachable = _inflate(region.len - 1, region.disconnect)
        while _highest_bit(
            top_addr & ~region.select & ~region.disconnect & _SIZE_MAX
        ) > _highest_bit(highest_reachable):
            region.disconnect |= _highest_bit(
                top_addr & ~region.select & ~region.disconnect & _SIZE_MAX
            )

    return regions


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

        Yields no elements when :attr:`descriptors` is :obj:`None`:

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

    def find(self, address: int) -> tuple[retro_memory_descriptor, int] | None:
        """
        Look up the descriptor that covers an address in the emulated machine's address space.

        Use this to reach the :class:`.Core`'s memory the way a frontend does,
        including the mirrors and gaps that the map describes.
        The address is resolved the same way RetroArch resolves one,
        so a map that RetroArch would read differently reads differently here too.

        Descriptors are searched in order and the first match wins,
        as ``libretro.h`` requires.
        A descriptor with no :attr:`~retro_memory_descriptor.select` mask
        matches only the addresses within its declared extent;
        all others match every address whose selected bits equal their
        :attr:`~retro_memory_descriptor.start`,
        which is how one buffer comes to appear at several addresses at once.

        The returned offset counts bytes into the descriptor's region,
        so a byte is read through
        :attr:`~retro_memory_descriptor.view`:

        >>> from ctypes import addressof, c_uint8
        >>> from libretro.api import retro_memory_descriptor, retro_memory_map
        >>> wram = (c_uint8 * 0x400000)()
        >>> wram[0x10] = 0x42
        >>> m = retro_memory_map([
        ...     retro_memory_descriptor(
        ...         ptr=addressof(wram),
        ...         start=0x02000000,
        ...         select=0xFF000000,
        ...         disconnect=0x00C00000,
        ...         len=0x400000,
        ...     ),
        ... ])
        >>> desc, offset = m.find(0x02000010)
        >>> desc.view[offset]
        66

        This map gives 16 MiB of address space to a 4 MiB buffer,
        so the same byte answers at three more addresses:

        >>> [m.find(a)[1] for a in (0x02400010, 0x02800010, 0x02C00010)]
        [16, 16, 16]

        .. note::
            The descriptor that comes back is the one the core sent,
            not the completed copy used to resolve the address.
            A descriptor that left its :attr:`~retro_memory_descriptor.len` at 0
            therefore still has it at 0,
            and :attr:`~retro_memory_descriptor.view` still refuses it.

        :param address: An address in the emulated machine's address space.
        :return: The matching descriptor and the offset of ``address`` within it,
            or :obj:`None` if no descriptor covers ``address``.
        :raises ValueError: If ``address`` doesn't fit in the 32 bits
            that frontends use to address core memory,
            or if this map contains a descriptor that a frontend would reject.

        .. seealso:: :attr:`retro_memory_descriptor.view`
        .. seealso:: :attr:`.EnvironmentCall.SET_MEMORY_MAPS`
        """
        if not 0 <= address <= _UINT_MAX:
            raise ValueError(f"Expected an address within 32 bits, got {address:#x}")

        descriptors = list(self)
        for desc, region in zip(descriptors, _preprocess(descriptors), strict=True):
            if not region.select:
                # Without a select mask, the descriptor covers one explicit range and no more
                if region.start <= address < region.start + region.len:
                    return desc, address - region.start
            elif not ((region.start ^ address) & region.select):
                # Drop the bits that this region doesn't use for addressing,
                # which is what folds a mirrored address back onto the buffer
                offset = _reduce(
                    (address - region.start) & _UINT_MAX, region.disconnect & _UINT_MAX
                )
                if offset < region.len:
                    return desc, offset

        return None

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
    "RETRO_MEMORY_ROM",
]
