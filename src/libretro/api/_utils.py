# pyright: reportPrivateUsage=false
# Some of these functions and type declarations
# rely on `ctypes` APIs that are technically private.
# However, their interfaces are documented and they're part of typeshed.

import ctypes
import mmap
import struct
import sys
from collections.abc import Buffer, Iterator, Sized
from contextlib import contextmanager
from copy import deepcopy
from ctypes import (
    Array,
    _Pointer,
    addressof,
    c_char_p,
    c_int,
    c_ssize_t,
    c_ubyte,
    c_uint8,
    c_void_p,
    py_object,
    pythonapi,
    sizeof,
)
from os import PathLike
from typing import TYPE_CHECKING, Any, Literal, Protocol, overload

from libretro.typing import TypedPointer

if TYPE_CHECKING:
    from ctypes import _CData, _CDataType


@overload
def as_bytes(value: str | bytes) -> bytes: ...


@overload
def as_bytes(value: None) -> None: ...


def as_bytes(value: str | bytes | None) -> bytes | None:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def is_zeroed(struct: _CData | _CDataType) -> bool:
    """
    Returns true if the given ``ctypes`` type is zeroed (all bytes are zero).
    """
    view = memoryview_at(addressof(struct), sizeof(struct), True)

    return not any(view)


def from_zero_terminated[T: _CData](ptr: _Pointer[T] | None) -> Iterator[T]:
    """
    Returns an iterator that yields items from a zero-terminated array of ``ctypes`` types.
    The iterator will stop when it encounters an item that is zeroed (all bytes are zero).
    If no such item exists, the behavior is undefined.

    If ptr is ``None``, the iterator will be empty.
    """
    if ptr:
        i = 0
        while not is_zeroed(ptr[i]):
            yield ptr[i]
            i += 1


MemoDict = dict[int, Any] | None


@overload
def deepcopy_array(array: None, length: int, memo: MemoDict) -> None: ...


@overload
def deepcopy_array[
    T: _CDataType
](array: _Pointer[T] | Array[T], length: int, memo: MemoDict = None) -> Array[T] | None: ...
@overload
def deepcopy_array[T: _CDataType](array: Array[T], length: MemoDict = None) -> Array[T] | None: ...


def deepcopy_array[
    T: _CDataType
](array: _Pointer[T] | Array[T] | None, length: int | MemoDict = None, memo: MemoDict = None) -> (
    Array[T] | None
):
    if not array:
        return None

    match array, length, memo:
        case Array(), dict() | None, None:
            arraylength = len(array)
            array_type = array._type_ * arraylength
            memodict = length
        case Array(), int(length), _ if length > len(array):
            raise ValueError(f"Expected length to be at most {len(array)}, got {length}")
        case Array(), int(length), dict() | None:
            arraylength = length
            array_type = array._type_ * arraylength
            memodict = memo
        case _Pointer(), int(length), dict() | None:
            arraylength = length
            array_type = array._type_ * arraylength
            memodict = memo
        case _:
            raise TypeError(f"Invalid arguments: {array}, {length}, {memo}")

    return array_type(*(deepcopy(array[i], memodict) for i in range(arraylength)))


@overload
def deepcopy_buffer(ptr: None | Literal[0], size: int) -> Array[c_uint8]: ...


@overload
def deepcopy_buffer(ptr: c_void_p | int, size: int) -> Array[c_uint8] | None: ...


def deepcopy_buffer(ptr: c_void_p | int | None, size: int) -> Array[c_uint8] | None:
    if ptr is not None and not isinstance(ptr, (c_void_p, int)):
        raise TypeError(f"Expected c_void_p or int, got {type(ptr).__name__}")

    if not ptr:
        return None

    if not size:
        return None

    address = ptr if isinstance(ptr, int) else ptr.value

    if not address:
        return None

    array_type = c_uint8 * size
    existing_buffer = memoryview_at(address, size, True)
    return array_type.from_buffer_copy(existing_buffer)


@contextmanager
def mmap_file(
    path: str | bytes | PathLike[str] | PathLike[bytes], mode: str = "rb"
) -> Iterator[memoryview[int]]:
    with open(path, mode, buffering=0) as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY) as m:
            view = memoryview(m)
            try:
                yield view
            finally:
                view.release()
            # If we don't release the memoryview manually,
            # we'll get a BufferError when the context manager exits
        f.close()


class SizedBuffer(Sized, Buffer, Protocol):
    pass


def addressof_buffer(buffer: SizedBuffer) -> int:
    array_type = c_ubyte * len(buffer)
    buffer_array = array_type.from_buffer(buffer)

    return ctypes.addressof(buffer_array)


if sys.version_info >= (3, 14):
    from ctypes import memoryview_at
else:
    # ctypes.memoryview_at was added in Python 3.14,
    # so we need to define it ourselves for older versions.
    # Taken from https://stackoverflow.com/a/72968176/1089957
    pythonapi.PyMemoryView_FromMemory.argtypes = (c_char_p, c_ssize_t, c_int)
    pythonapi.PyMemoryView_FromMemory.restype = py_object

    def memoryview_at[
        T: _CDataType
    ](
        address: c_char_p | c_void_p | int | bytes | TypedPointer[T],
        size: int,
        readonly: bool = False,
    ) -> memoryview[int]:
        flags = 0x100 if readonly else 0x200
        return pythonapi.PyMemoryView_FromMemory(address, size, flags)


if TYPE_CHECKING:

    class c_uintptr(ctypes._SimpleCData[int]):
        pass

else:
    if struct.calcsize("P") == struct.calcsize("Q"):
        c_uintptr = ctypes.c_uint64
    elif struct.calcsize("P") == struct.calcsize("I"):
        c_uintptr = ctypes.c_uint32
    else:

        class c_uintptr(ctypes._SimpleCData[int]):
            # Weird pointer size, but who am I to judge?
            _type_ = "P"


__all__ = [
    "as_bytes",
    "is_zeroed",
    "from_zero_terminated",
    "deepcopy_array",
    "deepcopy_buffer",
    "mmap_file",
    "addressof_buffer",
    "memoryview_at",
    "c_uintptr",
]
