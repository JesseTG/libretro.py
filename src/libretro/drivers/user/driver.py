from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.user import Language


@runtime_checkable
class UserDriver(Protocol):
    @property
    @abstractmethod
    def username(self) -> bytes | None: ...

    @property
    @abstractmethod
    def language(self) -> Language | None: ...


__all__ = ["UserDriver"]
