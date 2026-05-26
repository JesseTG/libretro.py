"""
Type annotations for :mod:`ctypes` behavior that is documented but missing from its type stubs.

Most of these definitions fall back to standard :mod:`ctypes` types at runtime;
this allows them to be used as drop-in replacements for the standard types in function signatures.

The subscripted helpers — :class:`TypedPointer`, :class:`TypedArray`,
:class:`TypedFunctionPointer`, :class:`Pointer` — are TYPE_CHECKING-only
refinements that erase to plain :mod:`ctypes` factories at runtime;
their docstrings therefore live on this module so they remain discoverable
through ``python -m pytest --doctest-modules src/libretro``.

Indexing a pointer to a primitive integer type yields a Python :class:`int`,
exactly as :func:`ctypes.POINTER` does — the subscript on
:class:`TypedPointer` resolves to the cached :func:`ctypes.POINTER` factory
so the two are interchangeable at runtime:

>>> from ctypes import POINTER, c_int, cast
>>> from libretro.ctypes import TypedPointer
>>> arr = (c_int * 3)(10, 20, 30)
>>> p = cast(arr, TypedPointer[c_int])
>>> p[0], p[2]
(10, 30)
>>> p[0] = 99
>>> arr[0]
99

Pointers to :class:`~ctypes.Structure` types return the struct directly on
indexing, with no implicit conversion to an address:

>>> from ctypes import Structure
>>> class Pt(Structure):
...     _fields_ = (("x", c_int), ("y", c_int))
>>> pts = (Pt * 2)(Pt(7, 8), Pt(13, 21))
>>> pp = cast(pts, TypedPointer[Pt])
>>> pp[1].x, pp[1].y
(13, 21)

The runtime :class:`Pointer` alias is the same factory as
:func:`ctypes.POINTER`, which caches per-element-type:

>>> from libretro.ctypes import Pointer
>>> Pointer[c_int] is POINTER(c_int)
True

:class:`TypedArray` is :class:`ctypes.Array` at runtime, so the standard
``ctype * N`` construction is the way to instantiate one. Iteration and
slicing then yield Python primitives, matching the conversions
:mod:`ctypes` documents:

>>> from ctypes import Array
>>> from libretro.ctypes import TypedArray
>>> TypedArray is Array
True
>>> a = (c_int * 4)(1, 2, 3, 4)
>>> isinstance(a, TypedArray)
True
>>> list(a)
[1, 2, 3, 4]
>>> a[1:3]
[2, 3]

A :class:`TypedFunctionPointer` is decorated as if :func:`ctypes.CFUNCTYPE`
had been used directly: arguments and return values flow through the same
implicit :mod:`ctypes` conversions, so an integer return becomes a Python
:class:`int`, a boolean return becomes a Python :class:`bool`, and a
``char *`` return becomes :class:`bytes`:

>>> from ctypes import c_bool, c_char_p
>>> from libretro.ctypes import TypedFunctionPointer
>>> as_bool = TypedFunctionPointer[c_bool, [c_int]](lambda x: x != 0)
>>> as_bool(0), as_bool(42)
(False, True)
>>> add = TypedFunctionPointer[c_int, [c_int, c_int]](lambda a, b: a + b)
>>> add(2, 3)
5
>>> echo = TypedFunctionPointer[c_char_p, [c_char_p]](lambda s: s)
>>> echo(b"hello")
b'hello'

A :class:`TypedFunctionPointer` declared with a :obj:`None` return type
produces a callable that returns :obj:`None`:

>>> noop = TypedFunctionPointer[None, []](lambda: None)
>>> noop() is None
True
"""

# pyright: reportPrivateUsage=false
# The types are private but the interfaces are documented, so this is a false positive.
# pyright: reportNoOverloadImplementation=false
# The overloads are only for type checking, so they don't need implementations.

from __future__ import annotations

from collections.abc import Buffer, Callable, Iterable, Iterator
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Array,
    Structure,
    c_bool,
    c_byte,
    c_char,
    c_char_p,
    c_double,
    c_float,
    c_int,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_long,
    c_longdouble,
    c_longlong,
    c_short,
    c_size_t,
    c_ssize_t,
    c_ubyte,
    c_uint,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_ulong,
    c_ulonglong,
    c_ushort,
    c_void_p,
)
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
    with the ``_as_parameter_`` property.

    Any object that implements this protocol may be passed where
    :mod:`ctypes` expects a primitive C type;
    the marshalling layer consults ``_as_parameter_`` to obtain the
    underlying :mod:`ctypes` value:

    >>> from ctypes import CFUNCTYPE, c_int
    >>> class Boxed:
    ...     def __init__(self, value):
    ...         self._as_parameter_ = c_int(value)
    >>> echo = CFUNCTYPE(c_int, c_int)(lambda x: x)
    >>> echo(Boxed(42))
    42
    """

    @property
    def _as_parameter_(self) -> T: ...


type ConvertibleTo[T: _CDataType] = T | AsParameter[T]
type ConvertibleToPrimitive[T: _CDataType, U: (int, float, bytes, bool)] = (
    ConvertibleTo[T] | U | _SimpleCData[U]
)


class _FunctionPointerDeclaration:
    @classmethod
    def __class_getitem__(cls, args: tuple[type[_CDataType] | None, list[type[_CDataType]]]):
        """Allow subscripted CoreFunctionPointer types to be used as type annotations."""
        # CFUNCTYPE doesn't support returning pointers to structs,
        # so function pointers will have to return c_void_p instead
        # and be cast back to the correct type in the implementation.
        # https://github.com/python/cpython/issues/49960
        restype = args[0]
        if (
            restype
            and issubclass(restype, _Pointer)
            and issubclass(restype._type_, (Structure, CFuncPtr))  # type: ignore
        ):
            return CFUNCTYPE(c_void_ptr, *args[1])
        else:
            return CFUNCTYPE(restype, *args[1])


class _PointerDeclaration:
    @classmethod
    def __class_getitem__(cls, arg: type[_CDataType]):
        """Allow subscripted Pointer types to be used as type annotations."""
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
    Instances remain :class:`~ctypes.c_void_p` subclasses, with their address
    rendered in hexadecimal:

    >>> from ctypes import c_void_p
    >>> from libretro.ctypes import c_void_ptr
    >>> ptr = c_void_ptr(0x1234)
    >>> repr(ptr)
    'c_void_ptr(0x1234)'
    >>> isinstance(ptr, c_void_p)
    True
    >>> ptr.value
    4660
    """

    @override
    def __repr__(self) -> str:
        return f"c_void_ptr({self.value:#x})"


if TYPE_CHECKING:
    type CBoolArg = ConvertibleToPrimitive[c_bool, bool]
    """A type that can be used as an argument for a C :c:type:`c_bool` parameter."""

    type CIntArg[T: CUint | CInt] = ConvertibleToPrimitive[T, int] | SupportsInt
    """A type that can be used as an argument for a C integer parameter."""

    type CFloatArg[T: CReal] = ConvertibleToPrimitive[T, float] | SupportsFloat
    """A type that can be used as an argument for a C floating-point parameter."""

    type CStringArg = ConvertibleToPrimitive[c_char_p, bytes] | SupportsBytes
    """A type that can be used as an argument for a C ``char *`` parameter."""

    type Pointer[T: _CDataType] = _Pointer[T]

    class TypedFunctionPointer[R: _CDataType | None, **P](CFuncPtr):
        """
        Typing-only refinement of :func:`ctypes.CFUNCTYPE` parameterized by return and parameter types.

        Defined inside a :attr:`typing.TYPE_CHECKING` block;
        at runtime this name resolves to a plain
        :func:`ctypes.CFUNCTYPE` factory (see the :keyword:`else` branch below).
        Exists so static analyzers can infer concrete return types
        (:class:`bool`, :class:`int``, :class:`float`, :class:`bytes`, etc.)
        from the ctypes return-type parameter ``R``.
        """

        @overload
        def __call__(self, func: Callable[P, R]) -> Self: ...
        @overload
        def __call__(
            self: TypedFunctionPointer[c_bool, P], *args: P.args, **kwargs: P.kwargs
        ) -> bool: ...
        @overload
        def __call__[I: CInt | CUint](
            self: TypedFunctionPointer[I, P], *args: P.args, **kwargs: P.kwargs
        ) -> int: ...
        @overload
        def __call__[F: CReal](
            self: TypedFunctionPointer[F, P], *args: P.args, **kwargs: P.kwargs
        ) -> float: ...
        @overload
        def __call__[S: Structure](
            self: TypedFunctionPointer[TypedPointer[S] | Pointer[S], P],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> c_void_ptr | None: ...
        @overload
        def __call__(
            self: TypedFunctionPointer[None, []], *args: P.args, **kwargs: P.kwargs
        ) -> TypedFunctionPointer[None, []] | None: ...
        @overload
        def __call__[T: _CDataType, **Q](
            self: TypedFunctionPointer[TypedFunctionPointer[T, Q], P],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> c_void_ptr | None: ...

        # See https://github.com/python/cpython/issues/49960
        @overload
        def __call__(
            self: TypedFunctionPointer[c_char_p, P], *args: P.args, **kwargs: P.kwargs
        ) -> bytes | None: ...

        @overload
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    class TypedArray[T: _CDataType](Array[T]):
        """
        Typing-only refinement of :class:`ctypes.Array` parameterized by element type.

        Defined inside ``if TYPE_CHECKING:``;
        at runtime this name resolves to plain :class:`ctypes.Array`
        (see the :keyword:`else` branch below).
        Exists so static analyzers can refine the element type
        returned by indexing and iteration based on the :mod:`ctypes` element type ``T``.
        """

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
        def __getitem__[P: _CDataType](
            self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]], key: int, /
        ) -> TypedArray[P]: ...

        @overload
        def __getitem__(self, key: slice[T], /) -> list[T]: ...

        @overload
        def __getitem__[I: CInt | CUint](self: TypedArray[I], key: slice, /) -> list[int]: ...

        @overload
        def __getitem__[F: CReal](self: TypedArray[F], key: slice, /) -> list[float]: ...

        @overload
        def __getitem__[S: Structure](self: TypedArray[S], key: slice, /) -> list[S]: ...

        @overload
        def __getitem__[P: _CDataType](  # pyright: ignore[reportIncompatibleMethodOverride]
            self: TypedArray[TypedArray[P]] | TypedArray[_Pointer[P]], key: slice, /
        ) -> list[TypedArray[P]]: ...

        # pyright triggers reportIncompatibleMethodOverride here because
        # it claims that not all overloads of the base type are covered;
        # not sure if it's a false positive or if the overloads are actually incompatible.
        # The error occurred in 1.1.409, but not 1.1.408; no idea why.
        # Same goes for __setitem__ below.

        @override
        @overload
        def __setitem__(self, key: int, value: ConvertibleTo[T], /) -> None: ...

        @overload
        def __setitem__[I: CInt | CUint](
            self: TypedArray[I], key: int, value: ConvertibleTo[I], /
        ) -> None: ...

        @overload
        def __setitem__[F: CReal](
            self: TypedArray[F], key: int, value: ConvertibleTo[F], /
        ) -> None: ...

        @overload
        def __setitem__[S: Structure](
            self: TypedArray[S], key: int, value: ConvertibleTo[S], /
        ) -> None: ...

        @overload
        def __setitem__[P: _CDataType](
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
        def __setitem__[I: CInt | CUint](
            self: TypedArray[I], key: slice, value: Iterable[ConvertibleTo[I]], /
        ) -> None: ...

        @overload
        def __setitem__[F: CReal](
            self: TypedArray[F], key: slice, value: Iterable[ConvertibleTo[F]], /
        ) -> None: ...

        @overload
        def __setitem__[S: Structure](
            self: TypedArray[S], key: slice, value: Iterable[ConvertibleTo[S]], /
        ) -> None: ...

        @overload
        def __setitem__[P: _CDataType](  # pyright: ignore[reportIncompatibleMethodOverride]
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
        """
        Typing-only refinement of :class:`ctypes.POINTER` parameterized by referent type.

        Defined inside ``if TYPE_CHECKING:``;
        at runtime this name resolves to a plain
        :func:`ctypes.POINTER` factory (see the :keyword:`else` branch below).
        Exists so static analyzers can refine the value type
        returned by indexing based on the :mod:`ctypes` referent type ``T``.
        """

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
        def __getitem__[P: _CDataType](
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
        def __getitem__[P: _CDataType](
            self: TypedPointer[TypedPointer[P]] | TypedPointer[_Pointer[P]], key: slice, /
        ) -> list[TypedPointer[P]]: ...

        @overload
        def __setitem__(self: TypedPointer[c_bool], key: int, value: CBoolArg, /) -> None: ...

        @overload
        def __setitem__[I: CInt | CUint](
            self: TypedPointer[I], key: int, value: CIntArg[I], /
        ) -> None: ...

        @overload
        def __setitem__[F: CReal](
            self: TypedPointer[F], key: int, value: CFloatArg[F], /
        ) -> None: ...

        @overload
        def __setitem__(self: TypedPointer[c_char_p], key: int, value: CStringArg, /) -> None: ...

        @overload
        def __setitem__[S: Structure](
            self: TypedPointer[S], key: int, value: ConvertibleTo[S], /
        ) -> None: ...

        @overload
        def __setitem__[P: _CDataType](
            self: TypedPointer[TypedPointer[P]] | TypedPointer[_Pointer[P]],
            key: int,
            value: ConvertibleTo[TypedPointer[P]] | ConvertibleTo[_Pointer[P]],
            /,
        ) -> None: ...

        def __bool__(self) -> bool:
            """Return :obj:`True` if this pointer is non-null."""
            ...

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
    "AsParameter",
    "ConvertibleTo",
    "CBoolArg",
    "CFloatArg",
    "CIntArg",
    "CStringArg",
    "TypedFunctionPointer",
    "Pointer",
    "TypedPointer",
    "TypedArray",
    "c_void_ptr",
)
