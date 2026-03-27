"""
This module defines type annotations for ``ctype``'s behavior
that's documented, but not reflected in its type stubs.

Most of these definitions fall back to standard ``ctypes`` types at runtime;
this allows them to be used as drop-in replacements for the standard types in function signatures.
"""

# pyright: reportPrivateUsage=false
# The types are private but the interfaces are documented, so this is a false positive.
# pyright: reportNoOverloadImplementation=false
# The overloads are only for type checking, so they don't need implementations.


from collections.abc import Buffer, Callable, Iterable
from ctypes import *  # pyright: ignore[reportWildcardImportFromLibrary]
from typing import (
    TYPE_CHECKING,
    Protocol,
    Self,
    SupportsBytes,
    SupportsFloat,
    SupportsInt,
    overload,
    override,
)

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


class c_void_ptr(c_void_p):
    """
    A trivial subclass of ``c_void_p`` that solely exists to
    prevent ``ctypes`` from implicitly converting
    ``void*`` parameters or struct fields to an ``int``.

    Use this in function signatures and struct definitions instead of ``c_void_p``.
    """

    pass


if TYPE_CHECKING:
    type ConvertibleToBool = ConvertibleToPrimitive[c_bool, bool]
    type ConvertibleToInteger[T: CUint | CInt] = ConvertibleToPrimitive[T, int] | SupportsInt
    type ConvertibleToFloat[T: CReal] = ConvertibleToPrimitive[T, float] | SupportsFloat
    type ConvertibleToString = ConvertibleToPrimitive[c_char_p, bytes] | SupportsBytes
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

    class TypedArray[T: _CDataType](Array[T]):
        @property
        @override
        def raw(self: TypedArray[c_char]) -> bytes: ...

        @raw.setter
        def raw(self: TypedArray[c_char], value: Buffer) -> None: ...

        @overload
        def __init__(self, *args: ConvertibleTo[T]) -> None: ...

        @overload
        def __init__[I: CInt | CUint](self: TypedArray[I], *args: ConvertibleTo[I]) -> None: ...

        @overload
        def __init__[F: CReal](self: TypedArray[F], *args: ConvertibleTo[F]) -> None: ...

        @overload
        def __init__[S: Structure](self: TypedArray[S], *args: ConvertibleTo[S]) -> None: ...

        @overload
        def __getitem__(self, key: int, /) -> T: ...

        @overload
        def __getitem__[I: CInt | CUint](self: TypedArray[I], key: int, /) -> int: ...

        @overload
        def __getitem__[F: CReal](self: TypedArray[F], key: int, /) -> float: ...

        @overload
        def __getitem__[S: Structure](self: TypedArray[S], key: int, /) -> S: ...

        @overload
        def __getitem__[
            P: _CDataType
        ](self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]], key: int, /) -> TypedArray[
            P
        ]: ...

        @overload
        def __getitem__(self, key: slice[T], /) -> list[T]: ...

        @overload
        def __getitem__[I: CInt | CUint](self: TypedArray[I], key: slice, /) -> list[int]: ...

        @overload
        def __getitem__[F: CReal](self: TypedArray[F], key: slice, /) -> list[float]: ...

        @overload
        def __getitem__[S: Structure](self: TypedArray[S], key: slice, /) -> list[S]: ...

        @overload
        def __getitem__[
            P: _CDataType
        ](self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]], key: slice, /) -> list[
            TypedArray[P]
        ]: ...

        @overload
        def __setitem__(self, key: int, value: ConvertibleTo[T], /) -> None: ...

        @overload
        def __setitem__[
            I: CInt | CUint
        ](self: TypedArray[I], key: int, value: ConvertibleTo[I], /) -> None: ...

        @overload
        def __setitem__[
            F: CReal
        ](self: TypedArray[F], key: int, value: ConvertibleTo[F], /) -> None: ...

        @overload
        def __setitem__[
            S: Structure
        ](self: TypedArray[S], key: int, value: ConvertibleTo[S], /) -> None: ...

        @overload
        def __setitem__[
            P: _CDataType
        ](
            self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]],
            key: int,
            value: ConvertibleTo[TypedArray[P]] | ConvertibleTo[_Pointer[P]],
            /,
        ) -> None: ...

        @overload
        def __setitem__(
            self, key: slice[ConvertibleTo[T]], value: Iterable[ConvertibleTo[T]], /
        ) -> None: ...

        @overload
        def __setitem__[
            I: CInt | CUint
        ](self: TypedArray[I], key: slice, value: Iterable[ConvertibleTo[I]], /) -> None: ...

        @overload
        def __setitem__[
            F: CReal
        ](self: TypedArray[F], key: slice, value: Iterable[ConvertibleTo[F]], /) -> None: ...

        @overload
        def __setitem__[
            S: Structure
        ](self: TypedArray[S], key: slice, value: Iterable[ConvertibleTo[S]], /) -> None: ...

        @overload
        def __setitem__[
            P: _CDataType
        ](
            self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]],
            key: slice,
            value: Iterable[ConvertibleTo[TypedArray[P]] | ConvertibleTo[_Pointer[P]]],
            /,
        ) -> None: ...

    class TypedPointer[T: _CDataType](_Pointer[T]):
        @overload
        def __getitem__(self: TypedPointer[c_bool], key: int, /) -> bool: ...

        @overload
        def __getitem__[I: CInt | CUint](self: TypedPointer[I], key: int, /) -> int: ...

        @overload
        def __getitem__[F: CReal](self: TypedPointer[F], key: int, /) -> float: ...

        @overload
        def __getitem__(self: TypedPointer[c_char_p], key: int, /) -> bytes: ...

        @overload
        def __getitem__[S: Structure](self: TypedPointer[S], key: int, /) -> S: ...

        @overload
        def __getitem__[
            P: _CDataType
        ](
            self: TypedPointer[TypedPointer[P]] | TypedPointer[_Pointer[P]], key: int, /
        ) -> TypedPointer[P]: ...

        @overload
        def __getitem__(self: TypedPointer[c_bool], key: slice, /) -> list[bool]: ...

        @overload
        def __getitem__[I: CInt | CUint](self: TypedPointer[I], key: slice, /) -> list[int]: ...

        @overload
        def __getitem__[F: CReal](self: TypedPointer[F], key: slice, /) -> list[float]: ...

        @overload
        def __getitem__(self: TypedPointer[c_char_p], key: slice, /) -> list[bytes]: ...

        @overload
        def __getitem__[S: Structure](self: TypedPointer[S], key: slice, /) -> list[S]: ...

        @overload
        def __getitem__[
            P: _CDataType
        ](self: TypedPointer[TypedPointer[P]] | TypedPointer[_Pointer[P]], key: slice, /) -> list[
            TypedPointer[P]
        ]: ...

        @overload
        def __setitem__(
            self: TypedPointer[c_bool], key: int, value: ConvertibleToBool, /
        ) -> None: ...

        @overload
        def __setitem__[
            I: CInt | CUint
        ](self: TypedPointer[I], key: int, value: ConvertibleToInteger[I], /) -> None: ...

        @overload
        def __setitem__[
            F: CReal
        ](self: TypedPointer[F], key: int, value: ConvertibleToFloat[F], /) -> None: ...

        @overload
        def __setitem__(
            self: TypedPointer[c_char_p], key: int, value: ConvertibleToString, /
        ) -> None: ...

        @overload
        def __setitem__[
            S: Structure
        ](self: TypedPointer[S], key: int, value: ConvertibleTo[S], /) -> None: ...

        @overload
        def __setitem__[
            P: _CDataType
        ](
            self: TypedPointer[TypedPointer[P]] | TypedPointer[_Pointer[P]],
            key: int,
            value: ConvertibleTo[TypedPointer[P]] | ConvertibleTo[_Pointer[P]],
            /,
        ) -> None: ...

        def __bool__(self) -> bool: ...

else:
    ConvertibleToBool = c_bool
    ConvertibleToInteger = _CTypeDeclaration
    ConvertibleToFloat = _CTypeDeclaration
    ConvertibleToString = c_char_p
    Pointer = _PointerDeclaration
    CoreFunctionPointer = _FunctionPointerDeclaration
    FrontendFunctionPointer = _FunctionPointerDeclaration
    TypedPointer = _PointerDeclaration
    TypedArray = Array

__all__ = (
    "ConvertibleTo",
    "ConvertibleToBool",
    "ConvertibleToFloat",
    "ConvertibleToInteger",
    "ConvertibleToString",
    "CoreFunctionPointer",
    "FrontendFunctionPointer",
    "Pointer",
    "TypedPointer",
    "TypedArray",
)
