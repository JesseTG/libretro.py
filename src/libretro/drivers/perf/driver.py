from abc import abstractmethod
from ctypes import POINTER
from typing import Protocol, runtime_checkable

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


@runtime_checkable
class PerfDriver(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_perf_callback()
        self._as_parameter_.get_time_usec = retro_perf_get_time_usec_t(self.get_time_usec)
        self._as_parameter_.get_cpu_features = retro_get_cpu_features_t(self.get_cpu_features)
        self._as_parameter_.get_perf_counter = retro_perf_get_counter_t(self.get_perf_counter)
        self._as_parameter_.perf_register = retro_perf_register_t(self.__perf_register)
        self._as_parameter_.perf_start = retro_perf_start_t(self.__perf_start)
        self._as_parameter_.perf_stop = retro_perf_stop_t(self.__perf_stop)
        self._as_parameter_.perf_log = retro_perf_log_t(self.perf_log)

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

    def __perf_register(self, counter: POINTER(retro_perf_counter)) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        perf_counter = counter[0]
        try:
            self.perf_register(perf_counter)
        except:
            perf_counter.registered = False
            raise

    def __perf_start(self, counter: POINTER(retro_perf_counter)) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        self.perf_start(counter[0])

    def __perf_stop(self, counter: POINTER(retro_perf_counter)) -> None:
        if not counter:
            raise ValueError("counter must not be NULL")

        self.perf_stop(counter[0])


__all__ = ["PerfDriver"]
