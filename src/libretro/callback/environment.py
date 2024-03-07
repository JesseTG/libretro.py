from abc import abstractmethod
from ctypes import c_void_p
from typing import Protocol

from ..defs import EnvironmentCall


class EnvironmentCallback(Protocol):
    @abstractmethod
    def environment(self, cmd: EnvironmentCall, data: c_void_p) -> bool: ...
