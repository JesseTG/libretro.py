"""
Types for retrieving core functions beyond
the standard ``retro_*`` API functions exposed by :class:`.Core`.
"""

from ctypes import Structure
from dataclasses import dataclass

from libretro.ctypes import CStringArg, TypedFunctionPointer

retro_proc_address_t = TypedFunctionPointer[None, []]
"""
Opaque function pointer returned by :c:type:`retro_get_proc_address_t`.

Despite this declaration, the underlying function may have any signature;
use :func:`ctypes.cast` to convert it to a :class:`~ctypes.CFUNCTYPE`
or :class:`.TypedFunctionPointer` with the correct prototype before invoking it.

.. danger::

    When calling a function pointer obtained from :c:type:`retro_get_proc_address_t`,
    ensure that the signature matches the expected function prototype
    and that it follows the C ABI (e.g. with ``extern "C"`` in C++).
    Mismatched signatures or calling conventions can lead to undefined behavior.

Corresponds to :c:type:`retro_proc_address_t` in ``libretro.h``.
"""

retro_get_proc_address_t = TypedFunctionPointer[retro_proc_address_t, [CStringArg]]
"""
Look up an exported function pointer in the core by symbol name.

Registered by the :term:`core` and called by the :term:`frontend`
to access libretro extensions implemented by the core.

:param sym: The symbol name to look up, as a :obj:`bytes`-like object.
:return: A :class:`.c_void_ptr` to the matching :c:type:`retro_proc_address_t`,
    or :obj:`None` if the core does not export a function with that name.

.. note::
    The returned pointer must be cast to the correct function signature before use.

Corresponds to :c:type:`retro_get_proc_address_t` in ``libretro.h``.
"""


@dataclass(init=False, slots=True)
class retro_get_proc_address_interface(Structure):
    """
    An interface to get function pointers directly from a :class:`.Core`.

    Corresponds to :c:type:`retro_get_proc_address_interface` in ``libretro.h``.
    """

    get_proc_address: retro_get_proc_address_t | None
    """Retrieves a function pointer by symbol name."""

    _fields_ = (("get_proc_address", retro_get_proc_address_t),)

    def __call__(self, sym: str | bytes) -> retro_proc_address_t | None:
        """
        Call :attr:`get_proc_address` with the given symbol name.

        :param sym: Symbol name as a string or bytes.
        :returns: The function pointer, or :obj:`None` if not found.
        :raises ValueError: If :attr:`get_proc_address` is :obj:`None`.
        :raises TypeError: If ``sym`` is not :class:`str` or :class:`bytes`.
        """
        if not self.get_proc_address:
            raise ValueError("get_proc_address is NULL")

        match sym:
            case str():
                sym_bytes = sym.encode("utf-8")
            case bytes():
                sym_bytes = sym
            case _:
                raise TypeError(f"sym must be str or bytes, got {type(sym).__name__}")

        return self.get_proc_address(sym_bytes)

    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_get_proc_address_interface(self.get_proc_address)


__all__ = [
    "retro_get_proc_address_interface",
    "retro_proc_address_t",
    "retro_get_proc_address_t",
]
