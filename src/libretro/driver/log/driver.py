from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.log import LogLevel, retro_log_callback, retro_log_printf_t


@runtime_checkable
class LogDriver(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_log_callback(retro_log_printf_t(self.log))

    @abstractmethod
    def log(self, message: LogLevel, fmt: bytes, *args) -> None: ...


__all__ = ["LogDriver"]
