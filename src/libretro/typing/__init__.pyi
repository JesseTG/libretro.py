from ctypes import *
from typing import Any, Protocol

from _ctypes import CFuncPtr, _CDataType, _Pointer

CInt = (
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
CUint = (
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
c_bool_arg = c_bool | bool | Any
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

class CoreFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
    """
    Type for a function defined in the core to be called in the frontend
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

class FrontendFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
    """
    Type for a function defined in the frontend to be called in the core
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

class AsParameter[T: _CDataType](Protocol):
    _as_parameter_: T

__all__ = (
    "c_int_arg",
    "CBufferArg",
    "c_int16_arg",
    "c_int64_arg",
    "c_size_t_arg",
    "c_bool_arg",
    "c_uint_arg",
    "Pointer",
    "TypedCFuncPtr",
    "c_uint8_arg",
    "c_uint32_arg",
    "c_uint64_arg",
)
