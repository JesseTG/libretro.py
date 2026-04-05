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

from __future__ import annotations

from collections.abc import Buffer, Callable, Iterable, Iterator
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
        # CFUNCTYPE doesn't support returning pointers to structs,
        # so function pointers will have to return c_void_p instead
        # and be cast back to the correct type in the implementation.
        # https://github.com/python/cpython/issues/49960
        restype = args[0]
        if restype and issubclass(restype, _Pointer) and issubclass(restype._type_, (Structure, CFuncPtr)):  # type: ignore
            return CFUNCTYPE(c_void_ptr, *args[1])
        else:
            return CFUNCTYPE(restype, *args[1])


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

    @override
    def __repr__(self) -> str:
        return f"c_void_ptr({self.value:#x})"


if TYPE_CHECKING:
    type CBoolArg = ConvertibleToPrimitive[c_bool, bool]
    type CIntArg[T: CUint | CInt] = ConvertibleToPrimitive[T, int] | SupportsInt
    type CFloatArg[T: CReal] = ConvertibleToPrimitive[T, float] | SupportsFloat
    type CStringArg = ConvertibleToPrimitive[c_char_p, bytes] | SupportsBytes
    type Pointer[T: _CDataType] = _Pointer[T]

    class TypedFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
        @overload
        def __call__(self, func: Callable[P, R]) -> Self: ...
        @overload
        def __call__(
            self: TypedFunctionPointer[c_bool, P], *args: P.args, **kwargs: P.kwargs
        ) -> bool: ...
        @overload
        def __call__[
            I: CInt | CUint
        ](self: TypedFunctionPointer[I, P], *args: P.args, **kwargs: P.kwargs) -> int: ...
        @overload
        def __call__[
            F: CReal
        ](self: TypedFunctionPointer[F, P], *args: P.args, **kwargs: P.kwargs) -> float: ...
        @overload
        def __call__[
            S: Structure
        ](
            self: TypedFunctionPointer[TypedPointer[S] | Pointer[S], P],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> (c_void_ptr | None): ...
        @overload
        def __call__(
            self: TypedFunctionPointer[None, []], *args: P.args, **kwargs: P.kwargs
        ) -> TypedFunctionPointer[None, []] | None: ...
        @overload
        def __call__[
            T: _CDataType, **Q
        ](
            self: TypedFunctionPointer[TypedFunctionPointer[T, Q], P],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> (c_void_ptr | None): ...

        # See https://github.com/python/cpython/issues/49960
        @overload
        def __call__(
            self: TypedFunctionPointer[c_char_p, P], *args: P.args, **kwargs: P.kwargs
        ) -> bytes | None: ...

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

        @overload
        def __iter__[I: CInt | CUint](self: TypedArray[I]) -> Iterator[int]: ...

        @overload
        def __iter__[F: CReal](self: TypedArray[F]) -> Iterator[float]: ...

        @overload
        def __iter__[S: Structure](self: TypedArray[S]) -> Iterator[S]: ...

        @overload
        def __iter__(self: TypedArray[T]) -> Iterator[T]: ...

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
        def __setitem__(self: TypedPointer[c_bool], key: int, value: CBoolArg, /) -> None: ...

        @overload
        def __setitem__[
            I: CInt | CUint
        ](self: TypedPointer[I], key: int, value: CIntArg[I], /) -> None: ...

        @overload
        def __setitem__[
            F: CReal
        ](self: TypedPointer[F], key: int, value: CFloatArg[F], /) -> None: ...

        @overload
        def __setitem__(self: TypedPointer[c_char_p], key: int, value: CStringArg, /) -> None: ...

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
    CBoolArg = c_bool
    CIntArg = _CTypeDeclaration
    CFloatArg = _CTypeDeclaration
    CStringArg = c_char_p
    Pointer = _PointerDeclaration
    TypedFunctionPointer = _FunctionPointerDeclaration
    TypedPointer = _PointerDeclaration
    TypedArray = Array

__all__ = (
    "ConvertibleTo",
    "CBoolArg",
    "CFloatArg",
    "CIntArg",
    "CStringArg",
    "TypedFunctionPointer",
    "Pointer",
    "TypedPointer",
    "TypedArray",
)
