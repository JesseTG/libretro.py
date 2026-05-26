"""
Property-based tests for :mod:`libretro.ctypes` conversion behavior.

Each test exercises one direction of the implicit :mod:`ctypes`
conversions documented for the refinement layer — values flow through a
``TypedPointer``, ``TypedArray``, ``TypedFunctionPointer``, or
``Structure`` field and must come back equal to what went in.
"""

from __future__ import annotations

import copy
from ctypes import (
    c_char_p,
    c_float,
    c_int8,
    c_int32,
    c_uint8,
    c_uint32,
    cast,
)

from hypothesis import given
from hypothesis import strategies as st

from libretro.api import retro_game_info, retro_message_ext
from libretro.ctypes import TypedFunctionPointer, TypedPointer


@given(value=st.integers(min_value=-(2**31), max_value=2**31 - 1))
def test_typed_pointer_int32_round_trip(value: int) -> None:
    """Writing then reading a ``c_int32`` via a pointer preserves the value."""
    arr = (c_int32 * 1)()
    p = cast(arr, TypedPointer[c_int32])
    p[0] = value
    assert p[0] == value
    assert arr[0] == value


@given(value=st.integers(min_value=0, max_value=2**32 - 1))
def test_typed_pointer_uint32_round_trip(value: int) -> None:
    arr = (c_uint32 * 1)()
    p = cast(arr, TypedPointer[c_uint32])
    p[0] = value
    assert p[0] == value


@given(value=st.integers(min_value=-128, max_value=127))
def test_typed_pointer_int8_round_trip(value: int) -> None:
    arr = (c_int8 * 1)()
    p = cast(arr, TypedPointer[c_int8])
    p[0] = value
    assert p[0] == value


@given(value=st.integers(min_value=0, max_value=255))
def test_typed_pointer_uint8_round_trip(value: int) -> None:
    arr = (c_uint8 * 1)()
    p = cast(arr, TypedPointer[c_uint8])
    p[0] = value
    assert p[0] == value


@given(value=st.floats(allow_nan=False, allow_infinity=False, width=32))
def test_typed_pointer_float_round_trip(value: float) -> None:
    """``c_float`` round-trips through ``TypedPointer`` within float32 precision."""
    arr = (c_float * 1)()
    p = cast(arr, TypedPointer[c_float])
    p[0] = value
    # c_float is single-precision, so compare against the float32-rounded value
    assert p[0] == c_float(value).value


@given(values=st.lists(st.integers(min_value=-(2**31), max_value=2**31 - 1), max_size=64))
def test_typed_array_int32_iteration_matches_input(values: list[int]) -> None:
    if not values:
        # An empty array can't be constructed from an empty *args list,
        # so guard against that case explicitly.
        return
    arr = (c_int32 * len(values))(*values)
    assert list(arr) == values


@given(
    values=st.lists(
        st.floats(allow_nan=False, allow_infinity=False, width=32),
        min_size=1,
        max_size=32,
    )
)
def test_typed_array_float_iteration_matches_input(values: list[float]) -> None:
    arr = (c_float * len(values))(*values)
    expected = [c_float(v).value for v in values]
    assert list(arr) == expected


@given(
    msg=st.binary(min_size=0, max_size=128),
    duration=st.integers(min_value=0, max_value=2**31 - 1),
    priority=st.integers(min_value=0, max_value=2**31 - 1),
    progress=st.integers(min_value=-1, max_value=100),
)
def test_retro_message_ext_round_trip_through_deepcopy(
    msg: bytes, duration: int, priority: int, progress: int
) -> None:
    """Hypothesis-generated values survive a ``copy.deepcopy`` of ``retro_message_ext``."""
    m = retro_message_ext(msg=msg, duration=duration, priority=priority, progress=progress)
    dup = copy.deepcopy(m)
    assert dup is not m
    assert dup.msg == m.msg
    assert dup.duration == m.duration
    assert dup.priority == m.priority
    # progress is c_int8 (signed), so -1..100 will fit naturally.
    assert dup.progress == m.progress


# c_char_p truncates at the first NUL, so restrict the strategy to NUL-free bytes
_nul_free_bytes = st.binary(min_size=0, max_size=64).filter(lambda b: b"\x00" not in b)


@given(
    path=st.one_of(st.none(), _nul_free_bytes.filter(bool)),
    size=st.integers(min_value=0, max_value=2**31 - 1),
    meta=st.one_of(st.none(), _nul_free_bytes),
)
def test_retro_game_info_string_fields_round_trip(
    path: bytes | None, size: int, meta: bytes | None
) -> None:
    info = retro_game_info(path=path, size=size, meta=meta)
    assert info.path == path
    assert info.size == size
    assert info.meta == meta


@given(value=st.integers(min_value=-(2**31), max_value=2**31 - 1))
def test_typed_function_pointer_int_argument_round_trip(value: int) -> None:
    """Calling a ``TypedFunctionPointer[c_int32, [c_int32]]`` returns its int input."""
    echo = TypedFunctionPointer[c_int32, [c_int32]](lambda x: x)
    assert echo(value) == value


@given(value=st.booleans())
def test_typed_function_pointer_bool_argument_round_trip(value: bool) -> None:
    from ctypes import c_bool

    echo = TypedFunctionPointer[c_bool, [c_bool]](lambda x: x)
    assert echo(value) == value


@given(payload=st.binary(min_size=0, max_size=128))
def test_typed_function_pointer_bytes_argument_round_trip(payload: bytes) -> None:
    """``c_char_p`` arguments survive a round-trip through a CFUNCTYPE callback."""
    echo = TypedFunctionPointer[c_char_p, [c_char_p]](lambda s: s)
    # NULL bytes truncate C strings; only verify up to the first NUL.
    expected = payload.split(b"\x00", 1)[0] if b"\x00" in payload else payload
    result = echo(payload)
    assert result == expected
