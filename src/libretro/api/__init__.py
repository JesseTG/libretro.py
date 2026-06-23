r"""
Python equivalents of the C data structures defined in
`libretro.h <https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h>`_.

Almost all types in this module are :mod:`ctypes`-based wrappers around
their equivalents in ``libretro.h``.

Although these types are primarily meant to be used with
the drivers in :mod:`libretro.drivers`,
they do not depend on any driver protocols or implementations.
You can use them independently of libretro.py's drivers.

They follow these conventions unless otherwise stated:

======
Naming
======

* All function pointer types and :class:`~.ctypes.Structure` subclasses
  are named exactly the same as their C counterparts.
* All explicit ``enum`` types are given ``CamelCase`` names
  that match the name of their C counterparts with the common ``RETRO_`` prefix removed.
* All groups of related ``#define`` constants are given ``CamelCase`` type names
  derived from their common prefix in C.
* All enum values (both explicit and ``#define``\s )
  are named in ``ALL_CAPS_SNAKE_CASE``, with their common prefix removed.

================
Type Conversions
================

This module's types rely heavily on the conversions defined by :mod:`ctypes`.
The linked documentation provides details, but in a nutshell:

* Python objects are implicitly converted to equivalent C data types when:
    * Assigned to a :class:`~ctypes.Structure` field, or;
    * Stored as an element in an appropriately-typed :class:`~ctypes.Array`, or;
    * Assigned as the target of a :class:`~ctypes._Pointer` (or equivalent :class:`~libretro.ctypes.TypedPointer`), or;
    * Passed as an argument to a C function defined with :func:`~ctypes.CFUNCTYPE`
      (or the equivalent :class:`~libretro.ctypes.TypedFunctionPointer`).
* C data types are implicitly converted to equivalent :mod:`ctypes` objects or Python primitives when:
    * Accessed as a field of a :class:`~ctypes.Structure`, or;
    * Accessed as an element of an :class:`~ctypes.Array`, or;
    * Accessed as the target of a :class:`~ctypes._Pointer` (or equivalent :class:`~libretro.ctypes.TypedPointer`), or;
    * Returned as the result of a C function defined with :func:`~ctypes.CFUNCTYPE`
      (or the equivalent :class:`~libretro.ctypes.TypedFunctionPointer`).
* Python classes that implement :class:`~libretro.ctypes.AsParameter`
  can be implicitly converted to C data types when passed to :func:`~ctypes.CFUNCTYPE`-defined functions.
* C integers are converted to Python :class:`int`\s regardless of their size or signedness.
* Python :class:`int`\s are masked to fit the size and signedness
  of the target C integer type when converted to C.
* C floating-point types are converted to and from Python :class:`float`\s.
* Python :class:`bytes` objects are converted to and from ``NULL``-terminated :c:expr:`char *`\s.
* ``NULL`` C pointers of any type are converted to and from :obj:`None`.
* C :c:expr:`bool`\s are converted to and from Python :class:`bool`\s.
* C :c:expr:`void *` pointers are converted to and from :class:`int`\s.
* Subclasses of any :mod:`ctypes` primitive are *not* implicitly converted to Python primitives.

.. seealso::

    :mod:`libretro.ctypes`
        Various :mod:`ctypes`-compatible types and utility functions.

==================
Additional Methods
==================

-----------------------------------------
Dataclass Operations
-----------------------------------------

All structs are valid :func:`dataclasses <dataclasses.dataclass>`.
Unless otherwise noted, they support these operations:

^^^^^^^^^^
``__eq__``
^^^^^^^^^^

libretro.py structs can be compared for equality:

>>> from libretro.api import retro_system_timing
>>> timing = retro_system_timing(fps=60.0, sample_rate=44100)
>>> timing == retro_system_timing(60, 44100)
True
>>> timing == retro_system_timing(59.9, 44100)
False

.. warning::
  Most :mod:`ctypes` pointers are only compared for identity, *not* for value!
  This means that two different pointer objects will always compare nonequal,
  even if they refer to the same address.

  >>> from ctypes import c_void_p
  >>> ptr1 = c_void_p(0xdeadbeef)
  >>> ptr2 = c_void_p(0xdeadbeef) # same address...
  >>> ptr1 == ptr2
  False
  >>> ptr1.value == ptr2.value
  True

  This goes for :class:`~ctypes.c_void_p`, :class:`~ctypes.c_char_p`,
  and anything returned by :func:`~ctypes.CFUNCTYPE` and :func:`~ctypes.POINTER`
  (or the equivalent :class:`.TypedFunctionPointer` and :class:`.TypedPointer`):

  If you want to compare two pointers for equality,
  :func:`~ctypes.cast` them  to :class:`~ctypes.c_void_p`
  and check their :attr:`~_SimpleCData.value`\s:

  >>> from ctypes import cast, c_char_p
  >>> ptr1 = c_char_p(0xdeadbeef)
  >>> ptr2 = c_char_p(0xdeadbeef) # same address going in...
  >>> addr1 = cast(ptr1, c_void_p).value
  >>> addr2 = cast(ptr2, c_void_p).value # same address coming out...
  >>> addr1 == addr2
  True
  >>> ptr1 == ptr2 # huh?
  False

  To stay consistent with :mod:`ctypes`,
  libretro.py structs that contain pointers will maintain this behavior.
  This means that **two libretro.py structs that contain pointers will compare as unequal.**

  >>> from ctypes import cast, c_void_p
  >>> from libretro.api import retro_led_interface, retro_set_led_state_t
  >>> ptr = retro_set_led_state_t(0xdeadbeef) # pointer to a function at this address
  >>> iface1 = retro_led_interface(ptr)
  >>> iface2 = retro_led_interface(ptr)
  >>> iface1 == iface2 # They're unequal!
  False
  >>> addr1 = cast(iface1.set_led_state, c_void_p).value
  >>> addr2 = cast(iface2.set_led_state, c_void_p).value
  >>> addr1 == addr2 # But they both point to the same thing!
  True

  **...with one exception!**
  Although :mod:`ctypes` pointer objects can be empty
  (i.e. they can point to ``NULL``),
  libretro.py will replace them with :obj:`None` when used as struct fields.

  >>> from libretro.api import retro_log_callback
  >>> log_a = retro_log_callback()
  >>> log_b = retro_log_callback() # both have a log field initialized to NULL
  >>> log_a.log # will be None
  >>> log_a.log == log_b.log
  True
  >>> log_a == log_b
  True

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

>>> from collections.abc import Sequence
>>> from libretro.api import retro_controller_info
>>> info = retro_controller_info([
...     retro_controller_description(b'Game Pad'),
...     retro_controller_description(b'Analog Stick')
... ])
>>> isinstance(info, Sequence)
True
>>> len(info) == 2
True
>>> info[0].desc == b'Game Pad'
True
>>> info[1].desc == b'Analog Stick'
True

.. seealso:: :mod:`libretro.drivers` for driver protocols that use these types.
"""

from .audio import *
from .av import *
from .camera import *
from .content import *
from .disk import *
from .environment import *
from .input.analog import *
from .input.device import *
from .input.joypad import *
from .input.keyboard import *
from .input.lightgun import *
from .input.mouse import *
from .input.pointer import *
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
