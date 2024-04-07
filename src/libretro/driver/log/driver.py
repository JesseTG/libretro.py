from abc import abstractmethod
from typing import runtime_checkable, Protocol

from libretro.api.log import retro_log_callback, retro_log_printf_t, LogLevel


@runtime_checkable
class LogDriver(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_log_callback(retro_log_printf_t(self.log))

    @abstractmethod
    def log(self, message: LogLevel, fmt: bytes, *args) -> None: ...


__all__ = ['LogDriver']
