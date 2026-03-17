from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.perf import CpuFeatures, retro_perf_counter


@runtime_checkable
class PerfDriver(Protocol):
    @abstractmethod
    def get_time_usec(self) -> int: ...

    @abstractmethod
    def get_cpu_features(self) -> CpuFeatures: ...

    @abstractmethod
    def get_perf_counter(self) -> int: ...

    @abstractmethod
    def perf_register(self, counter: retro_perf_counter) -> None: ...

    @abstractmethod
    def perf_start(self, counter: retro_perf_counter) -> None: ...

    @abstractmethod
    def perf_stop(self, counter: retro_perf_counter) -> None: ...

    @abstractmethod
    def perf_log(self) -> None: ...


__all__ = ["PerfDriver"]
