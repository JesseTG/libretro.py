from abc import abstractmethod
from ctypes import c_void_p
from typing import Protocol, runtime_checkable


@runtime_checkable
class EnvironmentDriver(Protocol):
    @abstractmethod
    def environment(self, cmd: int, data: c_void_p) -> bool: ...


__all__ = [
    'EnvironmentDriver',
]
