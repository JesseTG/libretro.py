from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from warnings import deprecated

from libretro.api.perf import (
    CpuFeatures,
    retro_get_cpu_features_t,
    retro_perf_callback,
    retro_perf_counter,
    retro_perf_get_counter_t,
    retro_perf_get_time_usec_t,
    retro_perf_log_t,
    retro_perf_register_t,
    retro_perf_start_t,
    retro_perf_stop_t,
)

if TYPE_CHECKING:
    from libretro.typing import StructurePointer


@runtime_checkable
class PerfDriver(Protocol):
    @property
    @deprecated("Set the function pointers in the EnvironmentDriver instead of the PerfDriver")
    def _as_parameter_(self) -> retro_perf_callback:
        return retro_perf_callback(
            get_time_usec=retro_perf_get_time_usec_t(self.get_time_usec),
            get_cpu_features=retro_get_cpu_features_t(self.get_cpu_features),
            get_perf_counter=retro_perf_get_counter_t(self.get_perf_counter),
            perf_register=retro_perf_register_t(self.__perf_register),
            perf_start=retro_perf_start_t(self.__perf_start),
            perf_stop=retro_perf_stop_t(self.__perf_stop),
            perf_log=retro_perf_log_t(self.perf_log),
        )

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

    def __perf_register(self, counter: StructurePointer[retro_perf_counter]) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        perf_counter = counter[0]
        try:
            self.perf_register(perf_counter)
        except:
            perf_counter.registered = False
            raise

    def __perf_start(self, counter: StructurePointer[retro_perf_counter]) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        self.perf_start(counter[0])

    def __perf_stop(self, counter: StructurePointer[retro_perf_counter]) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        self.perf_stop(counter[0])


__all__ = ["PerfDriver"]
