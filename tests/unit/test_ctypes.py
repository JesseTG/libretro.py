"""
Runtime behaviour tests for :mod:`libretro.ctypes`.

These tests assert that the ``ctypes`` refinement layer
(``TypedPointer``, ``TypedArray``, ``TypedFunctionPointer``, ``Pointer``,
and ``c_void_ptr``) behaves identically to the underlying ``ctypes``
factories that it erases to at runtime.
"""

from __future__ import annotations

import operator
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Array,
    Structure,
    c_bool,
    c_char_p,
    c_float,
    c_int,
    c_int32,
    c_uint8,
    c_void_p,
    cast,
)

from libretro.ctypes import (
    CIntArg,
    CStringArg,
    Pointer,
    TypedArray,
    TypedFunctionPointer,
    TypedPointer,
    c_void_ptr,
)


def ident[T](t: T) -> T:
    return t


def test_c_void_ptr_is_c_void_p_subclass() -> None:
    """Anywhere a ``c_void_p`` works, a ``c_void_ptr`` should too."""
    assert issubclass(c_void_ptr, c_void_p)
    assert isinstance(c_void_ptr(0), c_void_p)


def test_c_void_ptr_repr_uses_hex() -> None:
    assert repr(c_void_ptr(0x1234)) == "c_void_ptr(0x1234)"


def test_c_void_ptr_repr_uses_null() -> None:
    assert repr(c_void_ptr(0)) == "c_void_ptr(NULL)"


def test_c_void_ptr_value_round_trips() -> None:
    """``value`` returns the integer assigned at construction time."""
    ptr = c_void_ptr(0xDEADBEEF)
    assert ptr.value == 0xDEADBEEF


def test_typed_pointer_resolves_to_POINTER_at_runtime() -> None:
    """``TypedPointer[X]`` and ``POINTER(X)`` are the same factory."""
    assert TypedPointer[c_int] is POINTER(c_int)


def test_pointer_resolves_to_POINTER_at_runtime() -> None:
    """``Pointer[X]`` is the cached ``POINTER(X)`` factory."""
    assert Pointer[c_int] is POINTER(c_int)


def test_typed_pointer_indexes_primitives_back_to_python_ints() -> None:
    arr = (c_int * 3)(10, 20, 30)
    p = cast(arr, TypedPointer[c_int])
    assert p[0] == 10
    assert p[2] == 30
    p[0] = 99
    assert arr[0] == 99


def test_typed_pointer_to_struct_returns_struct_instance() -> None:
    class Pt(Structure):
        _fields_ = (("x", c_int), ("y", c_int))

    pts = (Pt * 2)(Pt(7, 8), Pt(13, 21))
    pp = cast(pts, TypedPointer[Pt])
    assert pp[1].x == 13
    assert pp[1].y == 21


def test_typed_array_is_ctypes_Array_at_runtime() -> None:
    assert TypedArray is Array


def test_typed_array_iteration_yields_python_ints() -> None:
    a = (c_int * 4)(1, 2, 3, 4)
    assert list(a) == [1, 2, 3, 4]


def test_typed_array_slicing_returns_list_of_python_primitives() -> None:
    a = (c_int * 4)(1, 2, 3, 4)
    sliced = a[1:3]
    assert sliced == [2, 3]
    assert isinstance(sliced, list)


def test_typed_array_setitem_accepts_python_primitive() -> None:
    a = (c_int * 2)(0, 0)
    a[0] = 42
    assert a[0] == 42


def test_typed_array_setitem_accepts_ctypes_primitive() -> None:
    a = (c_int * 2)(0, 0)
    a[1] = c_int(99)
    assert a[1] == 99


def test_typed_function_pointer_resolves_to_CFUNCTYPE_at_runtime() -> None:
    assert TypedFunctionPointer[c_int, [c_int]] == CFUNCTYPE(c_int, c_int)


def test_typed_function_pointer_bool_return_converts_to_python_bool() -> None:
    as_bool = TypedFunctionPointer[c_bool, [CIntArg[c_int]]](ident)
    assert as_bool(0) is False
    assert as_bool(42) is True


def test_typed_function_pointer_int_return_converts_to_python_int() -> None:
    add = TypedFunctionPointer[c_int, [CIntArg[c_int], CIntArg[c_int]]](operator.add)
    assert add(2, 3) == 5


def test_typed_function_pointer_bytes_return_converts_to_python_bytes() -> None:
    echo = TypedFunctionPointer[c_char_p, [CStringArg]](ident)
    assert echo(b"hello") == b"hello"


def test_typed_function_pointer_void_return_is_none() -> None:
    noop = TypedFunctionPointer[None, []](lambda: None)
    assert noop() is None


def test_as_parameter_protocol_accepts_user_type() -> None:
    """Classes that implement ``_as_parameter_`` work as a CFUNCTYPE arg."""

    class Boxed:
        def __init__(self, value: int) -> None:
            self._as_parameter_ = c_int(value)

    echo = CFUNCTYPE(c_int, c_int)(ident)
    assert echo(Boxed(42)) == 42
    # The Protocol declaration exists for typing; we exercise it
    # structurally rather than via isinstance.
    assert hasattr(Boxed(0), "_as_parameter_")


def test_typed_pointer_float_round_trip() -> None:
    arr = (c_float * 2)(1.5, 2.5)
    p = cast(arr, TypedPointer[c_float])
    assert p[0] == 1.5
    p[0] = -3.25
    assert arr[0] == -3.25


def test_typed_pointer_uint8_round_trip() -> None:
    arr = (c_uint8 * 4)(0xAA, 0xBB, 0xCC, 0xDD)
    p = cast(arr, TypedPointer[c_uint8])
    assert p[0] == 0xAA
    assert p[3] == 0xDD


def test_pointer_factory_caches_across_subscript_styles() -> None:
    """Both ``Pointer[T]`` and ``TypedPointer[T]`` resolve to the same cached factory."""
    assert Pointer[c_int32] is TypedPointer[c_int32]
