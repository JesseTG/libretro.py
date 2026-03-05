from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class Pollable(Protocol):
    @abstractmethod
    def poll(self) -> None: ...


__all__ = ("Pollable",)
