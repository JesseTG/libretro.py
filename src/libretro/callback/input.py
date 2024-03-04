from abc import abstractmethod
from collections.abc import Iterator, Callable
from ctypes import c_int16, c_uint
from typing import Protocol, NamedTuple, runtime_checkable, final
from collections import namedtuple

@runtime_checkable
class InputCallbacks(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: c_uint, device: c_uint, index: c_uint, id: c_uint) -> c_int16: ...


class DeviceParams(NamedTuple):
    port: int
    device: int
    index: int
    id: int


@final
class InputState(InputCallbacks):
    def __init__(self, generator: Callable[[int, int, int, int], Iterator[int]]):
        self._generator = generator
        self._generators: dict[DeviceParams, Iterator[int]] = {}