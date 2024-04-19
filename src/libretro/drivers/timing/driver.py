from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.timing import (
    retro_fastforwarding_override,
    retro_frame_time_callback,
    retro_throttle_state,
)


@runtime_checkable
class TimingDriver(Protocol):
    @property
    @abstractmethod
    def frame_time_callback(self) -> retro_frame_time_callback | None: ...

    @frame_time_callback.setter
    @abstractmethod
    def frame_time_callback(self, value: retro_frame_time_callback) -> None: ...

    def frame_time(self, time: int | None) -> None:
        callback = self.frame_time_callback
        if callback:
            callback(time if time is not None else callback.reference)

    @property
    @abstractmethod
    def fastforwarding_override(self) -> retro_fastforwarding_override | None: ...

    @fastforwarding_override.setter
    @abstractmethod
    def fastforwarding_override(self, value: retro_fastforwarding_override) -> None: ...

    @property
    @abstractmethod
    def throttle_state(self) -> retro_throttle_state | None: ...

    @throttle_state.setter
    @abstractmethod
    def throttle_state(self, value: retro_throttle_state) -> None: ...

    @throttle_state.deleter
    @abstractmethod
    def throttle_state(self) -> None: ...

    @property
    @abstractmethod
    def target_refresh_rate(self) -> float | None: ...

    @target_refresh_rate.setter
    @abstractmethod
    def target_refresh_rate(self, value: float) -> None: ...

    @target_refresh_rate.deleter
    @abstractmethod
    def target_refresh_rate(self) -> None: ...


__all__ = ["TimingDriver"]
