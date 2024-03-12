from abc import abstractmethod
from ctypes import *
from array import array
from typing import Protocol, final, runtime_checkable

from .._utils import memoryview_at


@runtime_checkable
class AudioCallbacks(Protocol):
    @abstractmethod
    def audio_sample(self, left: c_int16, right: c_int16) -> None: ...

    @abstractmethod
    def audio_sample_batch(self, data: POINTER(c_int16), frames: c_size_t) -> c_size_t: ...


class AudioState(AudioCallbacks, Protocol):
    @property
    def buffer(self) -> array: ...


@final
class ArrayAudioState(AudioState):
    def __init__(self):
        self._buffer = array('h')

    def audio_sample(self, left: c_int16, right: c_int16):
        self._buffer.append(left)
        self._buffer.append(right)

    def audio_sample_batch(self, data: POINTER(c_int16), frames: c_size_t) -> c_size_t:
        sample_view = memoryview_at(data, frames * 2 * sizeof(c_int16))
        self._buffer.frombytes(sample_view)

        return frames

    @property
    def buffer(self) -> array:
        return self._buffer
