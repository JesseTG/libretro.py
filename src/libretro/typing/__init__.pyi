from collections.abc import Callable, Iterable, Iterator
from ctypes import *
from typing import Any, Literal, Protocol, Self, overload, override

from _ctypes import CFuncPtr, _CDataType, _Pointer, _SimpleCData

type CInt = (
    c_int
    | c_byte
    | c_short
    | c_long
    | c_longlong
    | c_int8
    | c_int16
    | c_int32
    | c_int64
    | c_ssize_t
)
type CUint = (
    c_uint
    | c_ubyte
    | c_ushort
    | c_ulong
    | c_ulonglong
    | c_uint8
    | c_uint16
    | c_uint32
    | c_uint64
    | c_size_t
)
CReal = c_float | c_double | c_longdouble
CNumber = CInt | CUint | CReal
to_c_bool = c_bool | bool | Any
"""
Type for a boolean argument to a function intended to be called from the frontend.
"""

to_c_int16 = c_int16 | int
to_c_int64 = c_int64 | int
to_c_uint = c_uint | int
from_c_bool = bool
from_c_size_t = int
c_int_arg = c_int | int
c_int16_arg = c_int16 | int
c_int64_arg = c_int64 | int
c_size_t_arg = c_size_t | int
c_uint_arg = c_uint | int
c_uint8_arg = c_uint8 | int
c_uint32_arg = c_uint32 | int
c_uint64_arg = c_uint64 | int
c_str_arg = c_char_p | bytes
type CIntArg[I: CInt | CUint] = I | int
type CSignedIntArg[I: CInt] = I | int
type CUnsignedIntArg[I: CUint] = I | int
type CRealArg[R: CReal] = R | float
type CBoolArg = bool | c_bool | Any
type CBufferArg[T: _CDataType] = _Pointer[T] | memoryview | bytes
type CPointerArg[T: _CDataType] = _Pointer[T] | None
type CNullableBufferArg[T: _CDataType] = CBufferArg[T] | None
type Pointer[T: _CDataType] = _Pointer[T]

type PointerArg[T: _CDataType] = Pointer[T] | T | None
"""
Type for a pointer argument in a function intended to be called from the frontend.
Can be a pointer, a value of the pointed type, or None (which is converted to NULL).
"""

class CoreFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
    """
    Type for a function defined in the core to be called in the frontend
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

class FrontendFunctionPointer[R: _CDataType | None | int, **P](CFuncPtr):
    """
    Type for a function defined in the frontend to be called in the core
    """

    @overload
    def __call__(self, func: Callable[P, R]) -> Self: ...
    @overload
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

class AsParameter[T: _CDataType](Protocol):
    """
    A type that can be converted to a ctypes object
    with the _as_parameter_ property.
    """

    @property
    def _as_parameter_(self) -> T: ...

type ConvertibleTo[T: _CDataType] = T | AsParameter[T]
type ConvertibleToPrimitive[T: _CDataType, U: (int, float, bytes, bool)] = ConvertibleTo[
    T
] | U | _SimpleCData[U]
type ConvertibleToBool = bool | ConvertibleTo[c_bool]
type ConvertibleToInteger[T: (CUint, CInt)] = int | ConvertibleTo[T]
type ConvertibleToString = bytes | ConvertibleTo[c_char_p]

class StructureArray[T: Structure](Array[T]):
    @override
    def __init__(self, *args: ConvertibleTo[T]) -> None: ...
    @override
    @overload
    def __getitem__(self, key: int, /) -> T: ...
    @overload
    def __getitem__(self, key: slice[T], /) -> list[T]: ...
    @override
    @overload
    def __setitem__(self, key: int, value: ConvertibleTo[T], /) -> None: ...
    @overload
    def __setitem__(
        self, key: slice[ConvertibleTo[T]], value: Iterable[ConvertibleTo[T]], /
    ) -> None: ...
    @override
    def __iter__(self) -> Iterator[T]: ...

class StructurePointer[T: Structure](_Pointer[T]):
    @override
    @overload
    def __getitem__(self, key: int, /) -> T: ...
    @overload
    def __getitem__(self, key: slice[T], /) -> list[T]: ...
    @override
    def __setitem__(self, key: int, value: ConvertibleTo[T], /) -> None: ...
