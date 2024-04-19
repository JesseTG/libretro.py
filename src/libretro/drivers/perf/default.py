from collections.abc import Mapping
from time import process_time_ns, time_ns

from libretro.api.perf import CpuFeatures, retro_perf_counter

from .driver import PerfDriver


class DefaultPerfDriver(PerfDriver):
    def __init__(self):
        super().__init__()
        self._perf_counters: dict[bytes, retro_perf_counter] = {}

    def __del__(self):
        self._perf_counters.clear()
        # This dict contains references to core-owned data;
        # we clear the references here just in case
        # someone else managed to take ownership of the dict.

    @property
    def perf_counters(self) -> Mapping[bytes, retro_perf_counter]:
        return self._perf_counters

    def get_time_usec(self) -> int:
        return time_ns() // 1000

    def get_perf_counter(self) -> int:
        return process_time_ns()

    def get_cpu_features(self) -> CpuFeatures:
        # TODO: Use Cython to wrap libretro-common's get_cpu_features
        raise NotImplementedError("get_cpu_features is not implemented")

    def perf_register(self, counter: retro_perf_counter) -> None:
        if not counter.ident:
            raise ValueError("counter.ident must not be NULL")

        if counter.start:
            raise ValueError(
                f"Expected counter.start to be zero upon registration, got {counter.start}"
            )

        if counter.total:
            raise ValueError(
                f"Expected counter.total to be zero upon registration, got {counter.total}"
            )

        if counter.call_cnt:
            raise ValueError(
                f"Expected counter.call_cnt to be zero upon registration, got {counter.call_cnt}"
            )

        if counter.registered:
            raise ValueError(
                f"Expected counter.registered to be false upon registration, got {counter.registered}"
            )

        ident: bytes = counter.ident.value
        if ident in self._perf_counters:
            raise ValueError(f"counter with ident {ident} already exists")

        counter.registered = True
        self._perf_counters[ident] = counter

    def perf_start(self, counter: retro_perf_counter) -> None:
        assert counter.ident in self._perf_counters

        counter.call_cnt += 1
        counter.start = self.get_perf_counter()

    def perf_stop(self, counter: retro_perf_counter) -> None:
        assert counter.ident in self._perf_counters

        counter.total += self.get_perf_counter() - counter.start

    def perf_log(self) -> None:
        for counter in self._perf_counters.values():
            if counter.call_cnt:
                print(f"{counter.ident}: {counter.total / counter.call_cnt} ns")
            else:
                print(f"{counter.ident}: Not called")


__all__ = ["DefaultPerfDriver"]
