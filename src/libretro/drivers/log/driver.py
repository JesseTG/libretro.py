from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.log import LogLevel


@runtime_checkable
class LogDriver(Protocol):

    @abstractmethod
    def log(self, level: LogLevel, fmt: bytes) -> None: ...


__all__ = ["LogDriver"]
