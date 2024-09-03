import ctypes
import mmap
from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from ctypes import (
    POINTER,
    Array,
    Structure,
    addressof,
    c_char_p,
    c_double,
    c_int,
    c_int16,
    c_int32,
    c_int64,
    c_size_t,
    c_ssize_t,
    c_ubyte,
    c_uint8,
    c_void_p,
    cast,
    py_object,
    pythonapi,
    sizeof,
)
from os import PathLike
from typing import TypeAlias, get_type_hints

from libretro._typing import Buffer

# When https://github.com/python/cpython/issues/112015 is merged,
# use ctypes.memoryview_at instead of this hack
# taken from https://stackoverflow.com/a/72968176/1089957
pythonapi.PyMemoryView_FromMemory.argtypes = (c_char_p, c_ssize_t, c_int)
pythonapi.PyMemoryView_FromMemory.restype = py_object

_int_types = (c_int16, c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types


# From https://blag.nullteilerfrei.de/2021/06/20/prettier-struct-definitions-for-python-ctypes
# Please use it for all future struct definitions
class FieldsFromTypeHints(type(Structure)):
    def __new__(cls, name, bases, namespace):
        class AnnotationDummy:
            __annotations__ = namespace.get("__annotations__", {})

        annotations = get_type_hints(AnnotationDummy)
        namespace["_fields_"] = list(annotations.items())
        namespace["__slots__"] = list(annotations.keys())
        return type(Structure).__new__(cls, name, bases, namespace)


def as_bytes(value: str | bytes | None) -> bytes | None:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def is_zeroed(struct: Structure) -> bool:
    view = memoryview_at(addressof(struct), sizeof(struct), True)

    return not any(view)


def from_zero_terminated(ptr) -> Iterator:
    if ptr:
        i = 0
        while not is_zeroed(ptr[i]):
            yield ptr[i]
            i += 1


Pointer: TypeAlias = ctypes._Pointer


def deepcopy_array(array: Pointer, length: int, memo):
    if not array:
        return None

    arraytype: type[Array] = array._type_ * length
    return arraytype(*(deepcopy(array[i], memo) for i in range(length)))


def deepcopy_buffer(ptr: c_void_p | int, size: int) -> c_void_p | None:
    if ptr is not None and not isinstance(ptr, (c_void_p, int)):
        raise TypeError(f"Expected c_void_p or int, got {type(ptr).__name__}")

    if not ptr:
        return None

    if not size:
        return None

    arraytype: type[Array] = c_uint8 * size
    data = arraytype.from_buffer_copy(c_void_p(ptr))
    return cast(data, c_void_p)


@contextmanager
def mmap_file(path: str | PathLike, mode: str = "rb"):
    with open(path, mode, buffering=0) as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY) as m:
            view = memoryview(m)
            yield view
            view.release()
            # If we don't release the memoryview manually,
            # we'll get a BufferError when the context manager exits
        f.close()


def addressof_buffer(buffer: Buffer) -> int:
    if not isinstance(buffer, Buffer):
        raise TypeError(f"Expected Buffer, got {type(buffer).__name__}")
    array_type: type[Array] = c_ubyte * len(buffer)
    buffer_array = array_type.from_buffer(buffer)

    return ctypes.addressof(buffer_array)


def memoryview_at(
    address: c_char_p | c_void_p | int | bytes, size: c_ssize_t | int, readonly=False
) -> memoryview:
    flags = c_int(0x100 if readonly else 0x200)
    return pythonapi.PyMemoryView_FromMemory(cast(address, c_char_p), c_ssize_t(size), flags)


class c_uintptr(ctypes._SimpleCData):
    _type_ = "P"


c_double_p = POINTER(c_double)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return c_void_p


__all__ = [
    "FieldsFromTypeHints",
    "as_bytes",
    "is_zeroed",
    "from_zero_terminated",
    "Pointer",
    "deepcopy_array",
    "deepcopy_buffer",
    "mmap_file",
    "addressof_buffer",
    "memoryview_at",
    "c_ptrdiff_t",
    "c_uintptr",
    "c_double_p",
    "UNCHECKED",
]
