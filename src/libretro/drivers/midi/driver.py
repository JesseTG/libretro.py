from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class MidiDriver(Protocol):
    @property
    @abstractmethod
    def input_enabled(self) -> bool: ...

    @property
    @abstractmethod
    def output_enabled(self) -> bool: ...

    @abstractmethod
    def read(self) -> int | None: ...

    @abstractmethod
    def write(self, byte: int, delta_time: int) -> bool: ...

    @abstractmethod
    def flush(self) -> bool: ...


__all__ = ["MidiDriver"]
