from array import array
from copy import deepcopy

from libretro._typing import override
from libretro.api.audio import retro_audio_buffer_status_callback, retro_audio_callback
from libretro.api.av import retro_system_av_info
from libretro.error import UnsupportedEnvCall

from .driver import AudioDriver


class ArrayAudioDriver(AudioDriver):
    def __init__(self):
        self._buffer = array("h")
        self._system_av_info: retro_system_av_info | None = None

    def sample(self, left: int, right: int):
        self._buffer.append(left)
        self._buffer.append(right)

    def sample_batch(self, data: memoryview) -> int:
        self._buffer.frombytes(data.cast("B"))

        return len(data)

    @property
    @override
    def callbacks(self) -> retro_audio_callback | None:
        return None

    @callbacks.setter
    @override
    def callbacks(self, callback: retro_audio_callback | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting callbacks")

    @property
    @override
    def buffer_status(self) -> retro_audio_buffer_status_callback | None:
        return None

    @buffer_status.setter
    @override
    def buffer_status(self, callback: retro_audio_buffer_status_callback):
        raise UnsupportedEnvCall(
            "ArrayAudioDriver does not support setting buffer status callback"
        )

    @property
    @override
    def minimum_latency(self) -> int | None:
        return None

    @minimum_latency.setter
    @override
    def minimum_latency(self, latency: int | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting minimum latency")

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info)

    @system_av_info.setter
    @override
    def system_av_info(self, info: retro_system_av_info):
        if not isinstance(info, retro_system_av_info):
            raise TypeError(f"Expected retro_system_av_info; got {type(info).__name__}")

        self._system_av_info = deepcopy(info)

    @property
    def buffer(self) -> array:
        return self._buffer


__all__ = [
    "ArrayAudioDriver",
]
