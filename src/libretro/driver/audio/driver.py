from abc import abstractmethod
from ctypes import c_int16, POINTER
from typing import runtime_checkable, Protocol

from libretro.api import retro_audio_callback, retro_audio_buffer_status_callback, retro_system_av_info


@runtime_checkable
class AudioDriver(Protocol):
    @abstractmethod
    def sample(self, left: int, right: int) -> None: ...

    @abstractmethod
    def sample_batch(self, data: POINTER(c_int16), frames: int) -> int: ...

    # TODO: Use the callbacks in the session
    @abstractmethod
    def set_callbacks(self, callback: retro_audio_callback | None) -> bool: ...

    @abstractmethod
    def get_callbacks(self) -> retro_audio_callback | None: ...

    @property
    def callbacks(self) -> retro_audio_callback | None:
        return self.get_callbacks()

    @callbacks.setter
    def callbacks(self, callback: retro_audio_callback | None) -> None:
        self.set_callbacks(callback)

    @callbacks.deleter
    def callbacks(self) -> None:
        self.set_callbacks(None)

    @abstractmethod
    def get_status_callback(self) -> retro_audio_buffer_status_callback | None: ...

    @abstractmethod
    def set_status_callback(self, callback: retro_audio_buffer_status_callback | None) -> bool: ...

    @property
    def buffer_status(self) -> retro_audio_buffer_status_callback | None:
        return self.get_status_callback()

    @buffer_status.setter
    def buffer_status(self, callback: retro_audio_buffer_status_callback) -> None:
        self.set_status_callback(callback)

    @buffer_status.deleter
    def buffer_status(self) -> None:
        self.set_status_callback(None)

    def status(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        callback = self.buffer_status
        if callback:
            callback(active, occupancy, underrun_likely)

    @abstractmethod
    def get_minimum_latency(self) -> int | None: ...

    @abstractmethod
    def set_minimum_latency(self, latency: int | None) -> bool: ...

    @property
    def minimum_latency(self) -> int:
        return self.get_minimum_latency()

    @minimum_latency.setter
    def minimum_latency(self, latency: int | None) -> None:
        self.set_minimum_latency(latency)

    @minimum_latency.deleter
    def minimum_latency(self) -> None:
        self.get_minimum_latency()

    @abstractmethod
    def set_system_av_info(self, info: retro_system_av_info) -> None: ...


__all__ = [
    'AudioDriver',
]
