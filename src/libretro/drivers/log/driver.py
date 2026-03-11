from abc import abstractmethod
from typing import Protocol, runtime_checkable
from warnings import deprecated

from libretro.api.log import LogLevel, retro_log_callback, retro_log_printf_t


@runtime_checkable
class LogDriver(Protocol):

    @property
    @deprecated("Set the function pointer in the EnvironmentDriver instead of in the LogDriver")
    def _as_parameter_(self) -> retro_log_callback:
        return retro_log_callback(retro_log_printf_t(self.log))

    @abstractmethod
    def log(self, level: LogLevel, fmt: bytes) -> None: ...


__all__ = ["LogDriver"]
