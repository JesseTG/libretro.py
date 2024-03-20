from abc import abstractmethod
from typing import runtime_checkable, Protocol

from .defs import *


@runtime_checkable
class LogCallback(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_log_callback(retro_log_printf_t(self.log))

    @abstractmethod
    def log(self, message: int, fmt: bytes, *args) -> None: ...
