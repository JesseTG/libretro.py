from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api import retro_message, retro_message_ext


@runtime_checkable
class MessageInterface(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def set_message(self, message: retro_message | retro_message_ext | None) -> bool: ...


__all__ = [
    "MessageInterface",
]
