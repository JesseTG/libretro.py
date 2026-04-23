"""
Python equivalents of the C data structures defined in
`libretro.h <https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h>`_.

Almost all types in this module are :mod:`ctypes`-based wrappers around
their equivalents in ``libretro.h``.

Although these types are primarily meant to be used with
the drivers in :mod:`libretro.drivers`,
they do not depend on any driver protocols or implementations.

They follow these conventions unless otherwise stated:

======
Naming
======

* All function pointer types and :class:`~.ctypes.Structure` subclasses
  are named exactly the same as their C counterparts.
* All explicit :c:expr:`enum` types are given ``CamelCase`` names
  that match the name of their C counterparts with the common ``RETRO_`` prefix removed.
* All groups of related ``#define`` constants are given ``CamelCase`` type names
  derived from their common prefix in C.
* All enum values (both explicit and :c:expr:`#define` s )
  are named in ``ALL_CAPS_SNAKE_CASE``, with their common prefix removed.

================
Type Conversions
================

This module's types rely heavily on the conversions defined by :mod:`ctypes`.
The linked documentation provides details, but in a nutshell:

* Python objects are implicitly converted to equivalent C data types when:
    * Assigned to a :class:`~ctypes.Structure` field, or;
    * Stored as an element in an appropriately-typed :class:`~ctypes.Array`, or;
    * Assigned as the target of a :class:`~ctypes._Pointer` (or equivalent :class:`.TypedPointer`), or;
    * Passed as an argument to a C function defined with :func:`~ctypes.CFUNCTYPE`
      (or the equivalent :class:`.TypedFunctionPointer`).
* C data types are implicitly converted to equivalent :mod:`ctypes` objects or Python primitives when:
    * Accessed as a field of a :class:`~ctypes.Structure`, or;
    * Accessed as an element of an :class:`~ctypes.Array`, or;
    * Accessed as the target of a :class:`~ctypes._Pointer` (or equivalent :class:`.TypedPointer`), or;
    * Returned as the result of a C function defined with :func:`~ctypes.CFUNCTYPE`
      (or the equivalent :class:`.TypedFunctionPointer`).
* Python classes that implement :class:`.AsParameter`
  can be implicitly converted to C data types when passed to :func:`~ctypes.CFUNCTYPE`-defined functions.
* C integers are converted to Python :class:`int` s regardless of their size or signedness.
* Python :class:`int` s are masked to fit the size and signedness
  of the target C integer type when converted to C.
* C floating-point types are converted to and from Python :class:`float` s.
* Python :class:`bytes` objects are converted to and from ``NULL``-terminated :c:expr:`char *` s.
* ``NULL`` C pointers of any type are converted to and from :obj:`None`.
* C :c:expr:`bool` s are converted to and from Python :class:`bool` s.
* C :c:expr:`void *` pointers are converted to and from :class:`int` s.
* Subclasses of any :mod:`ctypes` type are _not_ implicitly converted to Python primitives.

.. seealso::

    :mod:`libretro.ctypes`
        Various :mod:`ctypes`-compatible types and utility functions.

==================
Additional Methods
==================

---------------------
:func:`copy.deepcopy`
---------------------

Unless otherwise noted, all structs can be copied with :func:`copy.deepcopy`;
the struct itself and its fields (including strings and buffers) are all deep-copied.
For example:

.. code-block:: python

        import copy
        from libretro.api import retro_controller_description

        desc = retro_controller_description(b'Game Pad', 5)
        desc_copy = copy.deepcopy(desc)

        assert desc == desc_copy

        desc.desc = b'Another Game Pad'
        assert desc != desc_copy

--------------------
Collection Protocols
--------------------

Where applicable, structs that logically represent arrays of items (e.g. :class:`~.retro_controller_info`)
implement :class:`collections.abc.Sequence` to allow indexing and iteration over the items,
plus ``__setitem__`` to update values. For example:

.. code-block:: python

        from libretro.api import retro_controller_info

        info = retro_controller_info()
        info.num_descriptions = 2
        info.descriptions[0] = retro_controller_description(b'Game Pad', 5)
        info.descriptions[1] = retro_controller_description(b'Analog Stick', 2)

        assert len(info) == 2
        assert info[0].desc == b'Game Pad'
        assert info[1].desc == b'Analog Stick'

.. seealso:: :mod:`libretro.drivers` for driver protocols that use these types.
"""

from .audio import *
from .av import *
from .camera import *
from .content import *
from .disk import *
from .environment import *
from .input import *
from .led import *
from .location import *
from .log import *
from .memory import *
from .message import *
from .microphone import *
from .midi import *
from .netpacket import *
from .options import *
from .perf import *
from .power import *
from .proc import *
from .rumble import *
from .savestate import *
from .sensor import *
from .timing import *
from .user import *
from .vfs import *
from .video import *
