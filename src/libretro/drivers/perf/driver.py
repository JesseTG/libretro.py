"""
:class:`~typing.Protocol` definition for the performance counter interface.

.. seealso::

    :mod:`libretro.api.perf`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.perf import CpuFeatures, retro_perf_counter


@runtime_checkable
class PerfDriver(Protocol):
    """
    Protocol for drivers that expose the libretro performance-counter interface.

    .. seealso::

        :mod:`libretro.api.perf`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @abstractmethod
    def get_time_usec(self) -> int:
        """
        Return the current wall-clock time in microseconds.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_get_time_usec_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def get_cpu_features(self) -> CpuFeatures:
        """
        Return a bitmask of CPU features available to the core.

        .. seealso::

            :class:`~libretro.api.perf.CpuFeatures`
                Bit flags describing each supported CPU feature.
        """
        ...

    @abstractmethod
    def get_perf_counter(self) -> int:
        """
        Return the current value of the high-resolution performance counter.

        Units are driver-defined but consistent within a single process.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_get_counter_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def perf_register(self, counter: retro_perf_counter) -> None:
        """
        Register a new performance counter with the driver.

        :param counter: The counter struct to register.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_register_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def perf_start(self, counter: retro_perf_counter) -> None:
        """
        Start measuring a previously registered performance counter.

        :param counter: The counter to start.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_start_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def perf_stop(self, counter: retro_perf_counter) -> None:
        """
        Stop measuring a previously started performance counter.

        :param counter: The counter to stop.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_stop_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def perf_log(self) -> None:
        """
        Emit accumulated performance-counter measurements to the driver's log sink.

        .. seealso::

            :data:`~libretro.api.perf.retro_perf_log_t`
                The C function pointer type whose signature this method implements.
        """
        ...


__all__ = ["PerfDriver"]
