"""
Runtime ``assert_type`` checks for :mod:`libretro.ctypes`.

These tests use :mod:`pytest_assert_type`, which AST-rewrites every
``assert_type(value, ExpectedType)`` call inside a function decorated
with :func:`pytest_assert_type.check` into a runtime check that fails
the test if the runtime value does not match the expected type.

The point is to lock in the actual :mod:`ctypes` conversion behaviour
described in :mod:`libretro.ctypes`. If a future :mod:`ctypes` change
collapses ``c_void_ptr`` to :class:`int`, or stops auto-converting a
``c_char_p`` return to :class:`bytes`, these tests fail loudly.
"""

from __future__ import annotations

from ctypes import (
    Structure,
    c_bool,
    c_char_p,
    c_float,
    c_int,
    c_int32,
    c_uint8,
    cast,
)
from typing import assert_type

import pytest_assert_type

from libretro.ctypes import (
    TypedFunctionPointer,
    TypedPointer,
    c_void_ptr,
)


class _Point(Structure):
    """A tiny struct used by the indexing tests below."""

    _fields_ = (("x", c_int), ("y", c_int))


class _WithVoidPtr(Structure):
    """A struct whose ``ptr`` field is :class:`c_void_ptr` instead of ``c_void_p``."""

    _fields_ = (("ptr", c_void_ptr),)


@pytest_assert_type.check
def test_c_void_ptr_constructor_returns_c_void_ptr() -> None:
    """``c_void_ptr(0)`` stays a ``c_void_ptr`` — it is not collapsed to ``int``."""
    value = c_void_ptr(0)
    assert_type(value, c_void_ptr)


@pytest_assert_type.check
def test_c_void_ptr_struct_field_round_trips_as_c_void_ptr() -> None:
    """A ``c_void_ptr`` struct member is read back as a ``c_void_ptr`` instance."""
    s = _WithVoidPtr()
    s.ptr = c_void_ptr(0xDEAD)
    assert_type(s.ptr, c_void_ptr)


@pytest_assert_type.check
def test_typed_pointer_to_c_int_indexes_to_python_int() -> None:
    arr = (c_int * 3)(10, 20, 30)
    p = cast(arr, TypedPointer[c_int])
    assert_type(p[0], int)


@pytest_assert_type.check
def test_typed_pointer_to_c_bool_indexes_to_python_bool() -> None:
    arr = (c_bool * 1)(True)
    p = cast(arr, TypedPointer[c_bool])
    assert_type(p[0], bool)


@pytest_assert_type.check
def test_typed_pointer_to_c_uint8_indexes_to_python_int() -> None:
    arr = (c_uint8 * 1)(0xAA)
    p = cast(arr, TypedPointer[c_uint8])
    assert_type(p[0], int)


@pytest_assert_type.check
def test_typed_array_of_c_float_indexes_to_python_float() -> None:
    a = (c_float * 2)(1.5, 2.5)
    assert_type(a[0], float)


@pytest_assert_type.check
def test_typed_array_of_c_int32_indexes_to_python_int() -> None:
    a = (c_int32 * 2)(10, 20)
    assert_type(a[0], int)


@pytest_assert_type.check
def test_typed_array_of_struct_indexes_to_struct_instance() -> None:
    a = (_Point * 2)(_Point(1, 2), _Point(3, 4))
    assert_type(a[0], _Point)


@pytest_assert_type.check
def test_typed_function_pointer_c_bool_return_is_python_bool() -> None:
    is_pos = TypedFunctionPointer[c_bool, [c_int]](lambda x: x > 0)
    assert_type(is_pos(5), bool)


@pytest_assert_type.check
def test_typed_function_pointer_c_int_return_is_python_int() -> None:
    add = TypedFunctionPointer[c_int, [c_int, c_int]](lambda a, b: a + b)
    assert_type(add(2, 3), int)


@pytest_assert_type.check
def test_typed_function_pointer_c_char_p_return_is_optional_bytes() -> None:
    echo = TypedFunctionPointer[c_char_p, [c_char_p]](lambda s: s)
    result = echo(b"hello")
    # ctypes returns bytes for a non-null c_char_p, or None for NULL.
    assert_type(result, bytes | None)


@pytest_assert_type.check
def test_typed_function_pointer_void_return_is_none() -> None:
    """A ``TypedFunctionPointer[None, []]`` call evaluates to ``None``."""
    noop = TypedFunctionPointer[None, []](lambda: None)
    result = noop()
    assert_type(result, type(None))
