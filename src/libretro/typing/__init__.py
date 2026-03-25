from collections.abc import Callable, Iterable, Iterator
from ctypes import *  # pyright: ignore[reportWildcardImportFromLibrary]
from typing import TYPE_CHECKING, Protocol, Self, overload, override

if TYPE_CHECKING:
    from _ctypes import _CDataType

from _ctypes import CFuncPtr, _Pointer, _SimpleCData

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


class _FunctionPointerDeclaration:
    @classmethod
    def __class_getitem__(cls, args: tuple[type[_CDataType] | None, list[type[_CDataType]]]):
        """
        Allow subscripted CoreFunctionPointer types to be used as type annotations.
        """
        return CFUNCTYPE(args[0], *args[1])


class _PointerDeclaration:
    @classmethod
    def __class_getitem__(cls, arg: type[_CDataType]):
        """
        Allow subscripted Pointer types to be used as type annotations.
        """
        return POINTER(arg)


class _CTypeDeclaration:
    @classmethod
    def __class_getitem__(cls, ctype: type[_CDataType]):
        return ctype


if TYPE_CHECKING:
    type ConvertibleToBool = ConvertibleToPrimitive[c_bool, bool]
    type ConvertibleToInteger[T: (CUint, CInt)] = ConvertibleToPrimitive[T, int]
    type ConvertibleToFloat[T: CReal] = ConvertibleToPrimitive[T, float]
    type ConvertibleToString = ConvertibleToPrimitive[c_char_p, bytes]
    type Pointer[T: _CDataType] = _Pointer[T]

    class CoreFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
        """
        Type for a function defined in the core to be called in the frontend
        """

        @overload
        def __call__(self, func: Callable[P, R]) -> Self: ...
        @overload
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    class FrontendFunctionPointer[R: _CDataType | None | int, **P](CFuncPtr):
        """
        Type for a function defined in the frontend to be called in the core
        """

        @overload
        def __call__(self, func: Callable[P, R]) -> Self: ...
        @overload
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

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
        def __bool__(self) -> bool: ...

    class IntPointer[T: CInt | CUint](_Pointer[_SimpleCData[int]]):
        @override
        @overload
        def __getitem__(self, key: int, /) -> int: ...
        @overload
        def __getitem__(self, key: slice, /) -> list[int]: ...
        @override
        def __setitem__(self, key: int, value: ConvertibleToInteger[T], /) -> None: ...
        def __bool__(self) -> bool: ...

    class FloatPointer[T: CReal](_Pointer[_SimpleCData[float]]):
        @override
        @overload
        def __getitem__(self, key: int, /) -> float: ...
        @overload
        def __getitem__(self, key: slice, /) -> list[float]: ...
        @override
        def __setitem__(self, key: int, value: ConvertibleToFloat[T], /) -> None: ...
        def __bool__(self) -> bool: ...

    class BoolPointer(_Pointer[c_bool]):
        @override
        @overload
        def __getitem__(self, key: int, /) -> bool: ...
        @overload
        def __getitem__(self, key: slice, /) -> list[bool]: ...
        @override
        def __setitem__(self, key: int, value: ConvertibleToBool, /) -> None: ...
        def __bool__(self) -> bool: ...

    class StringPointer(_Pointer[c_char_p]):
        @override
        @overload
        def __getitem__(self, key: int, /) -> bytes: ...
        @overload
        def __getitem__(self, key: slice, /) -> list[bytes]: ...
        @override
        def __setitem__(self, key: int, value: ConvertibleToString, /) -> None: ...
        def __bool__(self) -> bool: ...

else:
    ConvertibleToBool = c_bool
    ConvertibleToInteger = _CTypeDeclaration
    ConvertibleToFloat = _CTypeDeclaration
    ConvertibleToString = c_char_p
    Pointer = _PointerDeclaration
    CoreFunctionPointer = _FunctionPointerDeclaration
    FrontendFunctionPointer = _FunctionPointerDeclaration
    StructureArray = Array
    StructurePointer = _PointerDeclaration
    IntPointer = _PointerDeclaration
    FloatPointer = _PointerDeclaration
    BoolPointer = _PointerDeclaration
    StringPointer = _PointerDeclaration
