from abc import abstractmethod
from typing import Protocol, runtime_checkable

from .defs import Language


@runtime_checkable
class UserDriver(Protocol):
    @property
    @abstractmethod
    def username(self) -> bytes | None: ...

    @property
    @abstractmethod
    def language(self) -> Language | None: ...


__all__ = [
    'UserDriver'
]
