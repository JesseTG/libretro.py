from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api import (
    retro_audio_buffer_status_callback,
    retro_audio_callback,
    retro_system_av_info,
)


@runtime_checkable
class AudioDriver(Protocol):
    @abstractmethod
    def sample(self, left: int, right: int) -> None: ...

    @abstractmethod
    def sample_batch(self, frames: memoryview) -> int: ...

    @property
    @abstractmethod
    def callbacks(self) -> retro_audio_callback | None: ...

    @callbacks.setter
    @abstractmethod
    def callbacks(self, callback: retro_audio_callback | None) -> None: ...

    def set_state(self, enabled: bool) -> None:
        callbacks = self.callbacks
        if callbacks and callbacks.callback:
            callbacks.callback(enabled)

    def callback(self) -> None:
        callbacks = self.callbacks
        if callbacks and callbacks.callback:
            callbacks.callback()

    @property
    @abstractmethod
    def buffer_status(self) -> retro_audio_buffer_status_callback | None: ...

    @buffer_status.setter
    @abstractmethod
    def buffer_status(self, callback: retro_audio_buffer_status_callback) -> None: ...

    def report_buffer_status(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        callback = self.buffer_status
        if callback:
            callback(active, occupancy, underrun_likely)

    @property
    @abstractmethod
    def minimum_latency(self) -> int | None: ...

    @minimum_latency.setter
    @abstractmethod
    def minimum_latency(self, latency: int | None) -> None: ...

    @property
    @abstractmethod
    def system_av_info(self) -> retro_system_av_info | None: ...

    @system_av_info.setter
    @abstractmethod
    def system_av_info(self, info: retro_system_av_info) -> None: ...


__all__ = [
    "AudioDriver",
]
