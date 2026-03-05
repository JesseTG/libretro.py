from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ctypes import _CDataType


@runtime_checkable
class AsParameter[T: _CDataType](Protocol):
    """
    Protocol for objects that can be used as parameters in C functions.

    :see: https://docs.python.org/3/library/ctypes.html#calling-functions-with-your-own-custom-data-types
    """

    @property
    @abstractmethod
    def _as_parameter_(self) -> T: ...


@runtime_checkable
class Pollable(Protocol):
    @abstractmethod
    def poll(self) -> None: ...


__all__ = ("AsParameter", "Pollable")
