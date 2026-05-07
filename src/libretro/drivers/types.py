"""Shared protocol types used by multiple driver families."""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class Pollable(Protocol):
    """A type that can be polled for an update once per frame."""

    @abstractmethod
    def poll(self) -> None:
        """Poll the driver for an update."""
        ...


__all__ = ("Pollable",)
