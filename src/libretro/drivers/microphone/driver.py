from abc import abstractmethod
from array import array
from collections.abc import Collection
from typing import Protocol, runtime_checkable

from libretro.api.microphone import retro_microphone, retro_microphone_params


@runtime_checkable
class Microphone(Protocol):
    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def params(self) -> retro_microphone_params | None: ...

    @abstractmethod
    def read(self, frames: int) -> array[int] | None: ...

    @property
    @abstractmethod
    def state(self) -> bool: ...

    @state.setter
    @abstractmethod
    def state(self, state: bool) -> None: ...

    def poll(self) -> None:
        pass


@runtime_checkable
class MicrophoneDriver(Protocol):
    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def open_mic(self, params: retro_microphone_params | None) -> retro_microphone | None: ...

    @abstractmethod
    def close_mic(self, mic: retro_microphone) -> None: ...

    @abstractmethod
    def get_mic_params(self, mic: retro_microphone) -> retro_microphone_params | None: ...

    @abstractmethod
    def get_mic_state(self, mic: retro_microphone) -> bool: ...

    @abstractmethod
    def set_mic_state(self, mic: retro_microphone, state: bool) -> None: ...

    @abstractmethod
    def read_mic(self, mic: retro_microphone, frames: int) -> array[int] | None: ...

    @property
    @abstractmethod
    def microphones(self) -> Collection[Microphone]: ...


__all__ = ["Microphone", "MicrophoneDriver"]
