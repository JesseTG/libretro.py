from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.timing import retro_frame_time_callback, retro_fastforwarding_override, retro_throttle_state


@runtime_checkable
class TimingDriver(Protocol):

    @property
    @abstractmethod
    def frame_time_callback(self) -> retro_frame_time_callback | None: ...

    @frame_time_callback.setter
    @abstractmethod
    def frame_time_callback(self, value: retro_frame_time_callback | None) -> None: ...

    @frame_time_callback.deleter
    @abstractmethod
    def frame_time_callback(self) -> None: ...

    @property
    @abstractmethod
    def fastforwarding_override(self) -> retro_fastforwarding_override | None: ...

    @fastforwarding_override.setter
    @abstractmethod
    def fastforwarding_override(self, value: retro_fastforwarding_override | None) -> None: ...

    @property
    @abstractmethod
    def throttle_state(self) -> retro_throttle_state | None: ...

    @throttle_state.setter
    @abstractmethod
    def throttle_state(self, value: retro_throttle_state | None) -> None: ...

    @throttle_state.deleter
    @abstractmethod
    def throttle_state(self) -> None: ...

    @property
    @abstractmethod
    def target_refresh_rate(self) -> float | None: ...

    @target_refresh_rate.setter
    @abstractmethod
    def target_refresh_rate(self, value: float | None) -> None: ...

    @target_refresh_rate.deleter
    @abstractmethod
    def target_refresh_rate(self) -> None: ...


__all__ = ['TimingDriver']