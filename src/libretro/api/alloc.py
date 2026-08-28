"""
Types for memory that a :class:`.Core` negotiates with the frontend.

Covers executable memory for just-in-time compilation
and the frontend's report of host memory availability.
Distinct from :mod:`libretro.api.memory`,
which describes the address space of the core's *emulated* memory.

.. seealso::

    :class:`.EnvironmentDriver`
        The :class:`~typing.Protocol` that exposes these types to a :class:`.Core`.

    :mod:`libretro.drivers.environment`
        libretro.py's included :class:`.EnvironmentDriver` implementations.
"""

from ctypes import Structure, c_size_t, c_uint, c_uint64
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import NullPointerToNoneMixin
from libretro.ctypes import c_void_ptr

RETRO_EXEC_MEM_MODE_UNAVAILABLE = 0
"""The frontend cannot provide executable memory at all."""

RETRO_EXEC_MEM_MODE_UNRESTRICTED = 1
"""
The platform places no restrictions on executable memory,
so the core should allocate its own.

Cores must not request a non-zero size in this mode.
"""

RETRO_EXEC_MEM_MODE_RWX = 2
"""
A single readable, writable, and executable mapping.

:attr:`.retro_exec_mem_alloc.rx` and :attr:`.retro_exec_mem_alloc.rw`
point to the same region.
"""

RETRO_EXEC_MEM_MODE_WX_TOGGLE = 3
"""
A single mapping that is writable or executable, but never both at once.

:attr:`.retro_exec_mem_alloc.rx` and :attr:`.retro_exec_mem_alloc.rw`
point to the same region,
and the core must change the page protections itself
before writing to or executing from it.
"""

RETRO_EXEC_MEM_MODE_DUAL_MAP = 4
"""
Separate read-execute and read-write mappings of the same physical pages.

The core writes through :attr:`.retro_exec_mem_alloc.rw`
and executes from :attr:`.retro_exec_mem_alloc.rx`.
"""


class ExecMemMode(IntEnum):
    """
    Describes how the frontend provisions executable memory.

    Corresponds to the ``RETRO_EXEC_MEM_MODE_*`` constants in ``libretro.h``.

    >>> from libretro.api import ExecMemMode
    >>> ExecMemMode.DUAL_MAP
    <ExecMemMode.DUAL_MAP: 4>
    """

    UNAVAILABLE = RETRO_EXEC_MEM_MODE_UNAVAILABLE
    """No executable memory is available."""

    UNRESTRICTED = RETRO_EXEC_MEM_MODE_UNRESTRICTED
    """No platform restrictions; the core should allocate its own memory."""

    RWX = RETRO_EXEC_MEM_MODE_RWX
    """One mapping that is simultaneously readable, writable, and executable."""

    WX_TOGGLE = RETRO_EXEC_MEM_MODE_WX_TOGGLE
    """One mapping that is writable or executable, with the core toggling between them."""

    DUAL_MAP = RETRO_EXEC_MEM_MODE_DUAL_MAP
    """Separate read-execute and read-write mappings of the same pages."""


@dataclass(init=False, slots=True)
class retro_exec_mem_alloc(Structure, NullPointerToNoneMixin):
    """
    Request for a region of executable memory, used by cores that compile code at runtime.

    Corresponds to :c:type:`retro_exec_mem_alloc` in ``libretro.h``.

    The core sets :attr:`version` and :attr:`size` before the environment call;
    the frontend sets :attr:`mode`, :attr:`rx`, and :attr:`rw` on success.
    Memory returned by the frontend is page-aligned,
    and any allocation the core doesn't release is freed when the core is unloaded.

    Setting :attr:`size` to ``0`` makes the call a capability probe:
    the frontend reports what kind of memory it *would* provide in :attr:`mode`
    and leaves :attr:`rx` and :attr:`rw` set to :obj:`None`.

    .. warning::
        Unlike most structs in :mod:`libretro.api`,
        this one can't be copied with :func:`copy.deepcopy`.
        The mapping behind :attr:`rx` may be arbitrarily large,
        and an allocation's :attr:`mode` can't be reproduced
        without the driver that created it,
        so copying the pointers would alias the frontend's memory
        rather than duplicate it.
        The attempt raises instead of quietly returning an alias:

        >>> import copy
        >>> from libretro.api import retro_exec_mem_alloc
        >>> copy.deepcopy(retro_exec_mem_alloc())
        Traceback (most recent call last):
            ...
        TypeError: Can't copy retro_exec_mem_alloc; it refers to frontend-owned memory

    .. seealso::

        :attr:`.EnvironmentCall.EXEC_MEM_ALLOC`
            The environment call that fills in this struct.
    """

    version: int
    """
    Version of this struct that the core expects.
    Set by the core; currently ``1``.
    """

    size: int
    """
    Number of bytes requested, or ``0`` to probe for support without allocating.
    Set by the core.
    """

    mode: int
    """
    How the returned memory may be used, as an :class:`ExecMemMode` value.
    Set by the frontend.
    """

    rx: c_void_ptr | None
    """
    Pointer to execute the generated code from.
    Set by the frontend, or :obj:`None` for a probe.
    """

    rw: c_void_ptr | None
    """
    Pointer to write the generated code through.
    Set by the frontend, or :obj:`None` for a probe.

    Equal to :attr:`rx` when :attr:`mode` is
    :attr:`~ExecMemMode.RWX` or :attr:`~ExecMemMode.WX_TOGGLE`.
    """

    _fields_ = (
        ("version", c_uint),
        ("size", c_size_t),
        ("mode", c_uint),
        ("rx", c_void_ptr),
        ("rw", c_void_ptr),
    )

    def __deepcopy__(self, _=None):
        """
        Refuse to copy this struct.

        :raises TypeError: Always, as this method can't meet the semantics of a deep copy
        without involving the driver that allocated the memory.
        """
        raise TypeError("Can't copy retro_exec_mem_alloc; it refers to frontend-owned memory")


@dataclass(init=False, slots=True)
class retro_exec_mem_free(Structure, NullPointerToNoneMixin):
    """
    Request to release memory previously obtained with :class:`retro_exec_mem_alloc`.

    Corresponds to :c:type:`retro_exec_mem_free` in ``libretro.h``.

    Releasing memory is optional;
    the frontend frees whatever is outstanding when the core is unloaded.

    .. warning::
        Like :class:`retro_exec_mem_alloc`,
        this struct can't be copied with :func:`copy.deepcopy`.
        It holds nothing but a handle to memory the frontend owns,
        and a second handle to the same allocation invites a double free:

        >>> import copy
        >>> from libretro.api import retro_exec_mem_free
        >>> copy.deepcopy(retro_exec_mem_free())
        Traceback (most recent call last):
            ...
        TypeError: Can't copy retro_exec_mem_free; it refers to frontend-owned memory

    .. seealso::

        :attr:`.EnvironmentCall.EXEC_MEM_FREE`
            The environment call that consumes this struct.
    """

    rx: c_void_ptr | None
    """
    The :attr:`.retro_exec_mem_alloc.rx` pointer from a previous allocation.
    The matching :attr:`.retro_exec_mem_alloc.rw` pointer is also accepted.
    """

    _fields_ = (("rx", c_void_ptr),)

    def __deepcopy__(self, _=None):
        """
        Refuse to copy this struct.

        :raises TypeError: Always.
            :attr:`rx` identifies an allocation the frontend owns,
            so a copy would be a second handle to memory that only one owner may free.
        """
        raise TypeError("Can't copy retro_exec_mem_free; it refers to frontend-owned memory")


@dataclass(init=False, slots=True)
class retro_memory_status(Structure):
    """
    The frontend's report of how much system memory the host has.

    Corresponds to :c:type:`retro_memory_status` in ``libretro.h``.

    Cores use this to size large allocations
    (a memory pool, a heap, an asset cache)
    to the running machine rather than to a compile-time default.

    Both fields survive a round trip through :func:`copy.deepcopy`:

    >>> import copy
    >>> from libretro.api import retro_memory_status
    >>> status = retro_memory_status(free=1 << 30, total=1 << 33)
    >>> copy.deepcopy(status).free == status.free
    True

    .. seealso::

        :attr:`.EnvironmentCall.GET_MEMORY_STATUS`
            The environment call that fills in this struct.
    """

    free: int
    """
    Physical memory currently available to allocate, in bytes.
    ``0`` if the frontend couldn't determine it.

    .. warning::
        This is an advisory snapshot that may include reclaimable cache,
        and it can change immediately after the environment call returns.
        Cores should take a fraction of this value and clamp the result
        rather than assuming the whole amount is theirs to claim.
    """

    total: int
    """
    Total physical memory installed on the host, in bytes.
    ``0`` if the frontend couldn't determine it.
    """

    _fields_ = (
        ("free", c_uint64),
        ("total", c_uint64),
    )

    def __deepcopy__(self, _):
        """
        Return a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_memory_status
        >>> copy.deepcopy(retro_memory_status()).total
        0
        """
        return retro_memory_status(self.free, self.total)


__all__ = [
    "RETRO_EXEC_MEM_MODE_UNAVAILABLE",
    "RETRO_EXEC_MEM_MODE_UNRESTRICTED",
    "RETRO_EXEC_MEM_MODE_RWX",
    "RETRO_EXEC_MEM_MODE_WX_TOGGLE",
    "RETRO_EXEC_MEM_MODE_DUAL_MAP",
    "ExecMemMode",
    "retro_exec_mem_alloc",
    "retro_exec_mem_free",
    "retro_memory_status",
]
